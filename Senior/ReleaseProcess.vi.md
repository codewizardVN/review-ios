[English](./ReleaseProcess.md) | [Tiếng Việt](./ReleaseProcess.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Release Process

## Senior nên nói tới gì

- kiểm soát scope và tiêu chí release
- feature flag và kill switch
- QA, smoke test, và monitoring
- rollback hoặc mitigation plan

## Luồng điển hình

1. Chốt scope cho release candidate.
2. Chạy regression có trọng tâm ở các vùng rủi ro cao.
3. Xác nhận analytics, logging, và crash reporting đã sẵn sàng.
4. Rollout dần nếu có thể.
5. Theo dõi crash, funnel quan trọng, và tình trạng backend.

## Câu hỏi thực hành

- Điều gì khiến bạn chặn một release?
- Làm sao giảm release risk khi deadline đã cố định?

## Câu hỏi luyện tập

- Điều gì khiến bạn chặn một release lại?
- Bạn giảm rủi ro release ra sao khi deadline đã cố định?

## Góc nhìn senior

Release là một kỷ luật vận hành, không chỉ là bấm nút trên App Store Connect. Câu trả lời tốt nhất cân bằng tốc độ delivery với các guardrail đủ mạnh để team phục hồi nhanh khi có sự cố.

## Đáp án câu hỏi luyện tập

### Điều gì khiến bạn chặn một release lại?

Tôi chặn release khi có vấn đề gây hại cho người dùng hoặc doanh nghiệp mà không thể giảm thiểu sau khi ship; vấn đề nhỏ có workaround thì ghi thành known issue và vẫn ship. Stop-ship criteria nên được thống nhất trước với product và QA, không quyết theo cảm tính vào phút cuối.

Các tiêu chí tôi thường dùng:

- Crash hoặc hang ở luồng chính (launch, login, checkout), hoặc crash-free rate của release candidate thấp hơn ngưỡng so với bản trước.
- Mất hoặc hỏng dữ liệu người dùng, migration fail.
- Lỗi liên quan tới tiền: sai giá, trừ tiền hai lần, không khôi phục được giao dịch mua.
- Vấn đề security hoặc privacy: lộ token trong log, thu thập dữ liệu chưa khai báo trong privacy manifest hay privacy label.
- Feature rủi ro nhưng không có feature flag hoặc kill switch để tắt.
- Thiếu thứ cần để vận hành: dSYM chưa upload, analytics cho funnel quan trọng không hoạt động.

Những thứ không đáng chặn: lỗi UI nhỏ, lỗi trong feature đang tắt bằng flag, bug đã có từ version trước và không tệ hơn.

Khi chặn, tôi nói rõ với product: vấn đề gì, ảnh hưởng bao nhiêu người dùng, và các lựa chọn (fix và trễ X ngày, hoặc tắt feature và ship đúng hạn). Trade-off: chặn quá dễ khiến team mất nhịp, release sau dồn lớn hơn và rủi ro hơn; vì vậy quyết định phải dựa vào mức độ nghiêm trọng và khả năng khắc phục sau khi ship.

### Bạn giảm rủi ro release ra sao khi deadline đã cố định?

Khi deadline không đổi được, tôi giảm rủi ro bằng cách cắt scope và tăng khả năng tắt hoặc khắc phục, chứ không phải bằng làm thêm giờ và bỏ bớt test.

Cụ thể:

- **Chốt scope sớm:** phần quan trọng nhất cho deadline làm trước; phần chưa sẵn sàng thì đẩy ra sau flag hoặc sang release sau.
- **Feature flag có remote kill switch:** code được ship nhưng chỉ bật khi đã kiểm tra xong, và tắt được mà không cần build mới.
- **Code freeze và release branch sớm vài ngày:** chỉ nhận fix đã được phê duyệt.
- **TestFlight sớm** cho internal tester và nhóm beta; regression tập trung vào vùng bị thay đổi và luồng doanh thu.
- **Nộp App Review sớm** để có buffer, chọn phát hành thủ công để release đúng ngày mong muốn.
- **Phased release** trên App Store, theo dõi crash và funnel, pause nếu có dấu hiệu xấu.
- **Chuẩn bị sẵn kế hoạch hotfix** và người trực trong những ngày đầu.

Trade-off: cắt scope cần product đồng ý. Tôi trình bày dưới dạng lựa chọn rõ ràng: ship đủ scope với rủi ro X, hoặc ship phần lõi đúng hạn và phần còn lại sau một tuần. Làm thêm giờ dồn dập ở cuối thường tạo thêm bug chứ không làm giảm rủi ro.

## Bẫy phỏng vấn

### "Bản mới lỗi nặng sau khi lên App Store. Bạn rollback thế nào?"

**Dễ trả lời sai:** "Rollback về build trước trên App Store Connect." App Store không có chức năng rollback cho người dùng đã cập nhật.

**Nên trả lời:** Người dùng đã cài bản lỗi sẽ giữ nó cho đến khi có bản mới. Công cụ thật sự là: tắt feature bằng kill switch hoặc remote config, sửa phía server nếu có thể, pause phased release để giảm số người nhận auto-update, và ship hotfix với build number mới, có thể xin expedited review. Lưu ý: version đã phát hành (ví dụ 2.3.0) không nhận thêm build, nên hotfix phải là một version mới trên App Store Connect (ví dụ 2.3.1) kèm build number mới. Nếu bản lỗi đang trong phased release thì pause ngay, rồi để bản hotfix thay thế. Vì không rollback được, feature flag và kế hoạch hotfix phải có từ trước khi release, không phải nghĩ ra lúc sự cố.

### "Phased release đảm bảo chỉ 1% người dùng có bản mới ngày đầu?"

**Dễ trả lời sai:** "Đúng, phased release giới hạn chính xác số người nhận bản mới." Đây là hiểu sai phổ biến.

**Nên trả lời:** Phased release chỉ áp dụng cho người dùng đã bật automatic update: Apple đẩy bản mới cho một nhóm người dùng được chọn ngẫu nhiên, với tỷ lệ tăng dần theo ngày 1%, 2%, 5%, 10%, 20%, 50%, 100% trong 7 ngày, và có thể pause (tổng thời gian pause tối đa 30 ngày) hoặc bấm phát hành cho tất cả bất cứ lúc nào. Bất kỳ ai cũng có thể update thủ công hoặc tải mới app từ App Store và nhận ngay bản mới. Vì vậy phased release giảm tốc độ lan, nhưng muốn kiểm soát thật sự ai thấy feature mới thì phải dùng feature flag phía server.

### "Build đã qua TestFlight thì lên App Store khỏi review, phải không?"

**Dễ trả lời sai:** "Đúng, đã review rồi." Hoặc ngược lại: "Mọi build TestFlight đều phải chờ review."

**Nên trả lời:** Internal tester (thành viên của team trên App Store Connect) nhận build mà không cần review. External tester cần qua TestFlight App Review, thường là với build đầu tiên của một version; các build sau có thể không cần review đầy đủ. Submit lên App Store là một lần App Review riêng, với tiêu chí đầy đủ hơn. Ngoài ra build TestFlight hết hạn sau 90 ngày — đây là chi tiết interviewer hay hỏi khi bàn về beta dài hạn.

## Bài tập

Team buộc phải ship một update cho payments trước chiến dịch marketing. Hãy lập một release checklist gồm pre-release checks, rollout strategy, monitoring signal, và stop-ship criteria.
