[English](./CoreData.md) | [Tiếng Việt](./CoreData.vi.md)

[← Persistence](./README.vi.md)

# Core Data

## Ý chính

Core Data là một object graph và persistence framework, không chỉ đơn thuần là wrapper của database. `NSManagedObjectContext` theo dõi các thay đổi; `NSPersistentContainer` sở hữu stack và SQLite store bên dưới.

## Những điều cần nắm

- `NSManagedObjectContext` — main context (`viewContext`, gắn với main queue, dùng cho UI) vs background context (private queue, dùng cho ghi/import dữ liệu lớn); mọi truy cập context và object của nó phải nằm trên queue của context đó (với background context là bên trong `perform`/`performAndWait`), không bao giờ dùng chung một context giữa các thread
- `NSPersistentContainer` / `NSPersistentCloudKitContainer` — setup stack, `newBackgroundContext()`
- Merge policy — quyết định ai thắng khi hai context cùng sửa một object: `NSMergeByPropertyObjectTrumpMergePolicy` (giá trị trong memory của context đang save thắng) vs `NSMergeByPropertyStoreTrumpMergePolicy` (giá trị đã có trong store thắng); mặc định là `NSErrorMergePolicy`, tức save sẽ throw khi có conflict
- Lightweight vs manual migration — lightweight migration tự suy ra mapping cho thay đổi đơn giản (thêm attribute optional hoặc có default, đổi tên có khai báo renaming identifier...); khi phải biến đổi dữ liệu (tách/gộp field, đổi kiểu) thì cần mapping model tùy chỉnh, hoặc từ iOS 17 dùng staged migration (`NSStagedMigrationManager`)
- `NSFetchedResultsController` — điều khiển table/collection view theo thay đổi từ Core Data
- Faulting — object được fetch về dưới dạng "fault" (chỉ là vỏ rỗng), dữ liệu chỉ thật sự được load khi bạn đọc property lần đầu; nếu việc đọc này xảy ra ngoài queue của context thì là data race, có thể crash hoặc trả dữ liệu sai

## Ví dụ

```swift
import CoreData
import os

let logger = Logger(subsystem: "com.example.app", category: "CoreData")

let backgroundContext = persistentContainer.newBackgroundContext()
// Đặt merge policy tường minh; mặc định là NSErrorMergePolicy (conflict thì save throw)
backgroundContext.mergePolicy = NSMergePolicy.mergeByPropertyStoreTrump

backgroundContext.perform {
    let user = User(context: backgroundContext)
    user.name = "Trương"

    // Không có thay đổi thì không cần save (tránh I/O và notification thừa)
    guard backgroundContext.hasChanges else { return }
    do {
        try backgroundContext.save()
    } catch {
        // Không dùng `try?`: lỗi (validation, merge conflict...) phải được log/báo lên,
        // rồi rollback để context không giữ lại thay đổi không lưu được
        logger.error("Background save failed: \(error.localizedDescription)")
        backgroundContext.rollback()
    }
}
```

## Câu hỏi luyện tập

- Tại sao không bao giờ được truyền `NSManagedObject` trực tiếp giữa các thread?
- Điều gì xảy ra nếu hai context save các thay đổi xung đột lên cùng một object?

## Góc nhìn Senior

Phần lớn bug Core Data trong production là bug về threading, không phải bug về persistence — một `NSManagedObject` fetch trên background context rồi bị đụng vào ở main queue sẽ crash không thường xuyên khi tải cao, khiến rất khó bắt được trong code review. Nắm rõ nguyên tắc (mỗi thread một context, truyền `NSManagedObjectID` giữa các context thay vì truyền object) và giải thích được tại sao nó tồn tại.

## Đáp án câu hỏi luyện tập

### Tại sao không bao giờ được truyền `NSManagedObject` trực tiếp giữa các thread?

Vì một `NSManagedObject` thuộc về đúng một `NSManagedObjectContext`, và context đó chỉ được dùng trên queue riêng của nó; đụng vào object từ queue khác là data race, có thể crash hoặc đọc ra dữ liệu sai.

Cơ chế: managed object không tự giữ dữ liệu một cách độc lập. Nhiều object là fault — khi bạn đọc `note.title`, object gọi ngược vào context để lấy dữ liệu từ row cache hoặc từ store. Context không thread-safe, nên đọc từ thread khác nghĩa là hai thread cùng thao tác trên state nội bộ của context. Lỗi này không xảy ra mọi lần mà chỉ khi hai bên tranh chấp đúng thời điểm, vì thế nó hay lộ ra lúc tải cao trong production.

Cách đúng là truyền `NSManagedObjectID` — thứ an toàn để chia sẻ giữa các thread — rồi lấy lại object trong context đích:

```swift
let id = note.objectID
try await viewContext.perform {
    let noteOnMain = try viewContext.existingObject(with: id) as? Note
    // dùng noteOnMain trên queue của viewContext
}
```

Lưu ý: object vừa insert có ID tạm thời cho tới khi save hoặc gọi `obtainPermanentIDs(for:)`. Khi debug, bật launch argument `-com.apple.CoreData.ConcurrencyDebug 1` để Core Data crash ngay tại chỗ truy cập sai queue thay vì crash ngẫu nhiên. Với Swift 6, `NSManagedObject` không `Sendable`, nên compiler cũng báo lỗi khi bạn đưa nó qua ranh giới isolation.

Trade-off: nếu chỉ cần hiển thị, map object sang một struct giá trị (snapshot) cũng an toàn, đổi lại mất khả năng tự cập nhật theo context.

### Điều gì xảy ra nếu hai context save các thay đổi xung đột lên cùng một object?

Kết quả phụ thuộc vào merge policy của context save sau: với policy mặc định (`NSErrorMergePolicy`), lần save đó thất bại với lỗi merge conflict; với các policy khác, Core Data tự giải quyết theo từng property.

Cơ chế: mỗi context giữ snapshot của object tại lúc nó fetch. Khi save, Core Data so snapshot đó với giá trị đang có trong store (optimistic locking). Nếu store đã bị context khác thay đổi thì đó là conflict:
- `NSErrorMergePolicy` (mặc định): `save()` throw lỗi có code `NSManagedObjectMergeError` — nếu code dùng `try? save()`, lỗi bị nuốt và dữ liệu âm thầm không được lưu; đó là lý do ví dụ trong file bắt lỗi bằng `do/catch`.
- `NSMergeByPropertyObjectTrumpMergePolicy`: giá trị trong memory của context đang save thắng, nhưng chỉ ở những property nó đã sửa; property khác lấy giá trị từ store.
- `NSMergeByPropertyStoreTrumpMergePolicy`: giá trị trong store thắng ở các property xung đột.
- `NSOverwriteMergePolicy`: ghi đè toàn bộ object bằng bản trong memory.

Với bài `Note`: nếu background import dùng StoreTrump còn `viewContext` dùng ObjectTrump, chỉnh sửa của user trên UI sẽ thắng dù ai save trước, còn import không ghi đè các field user vừa sửa. Đừng quên `viewContext.automaticallyMergesChangesFromParent = true` để UI nhận thay đổi từ background save.

Trade-off: không có policy nào "đúng" cho mọi trường hợp; chọn theo nguồn nào đáng tin hơn với từng loại dữ liệu. Khi cần logic phức tạp hơn (merge theo version), có thể subclass `NSMergePolicy`.

## Bẫy phỏng vấn

### Merge policy mặc định có tự giải quyết conflict không?

**Dễ trả lời sai:** "Có, Core Data tự merge, cái nào save sau thì thắng."

**Nên trả lời:** Mặc định là `NSErrorMergePolicy`, tức là không giải quyết gì cả: `save()` throw lỗi merge conflict. Nếu code dùng `try? context.save()` thì thay đổi mất mà không ai biết. Hãy đặt `mergePolicy` tường minh cho cả `viewContext` lẫn background context, và log lỗi save thay vì nuốt nó.

### Chạy `NSBatchInsertRequest` xong thì list SwiftUI có tự cập nhật không?

**Dễ trả lời sai:** "Có, vì đã bật `automaticallyMergesChangesFromParent`."

**Nên trả lời:** Batch insert/update/delete ghi thẳng xuống SQLite store và bỏ qua context, nên không có notification save nào để merge, và merge policy cũng không áp dụng. Phải yêu cầu request trả về object ID (`resultType = .objectIDs`) rồi gọi `NSManagedObjectContext.mergeChanges(fromRemoteContextSave:into:)`, hoặc bật persistent history tracking và xử lý history. Đổi lại, batch nhanh hơn và tốn ít memory hơn nhiều so với tạo 1.000 object trong context.

### "Mỗi thread một context" — vậy chỉ cần dùng background context trên một thread cố định là đủ?

**Dễ trả lời sai:** "Đúng, tôi tạo một background thread riêng rồi dùng context trên thread đó."

**Nên trả lời:** Với context `privateQueueConcurrencyType` (như context từ `newBackgroundContext()`), quy tắc thật là "chỉ đụng vào context bên trong `perform`/`performAndWait`", vì context có queue riêng và thread thực thi có thể khác nhau giữa các lần gọi. Gọi trực tiếp ngoài `perform`, kể cả từ một thread "cố định", vẫn là sai. `viewContext` là ngoại lệ: nó gắn với main queue, nên dùng trực tiếp trên main thread (hoặc trong code `@MainActor`) là hợp lệ.

## Bài tập

Thiết kế một luồng import ở background cho entity `Note`: parse 1.000 note từ JSON trên background context, save, rồi merge vào main context để một list SwiftUI cập nhật. Viết ra merge policy bạn sẽ chọn và giải thích điều gì xảy ra nếu user sửa một note trên UI trong lúc background import vẫn đang chạy.
