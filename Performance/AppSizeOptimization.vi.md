[English](./AppSizeOptimization.md) | [Tiếng Việt](./AppSizeOptimization.vi.md)

[← Performance](./README.vi.md)

# App Size Optimization

## Ý chính

Kích thước app ảnh hưởng đến tỷ lệ cài đặt, giới hạn tải qua mạng di động, và ma sát khi update. Tối ưu diễn ra ở tầng asset, binary, và cơ chế phân phối — không chỉ đơn giản là "nén ảnh lại."

## Những điều cần nắm

- App thinning — App Store tạo và phục vụ cho mỗi thiết bị một variant chỉ chứa những gì thiết bị đó cần (ví dụ chỉ ảnh @3x cho iPhone @3x). Cơ chế chính là slicing dựa trên `Asset Catalog`; On-Demand Resources cũng là một phần của app thinning
- On-Demand Resources (ODR) — gắn tag để asset tải sau khi cài thay vì bundle sẵn trong bản tải ban đầu (ví dụ level game, asset của feature ít dùng). Tại WWDC25 Apple gọi ODR là công nghệ legacy sẽ bị deprecate và khuyên chuyển sang Background Assets (xem đáp án bên dưới)
- Asset catalog vs ảnh rời — ảnh trong catalog được slicing theo thiết bị và được Xcode nén/tối ưu khi build (có tuỳ chọn nén, gồm nén GPU/ASTC cho texture); ảnh rời trong bundle thì mọi thiết bị đều tải hết
- Dead code stripping — linker (`DEAD_CODE_STRIPPING`) chỉ loại bỏ function/data không được tham chiếu trong binary của bạn; nó không loại được method Obj-C (gọi động), localization, resource hay module SDK không dùng — những thứ này phải tự audit và xoá
- Static vs dynamic framework — mỗi dynamic framework là một binary Mach-O riêng: thêm chi phí load-time cho dyld, overhead cố định của file (header, chữ ký, căn trang), và không thể dead strip theo nhu cầu của app. (Từ Swift 5 với ABI stability, Swift runtime nằm sẵn trong iOS 12.2+ nên không còn bị copy theo app.) Static linking giảm launch time và cho phép dead strip, rất hợp với các module nội bộ nhỏ
- Audit dependency — một SDK nặng (analytics, ad network) có thể thêm hàng chục MB; cần biết cái gì thực sự đang dùng so với chỉ đang cài
- Đo size — App Thinning Size Report (tạo khi export archive từ Organizer với App Thinning "All compatible device variants") cho download size (nén) và install size (giải nén) của từng variant; mục file sizes của build trong App Store Connect cho số thật theo từng thiết bị. Để biết thành phần nào nặng, mở `.app` trong IPA đã thinning để xem kích thước executable, thư mục `Frameworks/`, `Assets.car` và các resource bundle, và bật build setting Write Link Map File để biết module/symbol nào chiếm chỗ trong executable

## Câu hỏi luyện tập

- Tại sao thêm một CocoaPod duy nhất có thể tăng cả binary size lẫn thời gian launch app?
- Khi nào bạn dùng On-Demand Resources thay vì bundle tất cả ngay từ đầu?

## Góc nhìn Senior

Kích thước app là chi phí xuyên suốt, không phải việc dọn dẹp một lần — mỗi dependency mới, mỗi localization không dùng, mỗi asset chưa nén đều cộng dồn. Câu trả lời ở tầm senior không phải "chạy size report một lần trước release," mà là có một size budget được track trong CI (fail build nếu binary size vượt ngưỡng), để phát hiện sự tăng trưởng theo từng PR thay vì phát hiện lúc submit.

## Đáp án câu hỏi luyện tập

### Tại sao thêm một CocoaPod duy nhất có thể tăng cả binary size lẫn thời gian launch app?

Vì một pod không chỉ thêm đúng phần code bạn gọi: nó kéo theo cả thư viện, các dependency bắc cầu, resource bundle, và nếu Podfile dùng `use_frameworks!` thì còn thêm một dynamic framework mà dyld phải load mỗi lần app khởi động.

Về binary size:

- Transitive dependency: một SDK quảng cáo hay analytics có thể kéo thêm nhiều pod khác (xem `Podfile.lock`).
- Linker flag `-ObjC` (CocoaPods thường thêm vào `OTHER_LDFLAGS`) buộc linker nạp mọi object file chứa class/category Obj-C trong static library, kể cả phần không dùng, nên dead stripping không loại bỏ được.
- Dynamic framework không thể bị dead strip theo nhu cầu của app: linker không biết app dùng symbol public nào, nên giữ lại tất cả.
- Resource bundle của SDK (ảnh, model, localization) được copy nguyên vào app.

Về launch time:

- Mỗi dynamic framework thêm việc cho dyld: map file, kiểm tra chữ ký, fix-up pointer, đăng ký class Obj-C.
- Nhiều SDK chạy code trong `+load`, static initializer, hoặc yêu cầu khởi tạo trong `didFinishLaunching` (swizzling, đọc config, gọi network).

Cách giảm: link static (`use_frameworks! :linkage => :static` hoặc bỏ `use_frameworks!`), chỉ dùng subspec cần thiết, khởi tạo SDK lazy sau frame đầu, và đo lại bằng App Thinning Size Report và template App Launch. (Ghi chú: CocoaPods đã chuyển sang chế độ bảo trì và dự án mới thường dùng Swift Package Manager, nhưng các nguyên tắc trên — dependency bắc cầu, static vs dynamic, `-ObjC`, resource bundle — áp dụng tương tự.) Trade-off: nếu cùng một module được link static vào cả app lẫn các extension, mỗi binary có một bản copy riêng; khi đó dynamic framework dùng chung hoặc mergeable libraries (Xcode 15+) hợp lý hơn.

### Khi nào bạn dùng On-Demand Resources thay vì bundle tất cả ngay từ đầu?

Dùng ODR khi asset lớn mà chỉ một phần người dùng cần, hoặc chỉ cần sau một thời điểm: level game phía sau, gói giọng nói/ngôn ngữ, video hướng dẫn, nội dung của tính năng ít dùng. Cách hoạt động: bạn gắn tag cho asset trong Xcode, App Store host chúng tách khỏi bản cài đặt chính, lúc runtime app xin tài nguyên bằng `NSBundleResourceRequest(tags:)` rồi `beginAccessingResources`. Tag có thể là Initial Install (tải cùng app), Prefetched (tải ngay sau khi cài), hoặc chỉ tải khi gọi. Khi thiết bị thiếu dung lượng, hệ thống có thể xoá các tài nguyên ODR không còn được dùng.

Không nên dùng khi:

- Asset cần ngay lần mở đầu hoặc phải dùng được offline (ví dụ người dùng mở app lần đầu trên máy bay).
- Asset nhỏ, lợi ích về size không đáng so với độ phức tạp.
- Nội dung cần cập nhật mà không phải release app: ODR gắn với từng build, muốn đổi phải submit bản mới — trường hợp này dùng CDN riêng.

Trade-off: bạn phải thiết kế trạng thái loading, lỗi và retry cho mọi màn hình dùng ODR. Ngoài ra, tại WWDC25 (session "Discover Apple-Hosted Background Assets") Apple gọi ODR là "legacy technology" sẽ bị deprecate và khuyên các app đang dùng ODR bắt đầu chuyển sang Background Assets; tại thời điểm đó Apple chưa công bố mốc thời gian gỡ bỏ cụ thể (hãy kiểm tra release notes của SDK mới nhất). Framework Background Assets đã có từ iOS 16 (khi đó bạn tự host asset), còn Apple-hosted asset packs — App Store host asset pack cho bạn, có thể cập nhật asset mà không cần phát hành bản app mới — là tính năng mới từ iOS 26. Với dự án mới, nên chọn Background Assets thay vì ODR.

## Bẫy phỏng vấn

### "File archive/IPA nặng 150MB, vậy người dùng phải tải 150MB?"

**Dễ trả lời sai:** Kích thước archive hoặc IPA universal chính là kích thước người dùng tải về.

**Nên trả lời:** Archive chứa mọi variant; người dùng nhận bản đã thinning cho đúng thiết bị và được nén. Phải phân biệt download size (bản nén, dùng để so với giới hạn tải qua mạng di động) và install size (dung lượng sau khi giải nén trên máy). Muốn số thật, export với App Thinning "All compatible device variants" để có App Thinning Size Report, hoặc xem mục file size của build trong App Store Connect.

### "Bật bitcode để App Store tối ưu size giúp mình?"

**Dễ trả lời sai:** Bitcode cho phép Apple recompile và làm app nhỏ hơn.

**Nên trả lời:** Đây là kiến thức lỗi thời: bitcode bị deprecate từ Xcode 14 và App Store không còn nhận bitcode cho iOS. Tối ưu size giờ nằm hoàn toàn ở phía bạn: bật Dead Code Stripping, strip symbol ở release, cân nhắc optimization level `-Osize` cho Swift (đổi lấy một chút tốc độ), loại bỏ asset và localization không dùng, audit dependency.

### "Chuyển hết framework sang static là app luôn nhỏ hơn?"

**Dễ trả lời sai:** Static linking luôn giảm cả launch time lẫn size, nên cứ static hết.

**Nên trả lời:** Static linking giảm việc cho dyld và cho phép dead strip, nhưng nếu một module được link vào app và nhiều extension (widget, notification service, share extension) thì mỗi binary chứa một bản copy riêng, tổng size có thể tăng. Khi đó một dynamic framework dùng chung sẽ nhỏ hơn. Mergeable libraries (Xcode 15+) là cách dung hoà: build dynamic khi debug để build nhanh, merge vào binary khi release.

## Bài tập

Install size của app bạn tăng từ 45MB lên 78MB sau hai chu kỳ release và marketing đang hỏi tại sao conversion giảm. Dùng App Thinning Size Report (hoặc file sizes của build trong App Store Connect) để so sánh hai bản, rồi chia phần tăng thêm theo nhóm executable, framework, resource bằng cách xem nội dung `.app` đã thinning và link map. Viết ra các bước điều tra bạn sẽ thực hiện để tìm 3 nguyên nhân lớn nhất, và đề xuất một cách fix cho mỗi category (ví dụ một dynamic framework có thể chuyển sang static link, một asset có thể chuyển sang tải sau bằng Background Assets (hoặc ODR với app cũ), một dependency có thể loại bỏ hoặc thay thế).
