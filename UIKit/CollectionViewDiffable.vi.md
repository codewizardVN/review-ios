[English](./CollectionViewDiffable.md) | [Tiếng Việt](./CollectionViewDiffable.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Collection View và Diffable Data Source

## Ý chính

`UICollectionViewDiffableDataSource` giúp việc cập nhật list dễ lý giải hơn bằng cách mô tả state snapshot, thay vì tự tính insert và delete thủ công.

## Cần ôn

- Item identity ổn định: item identifier là giá trị `Hashable` mà diffable dùng để nhận ra "đây vẫn là item cũ". Nó nên là ID không đổi theo thời gian (ví dụ ID từ server), không phải toàn bộ dữ liệu hiển thị.
- Chi phí khi apply snapshot: mỗi lần `apply`, diffable so sánh snapshot cũ với mới để tính insert/delete/move, rồi cập nhật collection view. List càng lớn và apply càng thường xuyên thì càng tốn.
- Cell reuse và cấu hình cell: cell được tái sử dụng khi scroll, nên mỗi lần cấu hình phải set lại toàn bộ trạng thái hiển thị. Cách hiện đại là `UICollectionView.CellRegistration` (iOS 14+) kết hợp content configuration như `UIListContentConfiguration`.
- Mô hình section: section identifier cũng phải `Hashable` và duy nhất, thường là một enum (ví dụ `.unread`, `.read`). Layout cho từng section thường đi cùng `UICollectionViewCompositionalLayout`.

## Câu hỏi thực hành

- Vì sao diffable vẫn có thể chậm trên list lớn?
- Điều gì hỏng nếu item identifier không ổn định?

## Câu hỏi luyện tập

- Tại sao diffable vẫn có thể cảm giác chậm trên list lớn?
- Điều gì sẽ hỏng nếu item identifier không ổn định?

## Góc nhìn senior

Diffable data source cải thiện correctness, không phải phép màu performance. Bạn vẫn cần item identity tốt, tần suất apply snapshot hợp lý, và cell configuration đủ nhẹ.

## Đáp án câu hỏi luyện tập

### Tại sao diffable vẫn có thể cảm giác chậm trên list lớn?

Diffable chậm trên list lớn vì mỗi lần `apply` nó phải so sánh toàn bộ snapshot cũ với snapshot mới, và phần việc này cùng với việc cấu hình cell đều tốn thời gian trên main thread. Diffable chỉ giúp bạn không phải tự tính insert/delete, nó không làm việc tính toán biến mất.

Những nguyên nhân thường gặp:

- **Identifier nặng.** Nếu dùng cả model struct làm item identifier, mỗi lần diff phải hash và so sánh mọi field của hàng nghìn item. Dùng ID nhỏ (`UUID`, `Int`, `String`) sẽ nhanh hơn nhiều.
- **Apply quá thường xuyên.** Ví dụ mỗi tin nhắn WebSocket đến là apply một lần. Nên gộp thay đổi lại (debounce) rồi apply một lần.
- **Animate thay đổi quá lớn.** Animate hàng nghìn insert/delete cùng lúc rất nặng. Khi dữ liệu thay đổi toàn bộ (đổi filter chẳng hạn), dùng `applySnapshotUsingReloadData(_:)` (iOS 15+) để bỏ qua bước diff.
- **Reload thay vì reconfigure.** `reloadItems` bỏ cell cũ và dequeue cell mới. `reconfigureItems` (iOS 15+) cập nhật nội dung ngay trên cell hiện có, nhẹ hơn nhiều.
- **Cell configuration nặng.** Decode ảnh, format ngày, tính text attributed ngay trong cell provider.

Một chi tiết theo version: từ iOS 15, `apply(_:animatingDifferences: false)` vẫn diff, chỉ là không animate. Trước iOS 15 nó tương đương `reloadData`. Trade-off: tài liệu cũ của Apple cho phép gọi `apply` từ background queue miễn là luôn dùng cùng một queue (trộn main và background sẽ gây lỗi khó đoán). Nhưng trong SDK hiện tại, diffable data source là class UIKit được đánh dấu `@MainActor`, nên với Swift 6 hãy apply trên main actor, và nếu cần thì chỉ đưa phần chuẩn bị dữ liệu nặng ra khỏi main.

### Điều gì sẽ hỏng nếu item identifier không ổn định?

Nếu identifier không ổn định, diffable sẽ coi mỗi thay đổi là "xóa item cũ, thêm item mới", nên animation, selection, trạng thái cell và vị trí scroll đều bị hỏng. Diffable nhận diện item chỉ bằng `Hashable`. Nếu identifier đổi mỗi lần bạn tạo snapshot, ví dụ `UUID()` sinh mới mỗi lần map từ API, hoặc dùng cả struct có field `isRead`, thì với diffable đó là một item hoàn toàn khác.

Hậu quả cụ thể:

- Cell nhấp nháy hoặc fade out/fade in thay vì cập nhật tại chỗ.
- Mất selection, mất focus, text field trong cell bị reset.
- `reloadItems`/`reconfigureItems` không dùng được vì identifier cũ không còn trong snapshot.
- Nếu hai item trùng identifier trong cùng snapshot, app sẽ gặp exception (crash) khi tạo hoặc apply snapshot.

Với bài tập notifications, identifier nên là ID từ server của model notification trong app (ví dụ `AppNotification.ID`, đặt tên khác để khỏi nhầm với `Foundation.Notification`), không chứa `isRead`. Nội dung lấy từ một store theo ID. Khi đánh dấu đã đọc:

```swift
var snapshot = dataSource.snapshot()
snapshot.deleteItems([id])
snapshot.appendItems([id], toSection: .read)
dataSource.apply(snapshot, animatingDifferences: true)
```

Vì ID không đổi, diffable hiểu đây là một phép move, không phải xóa rồi thêm item lạ. Lưu ý: move chỉ đổi vị trí, không gọi lại cell provider. Nếu cell phải đổi giao diện (ví dụ bỏ chấm "chưa đọc"), hãy cập nhật store trước rồi gọi `reconfigureItems([id])` để cell đọc lại dữ liệu mới. Trade-off: nếu animation move giữa hai section vẫn gây rối mắt, có thể giữ item ở chỗ cũ với style "đã đọc" và chỉ sắp xếp lại khi user rời màn hình.

## Bẫy phỏng vấn

### "Dùng luôn model struct làm item identifier cho tiện, có sao không?"

**Dễ trả lời sai:** Không sao, struct là `Hashable` rồi, diffable sẽ tự nhận ra item nào thay đổi và cập nhật.

**Nên trả lời:** Diffable không biết "cùng item nhưng nội dung đổi". Nó chỉ biết hai hash có bằng nhau không. Đổi một field như `isRead` thì hash đổi, nên item cũ bị xóa và item mới được thêm, cell nháy và mất state. Apple khuyên dùng identifier là ID ổn định, còn khi nội dung đổi thì gọi `snapshot.reconfigureItems([id])`. Cách dùng cả struct chỉ ổn với dữ liệu gần như không bao giờ thay đổi.

### "reloadItems và reconfigureItems khác gì nhau?"

**Dễ trả lời sai:** Giống nhau, cái nào cũng làm cell hiển thị lại dữ liệu mới.

**Nên trả lời:** `reloadItems` bỏ cell hiện tại và dequeue cell mới qua cell provider, nên có thể nháy, mất trạng thái như text đang nhập, và tốn hơn. `reconfigureItems` (iOS 15+) gọi lại cell provider trên chính cell đang hiển thị, giữ nguyên cell, nhẹ và mượt hơn. Chỉ dùng `reloadItems` khi cần đổi sang một loại cell khác.

### "Item identifier trùng nhau ở hai section khác nhau thì được chứ?"

**Dễ trả lời sai:** Được, vì mỗi section là một danh sách riêng.

**Nên trả lời:** Identifier phải duy nhất trong **toàn bộ** snapshot, không chỉ trong một section. Trùng lặp sẽ gây exception (crash) khi tạo hoặc apply snapshot, với thông báo lỗi về identifier bị trùng. Nếu cùng một dữ liệu phải hiện ở hai section (ví dụ "Pinned" và "All"), hãy bọc lại thành enum như `case pinned(ID)` và `case all(ID)` để hai giá trị khác nhau.

## Bài tập

Thiết kế một collection view hai section cho notifications: `unread` và `read`. Định nghĩa item identifier và giải thích cách cập nhật một item từ unread sang read mà không tạo animation khó hiểu.
