[English](./SystemDesign.md) | [Tiếng Việt](./SystemDesign.vi.md)

[← Chủ đề Senior](./README.vi.md)

# System Design cho iOS Apps

## Cần tập trung vào gì

- Ranh giới feature và ownership của module
- Luồng dữ liệu từ API qua storage tới UI
- Yêu cầu offline và caching
- Reliability, observability, và release risk

## Một câu trả lời senior tốt

Bắt đầu từ yêu cầu sản phẩm, rồi giải thích:

- thành phần chính
- quan hệ phụ thuộc giữa chúng
- state nằm ở đâu
- failure được xử lý thế nào
- phần nào sẽ hoãn lại cho bản đầu tiên nhỏ hơn

## Tình huống ví dụ

Thiết kế một app feed có:

- API cần đăng nhập
- local cache cho item gần đây
- pagination
- pull to refresh
- hỗ trợ đọc offline

Một cách tách hợp lý:

- `FeedAPIClient` cho transport
- `FeedRepository` cho mapping và điều phối cache
- `FeedStore` cho persistence
- `FeedViewModel` hoặc reducer cho screen state
- `FeedCoordinator` cho navigation

## Câu hỏi thực hành

- Bạn tách module trong app đang lớn lên như thế nào?
- Với team hai người, bạn sẽ đơn giản hóa phần nào?

## Câu hỏi luyện tập

- Bạn tách module thế nào trong một app đang phát triển?
- Bạn sẽ đơn giản hóa điều gì cho một team chỉ có hai engineer?

## Góc nhìn senior

Câu trả lời system design không phải để vẽ nhiều box nhất. Nó là cách thể hiện judgment: độ phức tạp nào hợp lý lúc này, phần nào nên defer, và design vẫn vận hành được ra sao khi sản phẩm lớn lên.

## Đáp án câu hỏi luyện tập

### Bạn tách module thế nào trong một app đang phát triển?

Tôi tách module theo feature và theo hướng phụ thuộc, nhưng chỉ tách khi ranh giới đã rõ và có lý do cụ thể như build time chậm, nhiều người cùng sửa một chỗ, hoặc cần tái sử dụng code.

Cách chia hay dùng:

- **Core module** (networking, persistence, design system, logging): không biết gì về feature.
- **Feature module** (Feed, Profile, Checkout): mỗi module sở hữu UI, view model và repository của mình, chỉ phụ thuộc vào core.
- Feature không import trực tiếp lẫn nhau. Chúng giao tiếp qua protocol hoặc một interface module nhỏ, và app target (hoặc coordinator) là nơi nối mọi thứ lại.

Với ví dụ feed ở trên: `FeedAPIClient` dựa vào core networking, còn `FeedRepository`, `FeedStore`, `FeedViewModel`, `FeedCoordinator` nằm trong module Feed. Trong Xcode hiện nay, cách nhẹ nhất là một local Swift Package có nhiều target, để compiler tự chặn import sai hướng thay vì chỉ dựa vào quy ước.

Trade-off: mỗi module thêm chi phí — phải thiết kế public API, lo access control, cấu hình build, và dễ sinh ra protocol trừu tượng quá sớm. Tách quá sớm khi domain còn thay đổi mạnh sẽ khiến bạn liên tục chuyển code qua lại giữa các module. Tôi thường bắt đầu bằng folder rõ ràng cộng quy ước dependency, rồi mới nâng lên package khi ranh giới đã ổn định.

### Bạn sẽ đơn giản hóa điều gì cho một team chỉ có hai engineer?

Với hai engineer, tôi cắt mọi thứ có chi phí vận hành lớn hơn lợi ích: ít module, ít lớp trừu tượng, tận dụng công cụ có sẵn của Apple và dịch vụ managed.

Cụ thể:

- Một app target, chia folder theo feature; tối đa thêm một package Core nếu thật sự cần.
- MVVM đơn giản với `@Observable` thay vì kiến trúc nhiều tầng như VIPER, trừ khi team đã quen.
- Offline đơn giản: lưu vài trang đầu của feed bằng SwiftData hoặc file JSON, thay vì tự viết sync engine hai chiều.
- Pagination dùng cursor do backend trả về (app chỉ gửi lại cursor để lấy trang tiếp), thay vì tự tính offset/số trang ở client; cách này đơn giản và tránh trùng hoặc sót item khi feed có item mới được chèn lên đầu.
- CI một workflow duy nhất: build, test, upload TestFlight bằng Xcode Cloud hoặc một lane Fastlane.
- Crash reporting và analytics dùng dịch vụ có sẵn.

Nguyên tắc là vẫn giữ đường nâng cấp: đặt ranh giới ở chỗ dễ thay, ví dụ `FeedRepository`, để sau này nâng cấp cache mà không phải đập lại UI. Những thứ không nên cắt dù team nhỏ: error handling, crash reporting, test cho logic quan trọng, và feature flag hoặc kill switch cho phần rủi ro.

Trade-off: đơn giản hóa sẽ tạo nợ khi team lên 8–10 người. Vì vậy nên ghi rõ trong design doc những điểm sẽ tách ra khi team lớn, để quyết định hôm nay là có chủ đích chứ không phải do thiếu hiểu biết.

## Bẫy phỏng vấn

### Interviewer vừa đưa đề, bạn bắt đầu vẽ kiến trúc ngay

**Dễ trả lời sai:** Nhảy thẳng vào vẽ các box Clean Architecture hoặc VIPER, liệt kê layer và pattern trước khi hỏi bất kỳ yêu cầu nào. Cách này cho thấy bạn áp khuôn có sẵn thay vì thiết kế cho bài toán thật.

**Nên trả lời:** Dành vài phút đầu để làm rõ scope: người dùng là ai, số lượng dữ liệu, có cần offline không, auth thế nào, yêu cầu nào là bắt buộc cho version 1. Sau đó nói rõ giả định và ưu tiên, rồi mới đi vào component. Interviewer chấm cách bạn thu hẹp đề và đưa ra trade-off, không chấm số box.

### "Offline hoạt động thế nào? Dữ liệu nào là source of truth?"

**Dễ trả lời sai:** "Cứ cache response lại, không có mạng thì đọc cache." Câu này bỏ qua invalidation, conflict khi ghi offline, và việc cache thuộc về user nào.

**Nên trả lời:** Chọn một source of truth rõ ràng, thường là local store: UI observe `FeedStore`, còn `FeedRepository` lấy dữ liệu từ network rồi ghi vào store. Nói rõ khi nào dữ liệu hết hạn, xóa cache khi logout hoặc đổi tài khoản, và nếu có thao tác ghi offline (như đánh dấu đã đọc) thì dùng queue với idempotency key để retry an toàn và giải quyết conflict theo quy tắc rõ ràng.

### Thiết kế như thể app là một backend service

**Dễ trả lời sai:** Giả định có thể deploy và rollback bất cứ lúc nào, mọi người dùng luôn chạy version mới nhất, nên API cứ đổi theo app.

**Nên trả lời:** App mobile không rollback được trên App Store, và người dùng có thể giữ version cũ hàng tháng. Vì vậy design cần API tương thích ngược, feature flag hoặc remote config để tắt tính năng lỗi, cơ chế minimum supported version cho trường hợp bắt buộc, và observability (crash reporting, log, metric) ngay từ đầu. Nhắc tới những điểm này là tín hiệu senior rõ ràng.

## Bài tập

Phác thảo một tính năng notification inbox. Gồm sync strategy, cập nhật read/unread, pagination, và điểm vào từ push notification. Sau đó giải thích phần nào bạn sẽ cố ý chưa xây ở version 1.
