[English](./RenderingPerformance.md) | [Tiếng Việt](./RenderingPerformance.vi.md)

[← SwiftUI](./README.vi.md)

# Hiệu năng Rendering

## Nguyên nhân thường gặp gây Re-render không cần thiết

- `@ObservedObject` / `@StateObject` publish thay đổi cho property mà view không thực sự dùng — với `ObservableObject`, một `@Published` bất kỳ đổi là mọi view observe object đó bị đánh giá lại `body`
- `@EnvironmentObject` lớn cập nhật thường xuyên — mọi view đọc object đó ở bất kỳ tầng nào đều bị invalidate
- Tính toán nặng trong `body` — sort/filter, tạo formatter, decode ảnh chạy lại mỗi lần `body` được gọi, trên main thread
- Thiếu `Equatable` conformance trên view type có thể dùng `.equatable()` — khi input của view chứa thứ SwiftUI không tự so sánh được (closure, reference type), SwiftUI coi là đã đổi

## Nội dung ôn tập

- `equatable()` modifier — với view conform `Equatable`, `.equatable()` (bọc view trong `EquatableView`) buộc SwiftUI dùng `==` của bạn để quyết định có cần đánh giá lại `body` hay không; nếu `==` trả `true` thì bỏ qua. Chỉ hữu ích khi so sánh mặc định của SwiftUI không đủ.
- Tách view — mỗi view con là một ranh giới invalidation riêng; view nhỏ chỉ nhận đúng dữ liệu nó cần (observation scope hẹp) nên khi dữ liệu khác đổi, `body` của nó không phải chạy lại.
- `LazyVStack` / `LazyHStack` — chỉ tạo view con khi chúng sắp xuất hiện trên màn hình thay vì tạo hết ngay từ đầu; nhưng không recycle view đã tạo.
- `List` vs `ScrollView + LazyVStack` — `List` được dựng trên `UICollectionView` của UIKit (iOS 16+; trước đó là `UITableView`) nên có cell reuse sẵn; `LazyVStack` linh hoạt layout hơn nhưng không reuse.

## Câu hỏi thực hành

- Tại sao view cứ reload không mong muốn?
- Nếu list lớn bị lag, bắt đầu debug từ đâu?

## Câu hỏi luyện tập

- Tại sao một view cứ reload liên tục ngoài ý muốn?
- Nếu một list lớn bị lag, bạn bắt đầu debug từ đâu?

## Góc nhìn Senior

Câu hỏi đầu tiên luôn là: `@Published` property nào thay đổi và view nào đang observe nó? (Với `@Observable` thì câu hỏi tương ứng là: property nào được đọc trong `body` vừa đổi.) Dùng template SwiftUI trong Instruments — từ Xcode 26 có SwiftUI instrument mới hiển thị các lần update `body` dài và đồ thị nguyên nhân (Cause & Effect) — hoặc thêm `let _ = Self._printChanges()` trong `body` để trace re-render khi debug.

## Đáp án câu hỏi luyện tập

### Tại sao một view cứ reload liên tục ngoài ý muốn?

Thường là vì view đang phụ thuộc vào một nguồn dữ liệu rộng hơn những gì nó thực sự dùng, nên mỗi thay đổi nhỏ ở nguồn đó đều khiến `body` của nó bị đánh giá lại.

Các nguyên nhân phổ biến:

- `ObservableObject`: bất kỳ `@Published` nào đổi cũng phát `objectWillChange`, và mọi view observe object đó bị invalidate, kể cả khi view không đọc property vừa đổi. Đây chính là tình huống `selectedTab` trong bài tập làm mọi row re-render.
- Parent re-render tạo lại child struct; nếu input của child không so sánh được (closure, reference type mới) SwiftUI coi là "đã đổi" và chạy lại `body` của child.
- Identity không ổn định: `.id(UUID())`, `ForEach(..., id: \.self)` với giá trị thay đổi, khiến view bị hủy và tạo lại chứ không chỉ cập nhật.
- Environment value đổi ở tầng trên (ví dụ environment object to).

Cách tìm: thêm `let _ = Self._printChanges()` vào `body` để xem property nào gây re-render (API có dấu gạch dưới, chỉ dùng khi debug). Cách sửa: tách view nhỏ và chỉ truyền giá trị view cần, chuyển sang `@Observable` (iOS 17+) để tracking theo từng property. Lưu ý: `body` chạy lại không đồng nghĩa với vẽ lại pixel; chỉ tối ưu khi nó gây vấn đề thật.

### Nếu một list lớn bị lag, bạn bắt đầu debug từ đâu?

Bắt đầu bằng việc đo, không đoán: profile trên thiết bị thật, bản Release, bằng Instruments (template SwiftUI, Time Profiler, Hitches/Animation Hitches) để biết frame bị trễ vì đâu.

Sau đó kiểm tra theo thứ tự:

1. Container: có đang dùng `VStack` hay `ScrollView` + `VStack` thường với hàng nghìn phần tử không? Chuyển sang `List` hoặc `LazyVStack`.
2. Việc làm trong `body` của row: tạo `DateFormatter`, sort/filter mảng, decode ảnh trên main thread. Chuyển các việc này vào model hoặc cache.
3. Identity: `ForEach` phải dùng ID ổn định (`Identifiable`); dùng index hay `.id()` thay đổi sẽ khiến list tạo lại toàn bộ row.
4. Observation scope: row có đang observe cả view model không? Truyền `User` (value) vào row thay vì cả `viewModel`.
5. Ảnh: load bất đồng bộ, downsample về đúng kích thước hiển thị.

Trade-off: `List` (dựa trên collection view của UIKit) tái sử dụng cell và thường mượt hơn với dữ liệu rất lớn, còn `LazyVStack` linh hoạt về layout hơn nhưng giữ lại view đã tạo. Đừng rải `.equatable()` khắp nơi trước khi đo được lợi ích.

## Bẫy phỏng vấn

### "LazyVStack cũng tái sử dụng view như List/UITableView?"

**Dễ trả lời sai:** Cho rằng `LazyVStack` recycle row giống `UITableView`, nên dùng nó thay `List` là hiệu năng tương đương với dữ liệu hàng chục nghìn phần tử.

**Nên trả lời:** `LazyVStack` chỉ trì hoãn việc tạo view cho đến khi cần hiển thị; nó không recycle. Row đã tạo thường được giữ lại khi cuộn qua, nên bộ nhớ tăng dần khi user cuộn sâu. `List` được dựng trên collection view của UIKit và tái sử dụng cell, nên với danh sách rất dài và đồng nhất, `List` thường là lựa chọn an toàn hơn.

### "Chuyển sang @Observable thì hết re-render thừa?"

**Dễ trả lời sai:** Nghĩ rằng `@Observable` tự động tối ưu mọi thứ, không cần quan tâm đến cách view đọc dữ liệu nữa.

**Nên trả lời:** `@Observable` chỉ track những property được đọc trong `body`, nên nó tốt hơn `ObservableObject` rất nhiều. Nhưng nếu `body` đọc cả mảng `users` rồi truyền từng phần tử xuống row, thì đổi một phần tử vẫn invalidate view đọc mảng đó; và nếu row nhận cả `viewModel` rồi đọc `viewModel.selectedTab`, row vẫn phụ thuộc vào tab. Tracking chỉ hẹp khi phạm vi đọc của bạn hẹp.

### "body được gọi lại nghĩa là view bị vẽ lại, rất tốn kém?"

**Dễ trả lời sai:** Coi mỗi lần `body` chạy là một lần render toàn màn hình, nên mục tiêu là không để `body` chạy lại bao giờ.

**Nên trả lời:** `body` chỉ tạo ra một mô tả view nhẹ; SwiftUI so sánh mô tả mới với cũ và chỉ cập nhật phần render tree thực sự khác. Chi phí thật đến từ việc nặng bên trong `body` và từ việc tạo lại identity. Vì vậy câu trả lời tốt là: giữ `body` rẻ và thuần túy, đo bằng Instruments, và chỉ tối ưu số lần gọi `body` khi nó hiện lên trong profile.

## Bài tập

Tạo `UserListView` với `@StateObject var viewModel` (một `ObservableObject`) có `@Published var users: [User]` và `@Published var selectedTab: Int`. Viết row view nhận cả view model (`@ObservedObject var viewModel`) cùng với user cần hiển thị, và thêm `let _ = Self._printChanges()` vào `body` của row. Thay đổi `selectedTab` và quan sát mọi row đều re-render không cần thiết. Sửa bằng cách cho row chỉ nhận giá trị nó cần (`let user: User`) thay vì cả view model, để observation scope của row hẹp lại. Xác nhận rows không còn re-render khi tab thay đổi (bản thân `UserListView` vẫn re-render, vì nó observe view model — điều đó là bình thường).
