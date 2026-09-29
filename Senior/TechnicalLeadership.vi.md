[English](./TechnicalLeadership.md) | [Tiếng Việt](./TechnicalLeadership.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Technical Leadership

## Biểu hiện

- Định hướng kỹ thuật và làm nó hiển thị với team
- Nêu rủi ro sớm — không chỉ thực thi task
- Gỡ chặn người khác thay vì tự làm hết
- Mentor qua câu hỏi, không chỉ câu trả lời
- Viết RFC hoặc design doc khi quyết định có tác động dài hạn

## Mentoring Engineer Junior và Mid-Level

- Hỏi họ đã thử gì trước khi đưa ra câu trả lời
- Review PR của họ với giải thích, không chỉ approve/reject
- Pair program trên vấn đề khó để họ học quy trình
- Để họ dẫn dắt tính năng nhỏ với sự hỗ trợ của bạn

## Ra quyết định kỹ thuật dưới áp lực

- Nêu rõ trade-off — "chúng ta có thể ship nhanh hơn với X nhưng sẽ trả giá Y sau"
- Ghi lại quyết định và lý do — decision log giúp engineer tương lai
- Tránh đề xuất giải pháp trước khi hiểu — hỏi câu hỏi làm rõ trước

## Câu hỏi thực hành

- Nếu team muốn ship nhanh nhưng chất lượng code kém, bạn làm gì?
- Nếu có bất đồng về kiến trúc, bạn xử lý như thế nào?
- Bạn cân bằng technical debt và product delivery như thế nào?

## Câu hỏi luyện tập

- Nếu team muốn ship nhanh nhưng chất lượng code kém, bạn làm gì?
- Nếu có bất đồng về architecture, bạn xử lý thế nào?
- Bạn cân bằng giữa technical debt và tiến độ sản phẩm ra sao?

## Góc nhìn senior

Technical leadership không phải là trở thành lập trình viên giỏi nhất trong team. Đó là nâng cao năng lực của cả team, ra quyết định tốt trong điều kiện không chắc chắn, và giao tiếp rõ ràng với cả engineer lẫn stakeholder.

## Đáp án câu hỏi luyện tập

### Nếu team muốn ship nhanh nhưng chất lượng code kém, bạn làm gì?

Tôi không chọn phe giữa tốc độ và chất lượng; tôi làm rõ chất lượng kém đang gây thiệt hại cụ thể gì, rồi thêm những guardrail rẻ nhất để team vẫn ship nhanh mà không tích tụ rủi ro.

Cấu trúc trả lời (tình huống → hành động → kết quả):

- **Tình huống:** team ship mỗi tuần, nhưng release nào cũng kèm 2–3 hotfix và crash-free rate đang giảm.
- **Hành động:**
  1. Lấy dữ liệu — số hotfix, bug lặp lại, thời gian làm lại — để nói chuyện bằng con số thay vì cảm giác "code xấu".
  2. Thêm guardrail tự động và rẻ: SwiftLint trên CI, unit test bắt buộc cho logic tiền và đăng nhập, PR template có checklist ngắn.
  3. Thống nhất với team một "definition of done" tối thiểu.
  4. Nói chuyện với PM bằng ngôn ngữ chi phí: mỗi hotfix tốn bao nhiêu ngày của team.
  5. Tự làm gương — PR nhỏ, có test, review nhanh — để quy trình mới không làm chậm ai.
- **Kết quả:** sau vài sprint số hotfix giảm, còn tốc độ không giảm vì ít phải làm lại.

Quan trọng là không đổ lỗi cho cá nhân; chất lượng kém thường đến từ áp lực deadline hoặc thiếu quy trình, không phải do người lười.

Trade-off: có lúc ship nhanh với code chưa đẹp là quyết định đúng — prototype, thử nghiệm A/B, tính năng có thể bị bỏ. Khi đó ghi rõ phần nợ và kế hoạch dọn, thay vì cấm hoàn toàn.

### Nếu có bất đồng về architecture, bạn xử lý thế nào?

Tôi chuyển bất đồng từ "ý kiến của ai" sang "tiêu chí nào quan trọng với chúng ta", rồi ra quyết định có thời hạn và ghi lại.

Cấu trúc:

1. **Hiểu từng phương án:** mời mỗi bên trình bày vấn đề họ muốn giải quyết, không chỉ giải pháp. Nhiều bất đồng thực ra là hai bên tối ưu cho hai mục tiêu khác nhau.
2. **Thống nhất tiêu chí trước:** testability, thời gian onboarding, build time, rủi ro migration, deadline.
3. **So sánh bằng bằng chứng:** RFC ngắn, hoặc spike 1–2 ngày trên một màn hình thật.
4. **Quyết định:** nếu không đồng thuận, người chịu trách nhiệm (tech lead hoặc owner) quyết, theo nguyên tắc "disagree and commit". Ghi vào ADR (architecture decision record) gồm lý do và điều kiện để xem xét lại.
5. **Theo dõi:** sau một thời gian, kiểm tra quyết định có đạt mục tiêu không.

Ví dụ với tình huống SwiftUI và UIKit trong bài tập, deadline 6 tuần: tôi có thể đề xuất giữ UIKit cho luồng đang làm dở, dùng SwiftUI cho màn hình mới qua `UIHostingController`, và hẹn xem lại sau release. Cả hai bên đều thấy mối quan tâm của mình được tính tới.

Trade-off: không phải quyết định nào cũng cần RFC. Quyết định dễ đảo ngược thì chọn nhanh; chỉ đầu tư quy trình cho quyết định khó đảo ngược.

### Bạn cân bằng giữa technical debt và tiến độ sản phẩm ra sao?

Tôi coi technical debt là thứ cần quản lý liên tục, không phải một dự án lớn phải xin riêng: ưu tiên nợ theo mức ảnh hưởng tới delivery và gắn việc trả nợ vào công việc sản phẩm.

Cách làm:

- **Lập danh sách nợ kèm tác động:** ví dụ "module Checkout không có test, mỗi thay đổi tốn thêm 2 ngày QA", "build mất 12 phút, mỗi engineer mất vài giờ mỗi tuần". Nợ không có tác động đo được thì ưu tiên thấp.
- **Trả nợ ở nơi sắp làm tính năng:** khi làm feature trong Checkout thì cộng thêm thời gian để thêm test và tách logic.
- **Ngân sách cố định:** ví dụ 15–20% capacity mỗi sprint, thống nhất với PM từ đầu, thay vì mỗi lần phải xin.
- **Nợ rủi ro cao được xử lý như bug:** security, crash, SDK sắp bị ngừng hỗ trợ, yêu cầu bắt buộc mới của App Store như privacy manifest.
- **Báo kết quả bằng ngôn ngữ product:** ít hotfix hơn, tính năng ra nhanh hơn.

Ví dụ khi kể trong phỏng vấn: "Tôi đề xuất dành một phần hai sprint để thêm test và tách networking khỏi view controller của Checkout; sau đó các tính năng ở vùng này làm nhanh hơn và ít bug hơn rõ rệt." Hãy dùng con số thật từ kinh nghiệm của bạn.

Trade-off: giai đoạn sản phẩm còn tìm product-market fit thì chấp nhận nợ nhiều hơn; sản phẩm đã trưởng thành với nhiều người dùng thì cần ngân sách trả nợ lớn hơn.

## Bẫy phỏng vấn

### "Kể về một lần bạn bất đồng với team hoặc manager"

**Dễ trả lời sai:** Kể câu chuyện mình đúng hoàn toàn và người khác sai, hoặc nói "tôi chưa bao giờ bất đồng với ai". Cả hai đều cho thấy thiếu tự nhận thức hoặc né câu hỏi.

**Nên trả lời:** Chọn một câu chuyện thật, kể theo cấu trúc tình huống → hành động → kết quả, nhấn vào việc bạn lắng nghe, dùng dữ liệu, và giữ quan hệ tốt. Câu chuyện mà cuối cùng bạn không thắng nhưng đã "disagree and commit" và hỗ trợ quyết định chung thường rất thuyết phục. Kết thúc bằng điều bạn học được.

### "Khi team chậm tiến độ, bạn làm gì?"

**Dễ trả lời sai:** "Tôi nhận hết task khó và làm thêm cuối tuần để kịp." Nghe tận tâm nhưng là red flag trong vòng leadership.

**Nên trả lời:** Hero culture biến bạn thành bottleneck và làm tăng rủi ro khi bạn vắng mặt (bus factor). Senior nhân năng lực của team: gỡ blocker, cắt scope cùng PM, chia task hợp lý, pair với người đang kẹt, viết tài liệu. Tự tay làm phần khó vẫn đúng khi thật sự gấp, nhưng phải kèm chia sẻ kiến thức để lần sau người khác làm được.

### Dùng "chúng tôi" hay "tôi" khi kể thành tích

**Dễ trả lời sai:** Chỉ nói "chúng tôi đã làm..." từ đầu tới cuối, khiến interviewer không biết vai trò của bạn; hoặc ngược lại, toàn "tôi" như thể một mình làm hết.

**Nên trả lời:** Nói rõ phần của bạn ("tôi phát hiện vấn đề, tôi viết RFC, tôi thuyết phục PM dành thời gian") và ghi nhận đóng góp của team. Kèm kết quả đo được nếu có, như giảm crash, giảm build time, rút ngắn thời gian release. Interviewer đang tìm bằng chứng về ảnh hưởng của cá nhân bạn trong bối cảnh làm việc nhóm.

## Bài tập

Team bạn bị chia đôi: một nửa muốn migrate sang SwiftUI ngay bây giờ, một nửa muốn giữ UIKit. Deadline product còn 6 tuần. Viết một tài liệu quyết định một trang bao gồm: trade-off của mỗi lựa chọn, khuyến nghị của bạn, và cách bạn truyền đạt nó cho cả engineering team và product manager.
