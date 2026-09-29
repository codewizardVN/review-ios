[English](./TestableDesign.md) | [Tiếng Việt](./TestableDesign.vi.md)

[← Testing](./README.vi.md)

# Thiết kế có thể kiểm thử

## Các nguyên tắc giúp code dễ test

1. **Inject dependency** — không tự tạo bên trong class những dependency có side effect (network, database, clock, analytics); nhận chúng qua initializer để test truyền fake vào. Có thể đặt giá trị mặc định cho production, ví dụ `init(service: ProfileService = LiveProfileService())`, miễn là test vẫn thay được.
2. **Phụ thuộc vào protocol (hoặc closure) ở ranh giới, không phải implementation cụ thể** — với dependency chậm hoặc bên ngoài, code chỉ biết đến protocol nên test dễ thay bằng fake. Không cần protocol cho logic thuần (xem bẫy phỏng vấn bên dưới).
3. **Tách side effect** — logic thuần túy (tính toán, quyết định) ở một chỗ, I/O (gọi API, ghi file, đọc giờ) ở ranh giới. Logic thuần test được chỉ bằng input/output, không cần fake.
4. **Tránh singleton và global state** — state dùng chung khiến test này ảnh hưởng test kia, kết quả phụ thuộc thứ tự chạy và dễ vỡ khi chạy song song.
5. **Đơn vị nhỏ, tập trung** — class lớn làm quá nhiều việc nên muốn test một phần phải dựng cả khối; tách nhỏ thì mỗi phần test riêng được.

## Dấu hiệu kiến trúc không thể kiểm thử

- ViewModel gọi `URLSession.shared` trực tiếp: test không thể thay network thật bằng dữ liệu giả.
- Logic nằm trong `viewDidLoad` hoặc `body`: phải dựng view hierarchy mới chạy được logic.
- Shared mutable global state: các test ghi đè state của nhau.
- Initializer khởi động service thật (mở kết nối, đọc database, bắt đầu timer): chỉ tạo object để test đã kéo theo side effect.

## Câu hỏi thực hành

- Có nên test tất cả mọi thứ không?
- Bao nhiêu UI testing là đủ mà không trở nên flaky?

## Câu hỏi luyện tập

- Có nên test mọi thứ không?
- Bao nhiêu UI test là đủ mà không bị flaky?

## Góc nhìn senior

Khả năng test là thước đo của thiết kế tốt. Tư duy senior tối ưu độ tin cậy trên chi phí — không phải số lượng test bằng mọi giá. Viết test ở những nơi mà failure sẽ gây đau đớn, không phải ở mọi nơi như nhau.

## Đáp án câu hỏi luyện tập

### Có nên test mọi thứ không?

Không. Nên *thiết kế* để mọi thứ quan trọng đều có thể test được, nhưng chỉ *viết* test ở nơi mà lỗi gây hậu quả thật hoặc logic đủ phức tạp để dễ sai.

Hai ý này hay bị gộp làm một. Testability là thuộc tính của thiết kế: dependency được inject, logic tách khỏi I/O, không có global state. Có được điều đó thì khi cần viết test, chi phí rất thấp. Còn việc có viết test hay không là quyết định đầu tư:

- **Nên test**: business rule, tính toán tiền, state machine, parsing, xử lý lỗi, code dùng chung nhiều nơi, và các bug đã từng xảy ra.
- **Có thể bỏ qua**: code chỉ nối dây (gọi thẳng sang dependency), view layout đơn giản, prototype sắp bị bỏ, và hành vi của framework Apple.

Một cách nghĩ hữu ích là "confidence per cost": mỗi test tốn thời gian viết, thời gian chạy và công bảo trì mỗi lần code đổi. Test ở tầng thấp (unit) rẻ và nhanh, nên phủ nhiều logic ở đó; test ở tầng cao (UI) đắt, nên chỉ giữ cho vài journey chính.

Trade-off: nếu team đặt quy tắc "phải test mọi thứ", họ thường sinh ra test lặp lại implementation, vỡ khi refactor, và làm mọi người sợ thay đổi code. Mục tiêu của test là giúp thay đổi code an toàn hơn, không phải làm nó chậm lại.

### Bao nhiêu UI test là đủ mà không bị flaky?

Đủ là khi mỗi journey quan trọng nhất của business có một UI test cho happy path, còn mọi biến thể khác được đẩy xuống unit test; với đa số app, con số đó chỉ khoảng vài chục test, không phải hàng trăm.

Lý do là UI test chạy qua cả app thật, simulator, animation và accessibility tree, nên mỗi test thêm vào là thêm một nguồn không xác định. Số test càng nhiều thì xác suất có ít nhất một test fail ngẫu nhiên trong mỗi lần CI chạy càng cao, và team bắt đầu bấm "re-run" thay vì đọc lỗi.

Dấu hiệu bạn đã có quá nhiều UI test:

- Chúng kiểm tra validation, format text hoặc nhánh lỗi mà unit test làm được.
- Suite chạy lâu đến mức dev không chạy trước khi merge.
- Tỷ lệ flaky vượt khoảng 1–2% và không ai sửa.

Để giữ ít mà vẫn tin được: dùng dữ liệu stub qua launch argument, `accessibilityIdentifier` ổn định, chờ theo điều kiện thay vì `sleep`, và theo dõi tỷ lệ flaky của từng test. Test nào flaky liên tục thì sửa ngay, hoặc cách ly (quarantine) rồi viết lại, đừng để nó làm mất lòng tin vào cả suite.

## Bẫy phỏng vấn

### "Để code testable, mỗi class nên có một protocol đi kèm, đúng không?"

**Dễ trả lời sai:** Đúng, mỗi service, ViewModel, helper đều cần một protocol để có thể thay bằng fake.

**Nên trả lời:** Protocol chỉ cần ở *ranh giới* với thứ chậm, không xác định hoặc bên ngoài: network, database, clock, analytics. Logic thuần (formatter, validator, reducer) nên test trực tiếp bằng implementation thật, không cần protocol. Tạo protocol 1:1 cho mọi class thêm nhiều file và indirection mà không tăng confidence. Ngoài protocol, dependency cũng có thể là closure, ví dụ `init(fetch: @escaping () async throws -> Profile)`, gọn hơn cho dependency chỉ có một hành vi.

### "Method private chứa logic quan trọng. Làm sao test nó?"

**Dễ trả lời sai:** Đổi `private` thành `internal` rồi dùng `@testable import` để gọi trực tiếp.

**Nên trả lời:** Nên test method private *thông qua* API public gọi đến nó, vì đó mới là hành vi người dùng của class nhìn thấy. `@testable import` chỉ mở quyền truy cập cho `internal`, không mở `private`. Nếu logic private phức tạp đến mức muốn test riêng, đó là dấu hiệu nó nên được tách thành một type riêng (ví dụ `PriceCalculator`) với API riêng; khi đó test nó trực tiếp là hợp lý.

### "Hàm này dùng `Date()` để kiểm tra token hết hạn. Vẫn test được mà, chỉ cần chạy thôi?"

**Dễ trả lời sai:** Được, `Date()` là API chuẩn nên không cần inject.

**Nên trả lời:** `Date()` là dependency ẩn vào đồng hồ hệ thống, nên test cho trường hợp "đã hết hạn" hoặc "sắp hết hạn" không thể chạy ổn định. Hãy inject thời gian, ví dụ `init(now: @escaping () -> Date = Date.init)`, để test truyền vào một ngày cố định. Tương tự, code dùng `Task.sleep` hoặc debounce có thể nhận `any Clock<Duration>` (iOS 16+) để test thay bằng clock điều khiển được. Apple không cung cấp sẵn test clock; có thể tự viết hoặc dùng thư viện như swift-clocks của Point-Free (`TestClock`, `ImmediateClock`). `UUID()` và random cũng nên được inject theo cách này.

## Bài tập

Lấy đoạn code không thể test này: `ProfileViewController` gọi `URLSession.shared.dataTask` trực tiếp trong `viewDidLoad`. Refactor để có thể test bằng cách tách `ProfileService` protocol, inject qua initializer, và viết một unit test không chạm đến network.
