[English](./Navigation.md) | [Tiếng Việt](./Navigation.vi.md)

[← SwiftUI](./README.vi.md)

# Navigation

## Nội dung ôn tập

- `NavigationStack` — thay thế `NavigationView` (đã deprecated) từ iOS 16+; với layout nhiều cột (iPad, Mac) dùng `NavigationSplitView`.
- `NavigationPath` — một stack type-erased (chứa được nhiều type `Hashable` khác nhau) để điều hướng bằng code: push là `append`, pop là `removeLast`. Nếu stack chỉ có một type route, một mảng typed như `[Route]` cũng dùng làm path được.
- `.navigationDestination(for:)` — ánh xạ "kiểu dữ liệu → màn hình": khi path chứa một giá trị kiểu đó, SwiftUI dựng màn tương ứng. Trigger (`NavigationLink(value:)` hoặc thay đổi path) tách khỏi destination.
- Sheet, fullScreenCover, popover — modal presentation, điều khiển bằng `Bool` (`isPresented:`) hoặc optional `Identifiable` (`item:`), không nằm trong navigation path. Trên iPhone, popover mặc định hiển thị thành sheet (từ iOS 16.4 có thể đổi bằng `.presentationCompactAdaptation(.popover)`).
- Deep linking — nhận URL bằng `.onOpenURL` (hoặc `onContinueUserActivity` cho universal link qua `NSUserActivity`), parse thành route rồi gán vào path. (`openURL` trong environment là để *mở* một URL, không phải để nhận.)

## Ví dụ

```swift
struct AppView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            FeedView()
                .navigationDestination(for: Item.self) { item in
                    ItemDetailView(item: item)
                }
        }
    }
}
```

## Câu hỏi luyện tập

- Bạn sẽ pre-populate NavigationPath của NavigationStack lúc app launch như thế nào để một deep link đi thẳng đến màn Reviews cho một item cụ thể, bỏ qua màn List và Detail?

## Góc nhìn Senior

Ưu tiên data-driven navigation (`.navigationDestination`) thay vì `NavigationLink(destination:)` inline. Cách này tách rời trigger khỏi destination và cho phép programmatic deep linking mà không cần biết toàn bộ view hierarchy.

## Đáp án câu hỏi luyện tập

### Bạn sẽ pre-populate NavigationPath của NavigationStack lúc app launch như thế nào để một deep link đi thẳng đến màn Reviews cho một item cụ thể, bỏ qua màn List và Detail?

Parse deep link thành một mảng route rồi gán cả mảng đó vào path của `NavigationStack` — ví dụ `[.detail(id), .reviews(id)]` — trước hoặc ngay khi stack hiển thị; SwiftUI sẽ dựng toàn bộ stack một lần và màn trên cùng là Reviews.

Cơ chế: `NavigationStack(path:)` coi path là nguồn sự thật. Mỗi phần tử trong path được map sang một màn thông qua `.navigationDestination(for:)` đăng ký ở root. Vì destination được quyết định bởi dữ liệu chứ không bởi `NavigationLink` nằm trong List hay Detail, bạn không cần "bấm" qua từng màn. Màn List vẫn là root, còn Detail vẫn nằm trong stack, nên nút Back từ Reviews quay về Detail như bình thường.

```swift
enum Route: Hashable { case detail(Item.ID), reviews(Item.ID) }

@State private var path: [Route] = []

NavigationStack(path: $path) {
    ListView()
        .navigationDestination(for: Route.self) { route in
            switch route {
            case .detail(let id): ItemDetailView(itemID: id)
            case .reviews(let id): ReviewsView(itemID: id)
            }
        }
}
.onOpenURL { url in
    if let id = DeepLink.itemID(from: url) { path = [.detail(id), .reviews(id)] } // helper tự viết
}
```

`onOpenURL` cũng được gọi khi app cold launch từ URL. Nên truyền ID thay vì cả model để mỗi màn tự load dữ liệu. Trade-off: mảng typed `[Route]` dễ kiểm tra và test hơn `NavigationPath`; chỉ dùng `NavigationPath` khi stack thật sự chứa nhiều type khác nhau. Nút "Go to Root" chỉ cần `path.removeAll()`.

## Bẫy phỏng vấn

### "Đặt .navigationDestination ở đâu cũng được, miễn là nằm trong NavigationStack?"

**Dễ trả lời sai:** Gắn `.navigationDestination(for:)` lên từng row bên trong `List` hoặc `LazyVStack`, gần với chỗ `NavigationLink(value:)`.

**Nên trả lời:** Destination phải được đăng ký ở view luôn tồn tại trong stack, thường là root, không nằm trong lazy container. Row trong lazy container có thể chưa được tạo hoặc đã bị hủy, nên SwiftUI không tìm thấy destination và bỏ qua lần navigate, kèm cảnh báo trong console. Với deep link, đây là lỗi hay gặp nhất: path đã đúng nhưng không màn nào hiện ra vì destination của type đó chưa được đăng ký.

### "NavigationLink(destination:) chỉ tạo màn đích khi user bấm vào?"

**Dễ trả lời sai:** Nghĩ rằng destination view chỉ được khởi tạo lúc navigate, nên đặt việc nặng trong `init` của màn đích là vô hại.

**Nên trả lời:** Với `NavigationLink(destination:)`, struct của màn đích được init ngay khi `body` chứa link được đánh giá — mỗi row được dựng (và dựng lại mỗi lần re-render) là thêm một lần init màn Detail, dù `body` của nó chưa chạy. `List` là lazy nên chỉ các row đang được dựng mới tốn, nhưng với `VStack` thường thì 100 row là 100 lần init. Nếu `init` tạo view model hay gọi network, chi phí đó lặp lại. `NavigationLink(value:)` + `.navigationDestination` chỉ dựng màn đích khi path thực sự chứa giá trị đó, đây là thêm một lý do để ưu tiên navigation theo dữ liệu.

### "Muốn restore navigation state sau khi app bị kill thì cứ lưu NavigationPath?"

**Dễ trả lời sai:** Cho rằng `NavigationPath` luôn encode được vì nó là type do Apple cung cấp.

**Nên trả lời:** `NavigationPath` chỉ encode được khi mọi phần tử bên trong đều `Codable`; thuộc tính `path.codable` trả về `nil` nếu có phần tử không phải `Codable`. Cách an toàn là dùng `enum Route: Hashable, Codable` chỉ chứa ID, lưu path (với `NavigationPath` thì encode `path.codable` — kiểu `NavigationPath.CodableRepresentation`; với `[Route]` thì encode thẳng mảng) vào `@SceneStorage` dạng `Data`, và khi restore phải xử lý trường hợp item không còn tồn tại thay vì mở màn rỗng. Lưu ý: dữ liệu scene restoration bị hệ thống xóa khi user tự vuốt tắt app trong app switcher, nên `@SceneStorage` chỉ khôi phục được khi hệ thống kill app ở background; nếu cần giữ cả trường hợp đó thì phải tự lưu ra disk.

## Bài tập

Xây dựng app 3 màn hình dùng `NavigationStack` với `NavigationPath`: List → Detail → Reviews. Thêm nút "Go to Root" trên màn Reviews xóa path bằng `path.removeLast(path.count)`. Sau đó hỗ trợ deep link: khi app launch, pre-populate `NavigationPath` để navigate thẳng đến màn Reviews cho một item cụ thể.
