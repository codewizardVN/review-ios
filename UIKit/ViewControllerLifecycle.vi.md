[English](./ViewControllerLifecycle.md) | [Tiếng Việt](./ViewControllerLifecycle.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# View Controller Lifecycle

## Ý chính

Mỗi lifecycle method có vai trò khác nhau. Bug thường xuất hiện khi networking, layout work, analytics, hoặc binding logic được đặt sai thời điểm.

## Cần ôn

- `viewDidLoad` cho setup một lần: chạy đúng một lần sau khi view được load vào bộ nhớ, trước khi view được gắn vào window. Hợp cho việc tạo subview, constraint, data source, binding.
- `viewWillAppear` cho state cần refresh trước khi hiển thị: chạy mỗi lần màn hình sắp hiện (kể cả khi quay lại sau khi pop màn hình phía trên), trước animation chuyển màn hình.
- `viewIsAppearing` (iOS 17, back-deploy tới iOS 13): chạy sau `viewWillAppear`, lúc view đã nằm trong hierarchy và có trait collection, kích thước đúng, nhưng vẫn trước animation. Là chỗ tốt cho cập nhật UI phụ thuộc size hoặc trait.
- `viewDidAppear` cho tracking hoặc công việc cần view đã xuất hiện: chạy sau khi transition hoàn tất, view đã thật sự trên màn hình.
- `viewWillDisappear`/`viewDidDisappear` và thời điểm cleanup: dừng timer, pause video, hủy subscription gắn với việc màn hình đang hiện. Lưu ý màn hình biến mất không có nghĩa view controller bị giải phóng (nó có thể chỉ bị push đè lên), nên cleanup "vĩnh viễn" vẫn thuộc về `deinit`.
- `viewWillLayoutSubviews`/`viewDidLayoutSubviews`: có thể chạy nhiều lần (xoay màn hình, đổi size, thay đổi layout), nên code trong đó phải nhẹ và chạy lặp lại không gây hại.

## Câu hỏi thực hành

- `viewWillAppear` khác `viewDidAppear` ở điểm nào?
- Công việc nào không nên đặt trong `viewDidLoad`?

## Câu hỏi luyện tập

- Sự khác biệt giữa viewWillAppear và viewDidAppear là gì?
- Công việc nào không bao giờ nên xảy ra trong viewDidLoad?

## Góc nhìn senior

Lifecycle thực chất là chuyện ownership và timing. Câu trả lời tốt cần giải thích vì sao một việc thuộc về phase đó, thay vì chỉ thuộc callback theo kiểu học thuộc.

## Đáp án câu hỏi luyện tập

### Sự khác biệt giữa viewWillAppear và viewDidAppear là gì?

`viewWillAppear` chạy trước khi view hiện lên, trước khi transition bắt đầu. `viewDidAppear` chạy sau khi transition đã xong và view đã thật sự nằm trên màn hình. Vì vậy mỗi callback hợp với một loại việc khác nhau:

- `viewWillAppear`: cập nhật những gì user phải thấy ngay khi màn hình trượt vào, như title, trạng thái nút, dữ liệu có thể đã đổi khi user ở màn hình khác. Nếu cập nhật muộn hơn, user sẽ thấy UI cũ rồi nhảy sang UI mới.
- `viewDidAppear`: việc cần view đã hiện hẳn, như gửi analytics "screen viewed", bắt đầu animation, `becomeFirstResponder` để bật bàn phím, present một alert hoặc onboarding tooltip.

Có hai chi tiết hay bị hỏi thêm. Thứ nhất, `viewWillAppear` có thể chạy mà không có `viewDidAppear` theo sau, ví dụ user vuốt back một nửa rồi thả ra (interactive pop bị hủy). Thứ hai, trong `viewWillAppear` view có thể chưa có trait collection và kích thước cuối cùng. iOS 17 thêm `viewIsAppearing(_:)` (back-deploy tới iOS 13). Method này chạy sau khi view đã được gắn vào hierarchy và có geometry đúng, nhưng vẫn trước animation. Đó là chỗ tốt hơn cho việc cập nhật UI phụ thuộc vào size hoặc trait.

Trade-off: không nên làm việc nặng đồng bộ trong cả hai method, vì chúng chạy trên main thread ngay trong transition và sẽ làm animation giật.

### Công việc nào không bao giờ nên xảy ra trong viewDidLoad?

Không nên đặt vào `viewDidLoad` bất cứ thứ gì phụ thuộc vào kích thước cuối cùng của view, cần chạy lại mỗi lần màn hình xuất hiện, hoặc cần view đã nằm trên màn hình. `viewDidLoad` chỉ chạy một lần, ngay sau khi view được load vào bộ nhớ. Lúc đó view chưa được gắn vào window, và `view.bounds` thường vẫn là kích thước từ storyboard hoặc giá trị mặc định.

Cụ thể nên tránh:

- Tính frame thủ công dựa trên `view.bounds`. Kết quả sẽ sai trên thiết bị khác, khi xoay màn hình hoặc trên iPad split view. Hãy dùng constraint, hoặc tính trong `viewDidLayoutSubviews`.
- Present alert hoặc view controller khác. UIKit sẽ báo warning kiểu "view is not in the window hierarchy" và không hiện gì.
- Gửi analytics "screen viewed". View có thể được load mà chưa từng hiện ra, và chỉ chạy một lần dù user quay lại màn hình nhiều lần.
- Công việc nặng chạy đồng bộ như decode file lớn hoặc query database. Nó chặn transition push nên user thấy app đơ.

Còn setup một lần như tạo subview, add constraint, cấu hình data source, bind ViewModel và bắt đầu load dữ liệu bất đồng bộ thì rất hợp với `viewDidLoad`.

## Bẫy phỏng vấn

### "Sau khi dismiss một sheet, viewWillAppear của màn hình bên dưới có chạy không?"

**Dễ trả lời sai:** Có. Mỗi lần màn hình hiện lại, `viewWillAppear` luôn được gọi, nên cứ reload dữ liệu ở đó.

**Nên trả lời:** Từ iOS 13, kiểu present mặc định là `.pageSheet`. Màn hình bên dưới vẫn nằm trong hierarchy nên nó không nhận `viewWillDisappear`/`viewWillAppear` khi sheet mở và đóng. Chỉ những kiểu present gỡ view bên dưới ra khỏi hierarchy, như `.fullScreen` hoặc `.currentContext`, mới gọi các callback appearance. `.overFullScreen` cũng giữ view bên dưới nên không gọi. Muốn biết sheet đã đóng, hãy dùng delegate hoặc closure từ màn hình con, hoặc `UIAdaptivePresentationControllerDelegate.presentationControllerDidDismiss(_:)` cho trường hợp user vuốt xuống.

### "viewWillAppear luôn được theo sau bởi viewDidAppear, đúng không?"

**Dễ trả lời sai:** Đúng, hai callback luôn đi thành cặp, nên có thể start việc gì đó ở `viewWillAppear` và chắc chắn nó sẽ "hoàn tất" ở `viewDidAppear`.

**Nên trả lời:** Khi user vuốt back một nửa rồi hủy, màn hình bên dưới nhận `viewWillAppear` rồi `viewWillDisappear` và `viewDidDisappear`, không hề có `viewDidAppear`. Nếu bạn bật một thứ ở `viewWillAppear` và trông chờ `viewDidAppear` để tắt hoặc "hoàn tất" nó (ví dụ hiện loading overlay ở `viewWillAppear`, ẩn ở `viewDidAppear`), khi pop bị hủy nó sẽ bị kẹt. Hãy ghép cặp start/stop đối xứng: `viewWillAppear` với `viewWillDisappear`, `viewDidAppear` với `viewDidDisappear`. Code stop cũng nên an toàn khi gọi mà chưa từng start (idempotent), vì trong ca hủy pop ở trên `viewDidDisappear` được gọi dù không có `viewDidAppear`. Ngoài ra, cập nhật phụ thuộc vào geometry nên đặt ở `viewIsAppearing`.

### "Observer của NotificationCenter được dọn trong deinit, vậy là an toàn?"

**Dễ trả lời sai:** Chỉ cần gọi `removeObserver` trong `deinit` là xong, không sợ leak.

**Nên trả lời:** Với API dựa trên block `addObserver(forName:object:queue:using:)`, NotificationCenter giữ closure, và nếu closure capture `self` mạnh thì view controller không bao giờ bị giải phóng, nên `deinit` không bao giờ chạy. Phải dùng `[weak self]` và giữ token để remove. Observer dạng selector thì từ iOS 9 tự động được bỏ khi object bị giải phóng. Cách gọn nhất hiện nay là dùng `for await` trên `NotificationCenter.default.notifications(named:)` trong một `Task` rồi cancel Task đó khi màn hình biến mất.

## Bài tập

Review một controller đang gọi API trong `viewDidAppear`, set constraints trong `viewWillAppear`, và subscribe notification trong `viewDidLoad` mà không cleanup. Hãy chuyển từng trách nhiệm sang vị trí phù hợp hơn và giải thích lý do.
