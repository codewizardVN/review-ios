[English](./CleanArchitecture.md) | [Tiếng Việt](./CleanArchitecture.vi.md)

[← Architecture](./README.vi.md)

# Clean Architecture

## Ý chính

Tổ chức code thành các tầng đồng tâm nơi dependency chỉ trỏ vào trong. Các tầng bên trong không biết gì về tầng bên ngoài.

## Các tầng (ngoài → trong)

1. **Presentation** — ViewModels, Views, UI logic
2. **Domain** — Use Cases, Entities, Repository protocols
3. **Data** — Repository implementations, API clients, local storage

## Quy tắc phụ thuộc

Domain layer không được import UIKit, Foundation networking, hay bất kỳ framework nào. Nó chỉ định nghĩa protocol để các tầng ngoài implement.

```text
Presentation → Domain ← Data
```

## Ví dụ

```swift
// Domain layer — pure Swift, no UIKit
protocol UserRepository {
    func fetchUser(id: String) async throws -> User
}

struct FetchUserUseCase {
    let repository: UserRepository
    func execute(id: String) async throws -> User {
        try await repository.fetchUser(id: id)
    }
}

// Data layer — implements the protocol
final class RemoteUserRepository: UserRepository {
    func fetchUser(id: String) async throws -> User { ... }
}
```

## Câu hỏi thực hành

- App nhỏ có nên dùng Clean Architecture không?
- Khi nào Clean Architecture trở thành over-engineering?

## Câu hỏi luyện tập

- Một app nhỏ có nên dùng Clean Architecture không?
- Khi nào Clean Architecture trở thành over-engineering?

## Góc nhìn Senior

Giá trị của Clean Architecture nằm ở testability và replaceability — bạn có thể swap data layer mà không động đến domain. Chi phí là boilerplate và indirection. Nó có giá trị với team lớn, domain phức tạp, hoặc app cần test nhiều.

## Bài tập

Implement tính năng "Get article list" theo 3 tầng: (1) Domain: `Article` entity, `ArticleRepository` protocol, `GetArticlesUseCase`. (2) Data: `RemoteArticleRepository` gọi mock URLSession. (3) Presentation: `ArticleListViewModel` dùng `GetArticlesUseCase`. Wire chúng trong unit test — không có network thật. Xác nhận domain layer không có UIKit hay networking imports.
