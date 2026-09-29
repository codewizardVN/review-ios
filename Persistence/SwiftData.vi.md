[English](./SwiftData.md) | [Tiếng Việt](./SwiftData.vi.md)

[← Persistence](./README.vi.md)

# SwiftData

## Ý chính

SwiftData là persistence framework thuần Swift của Apple, xây trên nền storage engine của Core Data, dùng macro (`@Model`) thay vì editor `.xcdatamodeld`.

## Những điều cần nắm

- `@Model` — macro biến một class Swift thuần thành entity được persist: nó sinh code lưu trữ cho từng stored property, cho class conform `PersistentModel` và `Observable`, nên SwiftUI tự cập nhật khi property thay đổi
- `ModelContainer` / `ModelContext` — tương tự `NSPersistentContainer` / `NSManagedObjectContext`
- `@Query` — fetch khai báo (declarative) ngay trong SwiftUI view, tự cập nhật khi có thay đổi
- Migration — `SchemaMigrationPlan` cho các thay đổi schema có version
- Quan hệ với Core Data — store mặc định của SwiftData chính là SQLite store của Core Data; SwiftData là lớp API mới phía trên, không phải engine thay thế (từ iOS 18 có thể viết custom data store qua protocol `DataStore`, nhưng hiếm khi cần)

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

## Đáp án câu hỏi luyện tập

### Trade-off khi áp dụng SwiftData vào một app đã có dữ liệu Core Data nhiều năm là gì?

Lợi ích là API thuần Swift gọn hơn và tích hợp tốt với SwiftUI; cái giá là rủi ro với dữ liệu thật của user, yêu cầu iOS 17+ và vài khoảng trống tính năng so với Core Data.

Những điểm cần cân nhắc:
- **Dùng lại store cũ không tự động.** SwiftData mở được chính file SQLite của Core Data, nhưng `@Model` phải khớp tên entity, attribute và relationship; tên khác cần `@Attribute(originalName:)`, và store URL phải trỏ đúng file cũ. Sai một chỗ là mất dữ liệu hoặc không mở được store.
- **Coexistence**: có thể chạy Core Data và SwiftData song song trên cùng store trong giai đoạn chuyển tiếp, nhưng phải giữ hai định nghĩa model đồng bộ và bật persistent history tracking.
- **Deployment target**: SwiftData cần iOS 17, và nhiều cải tiến quan trọng (`#Unique`, `#Index`, custom data store, nhiều bản sửa lỗi) chỉ có từ iOS 18, nên app còn hỗ trợ iOS 16 chưa dùng được.
- **Khoảng trống tính năng**: không có tương đương đầy đủ của `NSFetchedResultsController` với section, `#Predicate` hạn chế hơn `NSPredicate`, không có batch insert/update, ít quyền kiểm soát faulting và prefetch.
- **CloudKit**: sync tự động của SwiftData chỉ hỗ trợ private database; tính đến iOS 26 chưa hỗ trợ sharing (`CKShare`) hay public database như `NSPersistentCloudKitContainer`.

Trade-off thực tế: với app đang ổn định, thường tốt hơn là giữ Core Data, hoặc chỉ dùng SwiftData cho tính năng mới với store riêng, rồi đánh giá lại khi đã bỏ các bản iOS cũ. Chỉ migrate toàn bộ khi có lợi ích rõ ràng và đã test trên bản sao dữ liệu thật của user.

### Tại sao `@Query` giảm bớt boilerplate kiểu `NSFetchedResultsController`?

Vì `@Query` gói toàn bộ việc "fetch, theo dõi thay đổi và báo cho UI render lại" vào một property wrapper, nên view chỉ khai báo dữ liệu nó cần thay vì tự quản lý controller và delegate.

Với `NSFetchedResultsController` trong UIKit, bạn phải tạo `NSFetchRequest` với sort descriptor, khởi tạo controller với context, gọi `performFetch()`, implement delegate (`controllerDidChangeContent` hoặc `didChangeContentWith` snapshot), rồi apply snapshot vào diffable data source. `@Query` làm tất cả những việc đó ngầm: nó lấy `modelContext` từ environment, chạy fetch với sort/filter bạn khai báo, observe thay đổi trong context, và khi dữ liệu đổi thì SwiftUI render lại `body`. Trong `NoteListView`, một dòng `@Query(sort: \Note.createdAt, order: .reverse)` thay cho vài chục dòng setup.

Giới hạn cần biết:
- `@Query` chỉ dùng được trong SwiftUI `View`; ViewModel hay service phải dùng `FetchDescriptor` với `modelContext.fetch`, vốn không tự observe thay đổi.
- Muốn filter động (theo ô search), phải tạo lại query trong `init` của view bằng `Query(filter:sort:)` từ tham số truyền vào.
- Không có section sẵn như FRC; phải tự group.
- Fetch chạy trên main context, nên với tập dữ liệu lớn hãy đặt `fetchLimit` qua `FetchDescriptor`.

Trade-off: sự tiện lợi đến từ việc gắn chặt truy vấn với view, nên logic truy vấn khó test độc lập và khó dùng lại ngoài SwiftUI.

## Bẫy phỏng vấn

### Có thể truyền một `@Model` object sang background task để xử lý không?

**Dễ trả lời sai:** "Được, `@Model` chỉ là class Swift bình thường nên truyền như object thường."

**Nên trả lời:** Model object gắn với `ModelContext` đã fetch nó và không `Sendable`, giống `NSManagedObject`; Swift 6 sẽ báo lỗi khi bạn đưa nó qua ranh giới actor. Hãy truyền `persistentModelID` (kiểu `PersistentIdentifier`, là `Sendable`), rồi trong một actor đánh dấu `@ModelActor` (có context riêng) lấy lại object, ví dụ bằng `self[id, as: Note.self]` hoặc `modelContext.model(for:)` (trả về `any PersistentModel`, cần cast).

### Đổi tên property trong `@Model` (ví dụ `body` thành `content`) thì lightweight migration có tự lo không?

**Dễ trả lời sai:** "Có, SwiftData tự nhận ra và migrate."

**Nên trả lời:** SwiftData không đoán được việc đổi tên: nó coi đó là xóa attribute `body` và thêm attribute `content` mới, nên dữ liệu cũ bị mất. Phải khai báo `@Attribute(originalName: "body") var content: String` để lightweight migration map đúng. Với thay đổi phức tạp hơn (tách field, đổi kiểu), cần `VersionedSchema` và `MigrationStage.custom` trong `SchemaMigrationPlan`.

### Bật CloudKit sync cho model hiện có chỉ là thêm `cloudKitDatabase` vào `ModelConfiguration`?

**Dễ trả lời sai:** "Đúng, bật capability và cấu hình container là xong."

**Nên trả lời:** CloudKit đặt ràng buộc lên schema: không được dùng unique constraint (`@Attribute(.unique)`, `#Unique`), mọi relationship phải optional, và mọi property phải optional hoặc có default value. Model không theo các ràng buộc này sẽ khiến container không load được khi bật sync. Ngoài ra schema trên CloudKit production chỉ được thêm, không được xóa hay đổi field, nên phải thiết kế cẩn thận trước khi deploy schema.

## Bài tập

Phác thảo (trong comment) một ma trận quyết định so sánh Core Data vs SwiftData cho: một app SwiftUI hoàn toàn mới, và một app UIKit + Core Data hiện có với 3 năm dữ liệu người dùng và sync CloudKit. Nêu bạn chọn cái nào cho mỗi trường hợp và tại sao, kèm một rủi ro migration cụ thể cho trường hợp thứ hai.
