[English](./LargeListOptimization.md) | [Tiếng Việt](./LargeListOptimization.vi.md)

[← Performance](./README.vi.md)

# Tối ưu List lớn

## Nguyên nhân gốc rễ của List bị lag

1. Cell configuration chậm (tính toán nặng, decode ảnh đồng bộ)
2. Tất cả cell được tạo cùng lúc (không có lazy loading)
3. Reload toàn list không cần thiết thay vì cập nhật dựa trên diff
4. Main thread bị block trong khi scroll

## UIKit

- `UICollectionView` / `UITableView` — cell được reuse qua `dequeueReusableCell`
- `UICollectionViewDiffableDataSource` — apply snapshot để cập nhật có animation và diff
- `UICollectionViewCompositionalLayout` — layout linh hoạt không cần tính frame thủ công
- `prefetchDataSource` — load data trước khi cell hiển thị

## SwiftUI

- `List` — trên iOS được dựng trên collection view của UIKit nên có cơ chế reuse cell tích hợp; ưu tiên dùng thay `ScrollView + ForEach` cho data lớn
- `LazyVStack` bên trong `ScrollView` — chỉ tạo row khi sắp hiện ra, nhưng không reuse cell như UIKit/`List`, nên với list rất dài có thể tốn memory hơn. Còn `VStack` thường trong `ScrollView` thì tạo toàn bộ row ngay từ đầu
- Tránh computed property nặng trong cell view
- Xác định item với `id` ổn định để SwiftUI diff hiệu quả

## Câu hỏi thực hành

- Nếu màn hình scroll kém, bạn kiểm tra gì đầu tiên?

## Câu hỏi luyện tập

- Nếu một màn hình scroll kém, bạn kiểm tra điều gì đầu tiên?

## Góc nhìn senior

Profile trước. Cách sửa phụ thuộc vào nguyên nhân gốc: cell configuration chậm vs allocation quá nhiều vs main thread bị block. Kiểm tra Time Profiler trong khi scroll trước khi viết bất kỳ code tối ưu nào.

## Đáp án câu hỏi luyện tập

### Nếu một màn hình scroll kém, bạn kiểm tra điều gì đầu tiên?

Đầu tiên tôi tái hiện trên thiết bị thật với release build, rồi profile trong lúc scroll để biết chính xác main thread đang làm gì — không đoán rồi sửa. Cụ thể:

- Chạy Instruments với Animation Hitches để xác nhận có hitch và biết đó là commit hitch (main thread chậm) hay render hitch (layer quá nặng).
- Nếu là commit hitch, xem Time Profiler lọc theo main thread, tìm stack nặng nhất trong `cellForItemAt`, `layoutSubviews` hoặc `body` của row.

Các nghi phạm thường gặp, theo thứ tự hay gặp:

- Decode hoặc resize ảnh đồng bộ trong cell.
- Tạo `DateFormatter`/`NumberFormatter` mới cho mỗi cell, hoặc tính toán nặng (parse, attributed string) khi configure.
- Self-sizing cell với Auto Layout phức tạp, constraint bị thêm lại mỗi lần reuse.
- `reloadData()` toàn bộ list trong khi chỉ một item thay đổi.
- Render hitch do shadow không có `shadowPath`, mask, blending.
- Với SwiftUI: identity không ổn định khiến row bị tạo lại, `body` tính toán nặng, hoặc một thay đổi state làm toàn bộ row re-render. Dùng instrument SwiftUI trong Instruments (bản mới từ Xcode 26) hoặc `Self._printChanges()` (API có dấu gạch dưới, chỉ dùng khi debug) để xem view nào update và vì sao.

Chỉ khi biết nguyên nhân mới chọn cách sửa: ảnh thì downsample và decode nền, formatter thì cache, reload thì chuyển sang diffable snapshot. Trade-off: prefetch và cache làm scroll mượt hơn nhưng tốn thêm memory và network, nên cần giới hạn và cancel khi không còn cần.

## Bẫy phỏng vấn

### "Item identifier của diffable data source dùng luôn model struct `Hashable` được không?"

**Dễ trả lời sai:** Cứ cho model conform `Hashable` rồi đưa thẳng vào snapshot, diffable tự lo phần còn lại.

**Nên trả lời:** Nếu identifier là cả struct, khi một field (ví dụ `isLiked`) thay đổi thì hash đổi, diffable hiểu là xoá item cũ và chèn item mới: animation sai, cell bị tạo lại, và nếu có hai item trùng giá trị thì app crash. Hãy dùng ID ổn định (`Item.ID`) làm identifier, lấy dữ liệu từ store theo ID, và khi nội dung đổi thì gọi `reconfigureItems(_:)` (iOS 15+) — nó cập nhật cell hiện có thay vì tạo cell mới như `reloadItems(_:)`.

```swift
snapshot.reconfigureItems([changedID])
```

### "`ForEach(items, id: \.self)` hoặc `id` tạo bằng `UUID()` có vấn đề gì?"

**Dễ trả lời sai:** Chỉ cần có một `id` nào đó là SwiftUI diff được.

**Nên trả lời:** `id` phải ổn định và duy nhất theo thời gian. `id: \.self` với dữ liệu có giá trị trùng hoặc giá trị thay đổi làm identity đổi theo nội dung; một computed `var id: UUID { UUID() }` tạo identity mới mỗi lần đọc. Hậu quả là SwiftUI coi mọi row là view mới: mất state (`@State`, vị trí scroll), animation sai, tạo lại toàn bộ row, scroll giật. Dùng ID thật từ server hoặc database.

### "Đã implement `prefetchDataSource` rồi thì data luôn sẵn sàng khi cell hiện ra?"

**Dễ trả lời sai:** Prefetch được gọi cho mọi cell trước khi hiển thị, nên `cellForItemAt` không cần xử lý trường hợp chưa có data.

**Nên trả lời:** Prefetch chỉ là gợi ý: khi người dùng scroll rất nhanh, nhảy lên đầu list, hoặc ngay lần hiển thị đầu tiên, nó có thể không được gọi hoặc không kịp xong. `cellForItemAt` vẫn phải hiện placeholder và tự bắt đầu load nếu cần; đồng thời phải cancel công việc trong `collectionView(_:cancelPrefetchingForItemsAt:)` để không tốn network cho những cell người dùng đã scroll qua.

## Bài tập

Build `UICollectionView` hiển thị 10.000 item dùng `UICollectionViewDiffableDataSource`. Apply snapshot update khi filter thay đổi. Sau đó chuyển sang SwiftUI và implement cùng list dùng `List` với `id` ổn định. So sánh hiệu năng scroll trên thiết bị thật với release build: dùng Animation Hitches để đo hitch (hitch time ratio) khi scroll, và Time Profiler để xem main thread tốn thời gian ở đâu. Ghi nhận sự khác biệt giữa hai cách.
