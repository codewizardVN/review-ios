[English](./AccessControl.md) | [Tiếng Việt](./AccessControl.vi.md)

[← Swift Core](./README.vi.md)

# Access Control

## Nội dung ôn tập

- `private` — chỉ hiển thị trong phạm vi khai báo bao quanh và các extension của nó trong cùng file
- `fileprivate` — hiển thị trong cùng source file
- `internal` — hiển thị trong module (mặc định nếu không ghi gì). Một app target là một module, mỗi framework/Swift package target là một module riêng.
- `package` — (Swift 5.9, SE-0386) hiển thị cho mọi module trong cùng một Swift package, nhưng không lộ ra cho code ngoài package. Hữu ích khi tách một package thành nhiều module mà không muốn biến API nội bộ thành `public`.
- `public` — hiển thị bên ngoài module, nhưng code ở module khác không thể subclass class hay override member đó
- `open` — hiển thị bên ngoài module và có thể subclass/override từ module khác; chỉ dùng cho class và member của class

## Câu hỏi luyện tập

- Bạn sẽ thiết kế struct KeychainStore với các access level phù hợp cho items được lưu trữ, các method public read/write, và helper encrypt private như thế nào, và điều gì sẽ hỏng nếu items là public?

## Góc nhìn Senior

Access control là về API boundaries và giảm thiểu việc sử dụng sai, không chỉ đơn thuần là ẩn chi tiết implementation.

## Đáp án câu hỏi luyện tập

### Bạn sẽ thiết kế struct KeychainStore với các access level phù hợp cho items được lưu trữ, các method public read/write, và helper encrypt private như thế nào, và điều gì sẽ hỏng nếu items là public?

Tôi để `items` là `private`, `read(key:)` và `write(key:value:)` là `public`, còn `encrypt(_:)` là `private`; nếu `items` là public thì code bên ngoài có thể ghi thẳng vào dictionary, bỏ qua `encrypt` và phá vỡ quy tắc "mọi giá trị lưu vào đều đã được mã hóa".

Cơ chế: access control giúp compiler bảo vệ invariant của kiểu. Khi `items` là `private`, con đường duy nhất để ghi dữ liệu là `write`, và `write` luôn gọi `encrypt` — nên invariant luôn đúng mà không cần kiểm tra ở chỗ khác. `encrypt` là chi tiết implementation, để `private` thì có thể đổi thuật toán bất cứ lúc nào mà không ảnh hưởng ai.

Nếu `items` là `public`, sẽ hỏng ba thứ: có thể lưu plaintext qua `store.items["token"] = "abc"`; `read` có thể nhận dữ liệu chưa mã hóa và giải mã sai; và caller bị phụ thuộc vào `[String: String]`, nên sau này bạn không thể đổi sang Keychain thật (`SecItemAdd`/`SecItemCopyMatching`) mà không phá API.

Lưu ý thực tế: vì có member `public` nên bản thân `KeychainStore` cũng phải là `public struct`, và cần viết một `public init()` vì memberwise initializer không tự động public. Nếu chỉ cần cho đọc từ bên ngoài, `public private(set) var` là lựa chọn ở giữa. Nếu code chỉ dùng trong app (một module), `internal` là đủ, không cần `public`.

## Bẫy phỏng vấn

### "Đánh dấu private thì dữ liệu nhạy cảm được bảo mật đúng không?"

**Dễ trả lời sai:** Đúng, `private` ngăn không ai đọc được `items` nên token an toàn.

**Nên trả lời:** Access control chỉ là kiểm tra lúc compile, không phải cơ chế bảo mật. Lúc runtime, dữ liệu vẫn nằm trong bộ nhớ và đọc được qua debugger, trên thiết bị jailbreak, hoặc thậm chí bằng `Mirror(reflecting: store).children` — Mirror vẫn thấy stored property `private`. Dữ liệu nhạy cảm cần lưu vào Keychain thật (Security framework) và hạn chế thời gian nằm trong bộ nhớ.

### "public struct thì memberwise initializer cũng public chứ?"

**Dễ trả lời sai:** Có, struct là public thì init tự sinh cũng dùng được từ module khác.

**Nên trả lời:** Không. Memberwise initializer tự sinh có access level tối đa là `internal`, và sẽ là `private` nếu có stored property `private`. Tương tự, member bên trong một `public` type mặc định vẫn là `internal`. Muốn module khác tạo được instance, bạn phải tự viết `public init(...)`.

### "private không nhìn thấy được từ extension, phải dùng fileprivate đúng không?"

**Dễ trả lời sai:** Đúng, muốn extension truy cập được thì phải đổi `private` thành `fileprivate`.

**Nên trả lời:** Đó là hành vi của Swift 3. Từ Swift 4 (SE-0169), member `private` nhìn thấy được trong các extension của cùng kiểu nằm trong cùng file. `fileprivate` chỉ cần khi một kiểu khác trong cùng file phải truy cập. Một điểm liên quan: `@testable import` chỉ mở các symbol `internal` cho test, không mở `private` hay `fileprivate`.

## Bài tập

Thiết kế một struct `KeychainStore` lưu trữ `private var items: [String: String]`. Expose một `public func read(key: String) -> String?` và một `public mutating func write(key: String, value: String)`. Giữ `private func encrypt(_ value: String) -> String` là chi tiết implementation riêng tư của `KeychainStore` (`private`, không phải `internal`), để chỉ `write` gọi được nó. Viết comment cho từng access level giải thích quyết định thiết kế. Giải thích điều gì sẽ bị phá vỡ nếu `items` là public.
