[English](./DependencyInjection.md) | [Tiếng Việt](./DependencyInjection.vi.md)

[← SwiftUI](./README.vi.md)

# Dependency Injection trong SwiftUI

## Ý chính

SwiftUI hoạt động tốt nhất khi dependency được thể hiện tường minh. View nên nhận dữ liệu và service nó cần qua initializer, environment value, hoặc state object mà ownership được xác định rõ.

## Cách tiếp cận phổ biến

### Initializer injection

Tốt cho dependency rõ ràng và preview dễ dựng.

### Environment injection

Hữu ích cho dependency dùng xuyên suốt app, nhưng có thể trở nên quá ngầm nếu lạm dụng.

### `@StateObject` ownership

Phù hợp khi view tạo và sở hữu một view model, còn view model đó lại phụ thuộc vào các service được truyền vào.

## Câu hỏi thực hành

- Khi nào `EnvironmentObject` hữu ích, khi nào quá "ma thuật"?
- Làm sao giữ SwiftUI preview dễ dựng?

## Góc nhìn senior

Mục tiêu không phải loại bỏ mọi convenience. Mục tiêu là giữ ownership và chiều của dependency đủ rõ để view tree vẫn testable và predictable.

## Bài tập

Thiết kế `ProfileView` phụ thuộc vào `UserRepository`. Hãy viết một phiên bản dùng initializer injection vào view model và một phiên bản dùng environment injection. Sau đó giải thích cách nào bạn ưu tiên cho một session dependency dùng chung toàn app.
