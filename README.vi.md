[English](./README.md) | [Tiếng Việt](./README.vi.md)

# iOS Senior Review Source

Nguồn ôn tập iOS dành cho level Senior, tập trung vào `Swift`, `SwiftUI`, kiến trúc, performance, testing và các chủ đề thường gặp khi phỏng vấn hoặc review design.

## Mục tiêu

Repo này được dùng để:

- Hệ thống hóa kiến thức iOS cho level Senior.
- Ôn tập nhanh các chủ đề cốt lõi trước phỏng vấn.
- Làm tài liệu tham chiếu khi build app thực tế bằng Swift/SwiftUI.
- Tổng hợp checklist để review code, architecture và quality.

## Đối tượng phù hợp

Phù hợp nếu bạn:

- Đã có kinh nghiệm làm iOS và muốn tổng hợp lại kiến thức nền tảng.
- Đang chuẩn bị phỏng vấn `Senior iOS Developer`.
- Muốn ôn theo hướng practical, không chỉ học syntax.

## Phạm vi ôn tập

### 1. Swift core

- Value type vs reference type
- ARC, memory management, retain cycle
- Protocol-oriented programming
- Generics, associated type, opaque type
- Error handling
- Access control
- Concurrency với `async/await`, `Task`, `Actor`

### 2. SwiftUI

- Vòng đời `View`
- State management: `@State`, `@Binding`, `@ObservedObject`, `@StateObject`, `@EnvironmentObject`
- Navigation
- List, lazy stack, performance rendering
- Dependency injection trong SwiftUI
- Interop giữa `SwiftUI` và `UIKit`

### 3. UIKit và app lifecycle

- App lifecycle
- ViewController lifecycle
- Coordinator / Router
- Auto Layout
- CollectionView, Diffable Data Source
- Deep link, universal link, notification flow

### 4. Architecture

- MVC, MVVM, Clean Architecture
- Modularization
- Dependency injection
- Separation of concerns
- State-driven UI
- Trade-off giữa simplicity và scalability

### 5. Data và networking

- URLSession
- Codable
- Pagination
- Retry / timeout / cancellation
- Cache strategy
- Offline-first thinking
- API client design

### 6. Performance

- Main-thread discipline
- Instruments cơ bản
- Memory graph debugging
- Rendering performance
- Startup time
- Large-list optimization

### 7. Testing

- Unit test
- UI test
- Mocking / stubbing
- Testable architecture
- Snapshot test
- Regression prevention

### 8. Chủ đề senior-level

- Code review mindset
- Refactoring strategy
- Debugging production issue
- Backward compatibility
- Release process
- Mentoring và technical ownership
- Trade-off analysis khi ra quyết định kỹ thuật

## Cấu trúc repo

```text
.
|-- README.md
|-- README.vi.md
|-- CHANGELOG.md
|-- Docs/
|-- Swift/
|-- SwiftUI/
|-- UIKit/
|-- Architecture/
|-- Networking/
|-- Concurrency/
|-- Performance/
|-- Testing/
`-- Senior/
```

Gợi ý cách học:

1. Ôn lại `Swift core` trước.
2. Chuyển sang `SwiftUI` và state management.
3. Review UIKit lifecycle và navigation fundamentals.
4. Review architecture và dependency management.
5. Luyện bài toán networking, concurrency, testing.
6. Kết thúc bằng performance, system design, và code review scenarios.

## Checklist ôn tập nhanh

- Bạn có giải thích rõ `struct` vs `class` không?
- Bạn có biết khi nào dùng `@StateObject` thay vì `@ObservedObject` không?
- Bạn có hiểu retain cycle xảy ra ở đâu trong closure, delegate, hoặc task không?
- Bạn có thể mô tả cache strategy cho app production không?
- Bạn có biết cách tách module để giảm coupling không?
- Bạn có thể viết test cho ViewModel, use case, và network layer không?
- Bạn có biết cách debug crash, leak, và frame drop không?
- Bạn có thể defend trade-off architecture trước team không?

## Hướng phát triển tiếp

Repo này có thể bổ sung thêm:

- Ví dụ code nhỏ cho từng chủ đề
- Các bộ interview Q&A
- Mini projects bằng `SwiftUI`
- Sample architecture cho app production
- Template checklist code review cho iOS team

## Định hướng chất lượng

Tài liệu và source nên ưu tiên:

- Đơn giản nhưng rõ ràng
- Có practical example
- Tập trung vào lý do và trade-off
- Hướng tới maintainability, testability, performance

## Ghi chú

Nếu muốn, có thể mở rộng repo này thành:

- `interview handbook` cho Senior iOS
- `practice playground` cho Swift/SwiftUI
- `real-world architecture reference`
