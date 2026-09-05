[English](./SwiftData.md) | [Tiếng Việt](./SwiftData.vi.md)

[← Persistence](./README.vi.md)

# SwiftData

## Ý chính

SwiftData là persistence framework thuần Swift của Apple, xây trên nền storage engine của Core Data, dùng macro (`@Model`) thay vì editor `.xcdatamodeld`.

## Những điều cần nắm

- `@Model` — biến một class Swift thuần thành entity được persist, storage sinh ra bởi macro
- `ModelContainer` / `ModelContext` — tương tự `NSPersistentContainer` / `NSManagedObjectContext`
- `@Query` — fetch khai báo (declarative) ngay trong SwiftUI view, tự cập nhật khi có thay đổi
- Migration — `SchemaMigrationPlan` cho các thay đổi schema có version
- Quan hệ với Core Data — dùng chung storage bên dưới; SwiftData là lớp API, không phải engine thay thế

## Ví dụ

```swift
@Model
final class Note {
    var title: String
    var body: String
    var createdAt: Date

    init(title: String, body: String, createdAt: Date = .now) {
        self.title = title
        self.body = body
        self.createdAt = createdAt
    }
}

struct NoteListView: View {
    @Query(sort: \Note.createdAt, order: .reverse) private var notes: [Note]
    @Environment(\.modelContext) private var context

    var body: some View {
        List(notes) { Text($0.title) }
    }
}
```

## Câu hỏi luyện tập

- Trade-off khi áp dụng SwiftData vào một app đã có dữ liệu Core Data nhiều năm là gì?
- Tại sao `@Query` giảm bớt boilerplate kiểu `NSFetchedResultsController`?

## Góc nhìn Senior

SwiftData hấp dẫn cho app SwiftUI mới hoàn toàn, nhưng với app production đã có Core Data model trưởng thành, chi phí migration và các khoảng trống edge-case (fetch request phức tạp, một số kịch bản sync CloudKit) thường lớn hơn lợi ích về ergonomics. Quyết định ở tầm senior không phải "cái nào mới hơn" mà là "migration thực sự tốn bao nhiêu so với schema và setup sync hiện tại."

## Bài tập

Phác thảo (trong comment) một ma trận quyết định so sánh Core Data vs SwiftData cho: một app SwiftUI hoàn toàn mới, và một app UIKit + Core Data hiện có với 3 năm dữ liệu người dùng và sync CloudKit. Nêu bạn chọn cái nào cho mỗi trường hợp và tại sao, kèm một rủi ro migration cụ thể cho trường hợp thứ hai.
