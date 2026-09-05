[English](./CoreData.md) | [Tiếng Việt](./CoreData.vi.md)

[← Persistence](./README.vi.md)

# Core Data

## Ý chính

Core Data là một object graph và persistence framework, không chỉ đơn thuần là wrapper của database. `NSManagedObjectContext` theo dõi các thay đổi; `NSPersistentContainer` sở hữu stack và SQLite store bên dưới.

## Những điều cần nắm

- `NSManagedObjectContext` — main context (UI) vs background context (write/import), không bao giờ share một context giữa các thread
- `NSPersistentContainer` / `NSPersistentCloudKitContainer` — setup stack, `newBackgroundContext()`
- Merge policy — `NSMergeByPropertyObjectTrumpMergePolicy` vs `NSMergeByPropertyStoreTrumpMergePolicy` để resolve conflict giữa các context
- Lightweight vs manual migration — khi nào automatic mapping model không đủ
- `NSFetchedResultsController` — điều khiển table/collection view theo thay đổi từ Core Data
- Faulting — object được load lazy; truy cập một fault ngoài thread của context sẽ crash

## Ví dụ

```swift
let backgroundContext = persistentContainer.newBackgroundContext()

backgroundContext.perform {
    let user = User(context: backgroundContext)
    user.name = "Trương"
    try? backgroundContext.save()
}
```

## Câu hỏi luyện tập

- Tại sao không bao giờ được truyền `NSManagedObject` trực tiếp giữa các thread?
- Điều gì xảy ra nếu hai context save các thay đổi xung đột lên cùng một object?

## Góc nhìn Senior

Phần lớn bug Core Data trong production là bug về threading, không phải bug về persistence — một `NSManagedObject` fetch trên background context rồi bị đụng vào ở main queue sẽ crash không thường xuyên khi tải cao, khiến rất khó bắt được trong code review. Nắm rõ nguyên tắc (mỗi thread một context, truyền `NSManagedObjectID` giữa các context thay vì truyền object) và giải thích được tại sao nó tồn tại.

## Bài tập

Thiết kế một luồng import ở background cho entity `Note`: parse 1.000 note từ JSON trên background context, save, rồi merge vào main context để một list SwiftUI cập nhật. Viết ra merge policy bạn sẽ chọn và giải thích điều gì xảy ra nếu user sửa một note trên UI trong lúc background import vẫn đang chạy.
