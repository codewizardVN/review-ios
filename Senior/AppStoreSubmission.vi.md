[English](./AppStoreSubmission.md) | [Tiếng Việt](./AppStoreSubmission.vi.md)

[← Chủ đề cấp Senior](./README.vi.md)

# App Store Submission và Review

## Ý chính

Rejection từ App Review hiếm khi là vì một edge case tinh vi — gần như luôn là một tập nhỏ, có tài liệu rõ ràng, các vấn đề có thể đoán trước. Việc của một senior engineer là đảm bảo app không bao giờ đến review khi vẫn còn tồn tại một trong số đó.

## Những điều cần nắm

- Privacy manifest (`PrivacyInfo.xcprivacy`) — khai báo category thu thập dữ liệu và việc dùng API "required reason" (ví dụ `UserDefaults`, API dung lượng ổ đĩa, keyboard đang active) mà Apple bắt đầu enforce; thiếu entry gây rejection tự động, không chỉ là cờ để review thủ công
- "Nutrition label" Privacy trong App Store Connect — phải khớp với những gì app *thực sự* làm, không phải những gì nó làm ở lần submit trước; một SDK analytics mới hay ad network mới thay đổi cái này và là nguồn drift phổ biến
- Các nhóm lý do reject phổ biến — flow chính bị gãy trên tài khoản test của reviewer, metadata chưa hoàn chỉnh, nội dung placeholder, crash lúc mở app, sign-in yêu cầu mua hàng mà không có tài khoản demo, guideline 4.3 (app spam/template), guideline 5.1.1 (thu thập dữ liệu không nêu rõ mục đích)
- Yêu cầu tài khoản demo/test — App Review cần credential hoạt động cho bất kỳ flow bị khóa nào; một tài khoản demo hết hạn hoặc bật 2FA là nguyên nhân hàng đầu của reject "unable to test"
- Quy tắc metadata — screenshot phải phản ánh đúng app thật, không nhắc tới platform/đối thủ khác, không có text placeholder kiểu "Lorem ipsum", nhồi nhét keyword vào tên/subtitle
- Tuân thủ export mã hóa (`ITSAppUsesNonExemptEncryption`) — hầu hết app đủ điều kiện miễn trừ chuẩn (chỉ dùng HTTPS/TLS), nhưng khai sai cái này chặn đứng cả submission
- Phased release và staged rollout — release cho một phần trăm user trước, có khả năng dừng rollout nếu một metric bị regress, trước khi release toàn bộ
- Phản hồi khi bị reject — reply qua Resolution Center vs kháng cáo App Review Board; phân biệt việc reviewer hiểu sai guideline (đáng để kháng cáo kèm bằng chứng) với vi phạm policy thật sự (đáng để chỉ sửa)

## Ví dụ

Một submission bị reject theo mục 5.1.1 vì app request quyền location "always" nhưng chỉ dùng ở foreground. Cách fix không phải tranh luận về metadata — mà là đổi `NSLocationAlwaysAndWhenInUseUsageDescription` xuống `NSLocationWhenInUseUsageDescription` và bỏ capability không thực sự dùng, vì team review test dựa trên hành vi runtime thực tế, không phải ý định đã khai báo.

## Câu hỏi luyện tập

- Tại sao tài khoản demo bật 2FA gần như chắc chắn dẫn đến reject?
- Tại sao việc thiếu privacy manifest là reject tự động chứ không phải một quyết định phán đoán của con người?
- Khi nào nên kháng cáo một rejection thay vì chỉ sửa vấn đề bị gắn cờ?

## Góc nhìn Senior

Đây là một trong số ít mảng mà "sửa sau khi ship" không phải là lựa chọn — một build bị reject chặn cả release train, và một lần kháng cáo hỏng có thể tốn thêm nhiều ngày. Một senior engineer coi việc sẵn sàng cho App Review là một checklist trước-submit do team sở hữu (audit privacy manifest, kiểm tra tài khoản demo còn hiệu lực, độ chính xác của screenshot), chứ không phải điều bất ngờ phát hiện sau khi upload, và biết reject nào đáng kháng cáo có tài liệu so với reject nào nên fix và resubmit ngay trong ngày.

## Bài tập

Team bạn đang submit một version thêm SDK analytics bên thứ ba mới và một tier "premium" bị khóa sau paywall không có free trial. Liệt kê mọi mục ở App Store Connect và ở code bạn sẽ kiểm tra trước khi submit (privacy manifest, nutrition label, tài khoản demo, các vùng nguy cơ theo guideline) và mô tả hai lý do reject khả dĩ nhất cho thay đổi cụ thể này, kèm cách fix cho từng cái.
