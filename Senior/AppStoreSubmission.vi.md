[English](./AppStoreSubmission.md) | [Tiếng Việt](./AppStoreSubmission.vi.md)

[← Chủ đề cấp Senior](./README.vi.md)

# App Store Submission và Review

## Ý chính

Rejection từ App Review hiếm khi là vì một edge case tinh vi — gần như luôn là một tập nhỏ, có tài liệu rõ ràng, các vấn đề có thể đoán trước. Việc của một senior engineer là đảm bảo app không bao giờ đến review khi vẫn còn tồn tại một trong số đó.

## Những điều cần nắm

- Privacy manifest (`PrivacyInfo.xcprivacy`) — file plist trong bundle khai báo loại dữ liệu app thu thập, domain dùng cho tracking, và việc dùng API "required reason" (5 nhóm: file timestamp, system boot time, disk space, active keyboard, `UserDefaults`) kèm reason code được Apple chấp thuận. Từ 1/5/2024 Apple enforce phần required-reason: build dùng các API này mà thiếu khai báo bị App Store Connect từ chối ngay ở bước xử lý upload (email lỗi ITMS-91053), trước khi tới tay reviewer, chứ không phải chỉ là cờ để review thủ công
- "Nutrition label" Privacy trong App Store Connect — phải khớp với những gì app *thực sự* làm, không phải những gì nó làm ở lần submit trước; một SDK analytics mới hay ad network mới thay đổi cái này và là nguồn drift phổ biến
- Các nhóm lý do reject phổ biến — guideline 2.1 (App Completeness: crash lúc mở app, flow chính bị gãy trên tài khoản test của reviewer, nội dung placeholder, app bắt đăng nhập mà không cung cấp tài khoản demo), 2.3 (metadata sai hoặc chưa hoàn chỉnh), 3.1.1 (mở khóa nội dung/tính năng digital mà không dùng In-App Purchase), 4.3 (app spam/template), 5.1.1 (thu thập dữ liệu hoặc xin quyền mà không nêu rõ mục đích, hoặc thu nhiều hơn mức cần)
- Yêu cầu tài khoản demo/test — App Review cần credential hoạt động cho bất kỳ flow bị khóa nào; một tài khoản demo hết hạn hoặc bật 2FA là nguyên nhân hàng đầu của reject "unable to test"
- Quy tắc metadata — screenshot phải phản ánh đúng app thật đang chạy, không nhắc tới tên hay icon của platform/đối thủ khác, không có text placeholder kiểu "Lorem ipsum", và không nhồi nhét keyword hay tên thương hiệu khác vào tên/subtitle
- Tuân thủ export mã hóa (`ITSAppUsesNonExemptEncryption` trong Info.plist) — app chỉ dùng mã hóa có sẵn của hệ điều hành (HTTPS/TLS qua `URLSession`, Keychain…) thường thuộc diện miễn trừ, khai `NO`. Nếu không khai key này, App Store Connect sẽ hỏi câu export compliance cho mỗi build và build nằm ở trạng thái "Missing Compliance", chưa dùng được cho TestFlight hay submit cho tới khi trả lời. Khai sai (nói miễn trừ trong khi app dùng mã hóa tự viết/không miễn trừ) là rủi ro pháp lý về luật xuất khẩu, không chỉ là chuyện review
- Phased release — App Store phát hành bản update dần trong 7 ngày (1%, 2%, 5%, 10%, 20%, 50%, 100%) cho các user bật tự động cập nhật; có thể tạm dừng (tổng cộng tối đa 30 ngày) nếu crash rate hay một metric bị regress, hoặc release cho tất cả ngay. Lưu ý: user vẫn có thể tự tải bản mới từ App Store trong lúc phased release, và pause không rút được bản đã phát hành — muốn chặn hẳn phải có kill switch trong app hoặc ship bản sửa
- Phản hồi khi bị reject — reply cho reviewer trong App Store Connect (Resolution Center) vs gửi appeal lên App Review Board; phân biệt việc reviewer hiểu sai guideline (đáng để kháng cáo kèm bằng chứng) với vi phạm policy thật sự (đáng để chỉ sửa)

## Ví dụ

Một submission bị reject theo mục 5.1.1 vì app request quyền location "always" nhưng chỉ dùng ở foreground. Cách fix không phải tranh luận về metadata — mà là chỉ xin đúng quyền cần: trong code gọi `requestWhenInUseAuthorization()` thay cho `requestAlwaysAuthorization()`, xóa key `NSLocationAlwaysAndWhenInUseUsageDescription` khỏi Info.plist (chỉ giữ `NSLocationWhenInUseUsageDescription` với câu giải thích cụ thể), và bỏ background mode `location` nếu không thực sự dùng. Lý do là reviewer đánh giá theo hành vi runtime thực tế (app xin quyền gì, dùng vào lúc nào), không phải ý định đã khai báo.

## Câu hỏi luyện tập

- Tại sao tài khoản demo bật 2FA gần như chắc chắn dẫn đến reject?
- Tại sao việc thiếu privacy manifest là reject tự động chứ không phải một quyết định phán đoán của con người?
- Khi nào nên kháng cáo một rejection thay vì chỉ sửa vấn đề bị gắn cờ?

## Góc nhìn Senior

Đây là một trong số ít mảng mà "sửa sau khi ship" không phải là lựa chọn — một build bị reject chặn cả release train, và một lần kháng cáo hỏng có thể tốn thêm nhiều ngày. Một senior engineer coi việc sẵn sàng cho App Review là một checklist trước-submit do team sở hữu (audit privacy manifest, kiểm tra tài khoản demo còn hiệu lực, độ chính xác của screenshot), chứ không phải điều bất ngờ phát hiện sau khi upload, và biết reject nào đáng kháng cáo có tài liệu so với reject nào nên fix và resubmit ngay trong ngày.

## Đáp án câu hỏi luyện tập

### Tại sao tài khoản demo bật 2FA gần như chắc chắn dẫn đến reject?

Vì reviewer không thể nhận được mã xác thực gửi tới điện thoại hay email của bạn, nên họ kẹt ở màn hình login và reject với lý do "không thể review app" (thường là guideline 2.1 – App Completeness).

Reviewer làm việc bất đồng bộ, ở múi giờ khác, trên thiết bị của Apple. Mã OTP gửi qua SMS tới số của một người trong team, hoặc tới email không ai đọc lúc 3 giờ sáng, coi như không tồn tại. Họ sẽ không nhắn tin chờ bạn gửi mã; họ ghi nhận là không vào được flow chính và trả build về. Mỗi vòng như vậy tốn thêm một hoặc vài ngày.

Cách xử lý thực tế:

- Tạo một tài khoản demo riêng cho App Review, tắt 2FA hoặc cấu hình backend để tài khoản đó dùng một mã cố định đã ghi trong App Review Information.
- Kiểm tra tài khoản còn hoạt động ngay trước khi submit: chưa hết hạn, chưa bị khóa vì đăng nhập sai, có sẵn dữ liệu mẫu để thấy được feature.
- Nếu flow cần phần cứng hoặc vị trí đặc biệt, bật demo mode hoặc gửi video demo kèm notes.

Trade-off: một tài khoản bỏ qua 2FA là một lỗ hổng tiềm năng. Giới hạn quyền của nó (chỉ dữ liệu giả, không truy cập admin), theo dõi đăng nhập, và xoay vòng mật khẩu sau mỗi release.

### Tại sao việc thiếu privacy manifest là reject tự động chứ không phải một quyết định phán đoán của con người?

Vì việc dùng required-reason API có thể phát hiện bằng máy: khi bạn upload build, Apple quét binary để tìm symbol của các API đó và so với `PrivacyInfo.xcprivacy`, không cần người xem.

Từ 1/5/2024, App Store Connect từ chối nhận app mới hoặc bản update có dùng required-reason API mà không khai báo lý do được chấp thuận (lỗi ITMS-91053 "Missing API declaration"). Các nhóm API gồm: file timestamp, system boot time, disk space, active keyboard, và `UserDefaults`. Việc kiểm tra là so khớp đơn giản: binary có tham chiếu `UserDefaults` không, manifest có entry `NSPrivacyAccessedAPICategoryUserDefaults` với reason code hợp lệ (ví dụ `CA92.1`) không. Có hay không, không cần diễn giải, nên nó được tự động hóa ở bước xử lý build — bạn nhận email báo lỗi trước khi build tới tay reviewer.

Ngoài ra, các SDK bên thứ ba nằm trong danh sách "commonly used SDKs" của Apple (ví dụ Firebase, Alamofire, SDWebImage) phải kèm privacy manifest riêng, và nếu được nhúng dưới dạng binary (XCFramework) thì còn phải có chữ ký của nhà phát triển SDK; thiếu thì App Store Connect cũng có thể chặn tương tự. Cách xử lý thường chỉ là nâng SDK lên version đã kèm manifest.

Điểm cần phân biệt: phần khai báo data collection (`NSPrivacyCollectedDataTypes`) và tracking domain thì máy khó kiểm chứng hơn, nên độ chính xác của chúng vẫn chủ yếu dựa vào trách nhiệm của bạn và vào review. Vì vậy manifest "pass upload" không có nghĩa là privacy của app đã đúng.

### Khi nào nên kháng cáo một rejection thay vì chỉ sửa vấn đề bị gắn cờ?

Kháng cáo khi bạn có bằng chứng reviewer hiểu sai app hoặc áp sai guideline; còn nếu app thật sự vi phạm, sửa và resubmit nhanh hơn nhiều.

Trước tiên luôn đọc kỹ guideline được trích và tái hiện đúng điều reviewer thấy. Có ba tình huống:

- Reviewer thiếu thông tin (không tìm thấy feature, không hiểu vì sao cần quyền): trả lời trong App Store Connect, giải thích rõ, kèm screenshot hoặc video, thường không cần kháng cáo.
- Reviewer áp sai guideline (ví dụ coi nội dung vật lý là digital content phải dùng IAP): gửi appeal lên App Review Board kèm lập luận theo đúng câu chữ guideline và bằng chứng.
- Vi phạm thật (thiếu nút xóa tài khoản, xin quyền không dùng): sửa và resubmit ngay trong ngày.

Một điểm hay bị quên: từ 2020, Apple cho biết bản sửa bug của app đã có trên store sẽ không bị giữ lại vì vi phạm guideline, trừ vấn đề pháp lý; bạn có thể xin ship bản fix trước và giải quyết vi phạm ở lần submit sau.

Trade-off: appeal có thể mất vài ngày và không đảm bảo thắng. Nếu release đang gấp và cách sửa rẻ, sửa trước rồi tranh luận sau.

## Bẫy phỏng vấn

### "Đã có privacy manifest rồi thì nutrition label cập nhật tự động đúng không?"

**Dễ trả lời sai:** Đúng, App Store Connect đọc `PrivacyInfo.xcprivacy` và điền App Privacy label thay mình.

**Nên trả lời:** Hai thứ này tách biệt. Manifest nằm trong bundle, khai báo cho binary; nutrition label vẫn phải điền thủ công trong App Store Connect. Xcode có thể tạo Privacy Report gộp manifest của app và các SDK để bạn dùng làm tài liệu tham khảo khi điền label, nhưng nếu hai bên mâu thuẫn thì đó là việc của team phải sửa. Mỗi lần thêm SDK mới, cần review lại cả hai.

### "App không thu thập dữ liệu gì, vậy có cần privacy manifest không?"

**Dễ trả lời sai:** Không cần, privacy manifest chỉ dành cho app có tracking hoặc analytics.

**Nên trả lời:** Required-reason API không liên quan đến việc thu thập dữ liệu. Gần như mọi app đều dùng `UserDefaults`, và nhiều app đọc file timestamp hoặc dung lượng ổ đĩa, nên đều cần khai báo lý do. Thêm vào đó, SDK bên thứ ba có thể dùng các API này ngay cả khi code của bạn không dùng. Cách an toàn là có manifest ở target app, và kiểm tra từng SDK đã kèm manifest của riêng nó.

### "App có đăng ký tài khoản, user muốn xóa thì bảo họ email cho support được không?"

**Dễ trả lời sai:** Được, chỉ cần có một cách để user yêu cầu xóa, ví dụ gửi email hoặc điền form trên web.

**Nên trả lời:** Theo guideline 5.1.1(v), app cho phép tạo tài khoản phải cho phép bắt đầu việc xóa tài khoản ngay trong app. Chỉ vô hiệu hóa tài khoản hoặc bắt user gửi email là không đủ; nếu app ở ngành bị quản lý chặt cần thêm bước xác minh, có thể dẫn qua quy trình đó nhưng điểm khởi đầu vẫn phải nằm trong app. Nếu dùng Sign in with Apple, nên revoke token qua REST API của Apple khi xóa tài khoản.

## Bài tập

Team bạn đang submit một version thêm SDK analytics bên thứ ba mới và một tier "premium" bị khóa sau paywall không có free trial. Liệt kê mọi mục ở App Store Connect và ở code bạn sẽ kiểm tra trước khi submit (privacy manifest, nutrition label, tài khoản demo, các vùng nguy cơ theo guideline) và mô tả hai lý do reject khả dĩ nhất cho thay đổi cụ thể này, kèm cách fix cho từng cái.
