[English](./StateManagement.md) | [Tiếng Việt](./StateManagement.vi.md)

[← SwiftUI](./README.vi.md)

# Quản lý State

## Tổng quan Property Wrappers

| Wrapper | Sở hữu state? | Nguồn |
|---|---|---|
| `@State` | Có | Local trong view này |
| `@Binding` | Không | Truyền vào từ parent |
| `@StateObject` | Có | Sở hữu object lifetime |
| `@ObservedObject` | Không | Object được sở hữu bởi nơi khác |
| `@EnvironmentObject` | Không | Inject từ ancestor |

Từ iOS 17, với class `@Observable` (Observation framework) bộ tương ứng là: `@State` để sở hữu instance, property thường (`let`/`var`) hoặc `@Bindable` khi cần tạo binding tới property của nó, và `.environment(model)` + `@Environment(Model.self)` thay cho `EnvironmentObject`.

## Nội dung ôn tập

- `@State` — state local của view (thường là value type); storage do SwiftUI giữ theo identity của view, nên giá trị không mất khi struct view bị tạo lại. Nên khai báo `private`.
- `@Binding` — tham chiếu hai chiều (đọc và ghi) tới state mà view khác sở hữu; view con sửa binding thì state ở parent đổi theo.
- `@StateObject` — tạo và sở hữu một `ObservableObject`; object được tạo một lần cho mỗi identity và sống qua các lần struct view bị tạo lại.
- `@ObservedObject` — chỉ subscribe vào `ObservableObject` do nơi khác tạo và giữ; bản thân nó không giữ object sống.
- `@EnvironmentObject` — đọc một `ObservableObject` mà ancestor đã inject bằng `.environmentObject()`, tìm theo type; thiếu inject thì crash lúc runtime.

## Điểm khác biệt quan trọng: `@StateObject` vs `@ObservedObject`

```swift
// Đúng: view này sở hữu view model
struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()
}

// Đúng: parent tạo ra, view này chỉ observe
struct FeedView: View {
    @ObservedObject var viewModel: FeedViewModel
}
```

Dùng `@ObservedObject` (kiểu `@ObservedObject var viewModel = FeedViewModel()`) khi view đáng lẽ phải sở hữu object sẽ khiến object bị tạo mới mỗi lần struct view bị init lại — tức là mỗi lần parent re-render — và mọi state trong đó bị reset.

## Câu hỏi thực hành

- Khi nào nên dùng `@StateObject` thay vì `@ObservedObject`?
- Khi nào `EnvironmentObject` phù hợp, và khi nào là lạm dụng?

## Câu hỏi luyện tập

- Khi nào nên dùng @StateObject thay vì @ObservedObject?
- Khi nào EnvironmentObject phù hợp, và khi nào là lạm dụng?

## Góc nhìn Senior

Luồng dữ liệu một chiều: state đi xuống qua binding và environment, events đi lên qua callback hoặc view model method. Giữ nhất quán chiều này ngăn subtle re-render bugs.

## Đáp án câu hỏi luyện tập

### Khi nào nên dùng @StateObject thay vì @ObservedObject?

Dùng `@StateObject` khi chính view này tạo ra object và phải là owner của nó; dùng `@ObservedObject` khi object được tạo và giữ ở nơi khác rồi truyền vào view.

Lý do nằm ở chỗ view struct bị tạo lại rất thường xuyên — mỗi lần parent re-render là một instance struct mới. `@StateObject` lưu object trong storage do SwiftUI quản lý, gắn với identity của view, và initializer của nó là autoclosure chỉ chạy một lần cho mỗi identity. `@ObservedObject` thì chỉ là một tham chiếu để subscribe `objectWillChange`; nó không giữ object sống qua các lần tạo lại struct. Nếu viết `@ObservedObject var viewModel = CartViewModel()`, mỗi lần `ShoppingCartView` bị init lại (do parent của nó re-render) bạn sẽ thấy log "CartViewModel init" lặp lại và mọi state trong view model bị reset.

Quy tắc ngắn gọn: ai tạo thì dùng `@StateObject`, ai nhận thì dùng `@ObservedObject`.

Từ iOS 17 với `@Observable`, cặp tương ứng là `@State` (owner) và property thường hoặc `@Bindable` (nhận vào). Trade-off: `@StateObject` chỉ dùng giá trị khởi tạo đầu tiên, nên nếu view model phụ thuộc vào tham số thay đổi theo thời gian (như `itemID`), bạn phải tự xử lý việc cập nhật, ví dụ qua `.task(id:)` hoặc `.id(itemID)`.

### Khi nào EnvironmentObject phù hợp, và khi nào là lạm dụng?

`EnvironmentObject` phù hợp cho dependency thực sự dùng chung ở nhiều tầng và sống theo app hoặc scene — session đăng nhập, theme, router, settings — và là lạm dụng khi dùng nó chỉ để khỏi truyền dữ liệu qua một hai tầng view.

Cơ chế: ancestor gọi `.environmentObject(obj)`, mọi view con cháu có `@EnvironmentObject` sẽ tìm object theo type. Tiện lợi, nhưng có ba cái giá:

- Dependency bị ẩn: nhìn signature của view không biết nó cần gì, preview và test phải nhớ inject đúng.
- Thiếu object là crash lúc runtime, không phải lỗi compile.
- Với `ObservableObject`, bất kỳ `@Published` nào đổi cũng invalidate mọi view đang observe object đó (kể cả view không đọc property vừa đổi), nên một object "tổng" to và đổi liên tục sẽ kéo cả cây view re-render.

Dấu hiệu lạm dụng: đưa view model riêng của một màn hình vào environment, hoặc một `AppState` khổng lồ chứa mọi thứ. Từ iOS 17, `.environment(model)` với `@Environment(Model.self)` và `@Observable` giúp tracking theo từng property nên đỡ vấn đề hiệu năng, nhưng vấn đề dependency bị ẩn vẫn còn nguyên.

## Bẫy phỏng vấn

### "Truyền tham số vào @StateObject qua init thì khi tham số đổi, view model sẽ cập nhật theo?"

**Dễ trả lời sai:** Viết `_viewModel = StateObject(wrappedValue: DetailViewModel(id: id))` và tin rằng khi parent truyền `id` mới thì view model mới được tạo.

**Nên trả lời:** Autoclosure của `StateObject` chỉ được đánh giá lần đầu cho mỗi identity của view; các lần init sau giá trị mới bị bỏ qua, nên view vẫn hiển thị dữ liệu của `id` cũ. Muốn tạo lại view model, hãy đổi identity bằng `.id(id)`; muốn giữ view model nhưng reload dữ liệu, dùng `.task(id: id) { await viewModel.load(id) }`.

### "Với @Observable, @State var model = Model() thì Model chỉ được init một lần?"

**Dễ trả lời sai:** Cho rằng `@State` với class `@Observable` hành xử y hệt `@StateObject`, nên initializer của model chỉ chạy một lần.

**Nên trả lời:** SwiftUI chỉ giữ instance đầu tiên, nhưng biểu thức khởi tạo `Model()` vẫn được đánh giá mỗi lần view struct bị init lại, rồi instance thừa bị bỏ đi. Nếu `init` của model có side effect (gọi network, đăng ký observer, log), các side effect đó lặp lại. Giữ `init` nhẹ và đưa việc load vào `.task`, hoặc tạo model ở tầng trên rồi truyền xuống.

### "Quên .environmentObject() thì compiler sẽ báo lỗi?"

**Dễ trả lời sai:** Nghĩ rằng thiếu object trong environment là lỗi compile, hoặc view sẽ nhận một giá trị mặc định rỗng.

**Nên trả lời:** `@EnvironmentObject` được resolve lúc runtime; nếu không ancestor nào inject object đó, app crash khi view đọc nó (thường gặp ở preview, sheet dựng từ UIKit, hoặc màn mới bị gắn vào cây khác). `@Environment(Model.self)` từ iOS 17 cũng crash nếu thiếu, trừ khi khai báo optional: `@Environment(Model.self) private var model: Model?`. Đây là lý do nên inject ở root và có preview dựng đủ dependency.

## Bài tập

Xây dựng parent `ShoppingCartView` với `@State var items: [CartItem]`. Tạo child `CartItemRow` nhận `@Binding var item: CartItem` để toggle `isSelected`. Thêm `@StateObject var viewModel = CartViewModel()` trong parent. Navigate sang detail screen và quay lại — xác nhận `@StateObject` KHÔNG bị tái tạo bằng cách thêm `init() { print("CartViewModel init") }` vào `CartViewModel`. Giải thích điều gì xảy ra nếu dùng `@ObservedObject`.
