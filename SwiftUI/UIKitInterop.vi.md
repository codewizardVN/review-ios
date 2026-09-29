[English](./UIKitInterop.md) | [Tiếng Việt](./UIKitInterop.vi.md)

[← SwiftUI](./README.vi.md)

# Tương tác với UIKit

## Hai hướng

### SwiftUI → UIKit: `UIViewRepresentable` / `UIViewControllerRepresentable`

Wrap UIKit component để dùng trong SwiftUI view hierarchy.

```swift
struct MapView: UIViewRepresentable {
    func makeUIView(context: Context) -> MKMapView {
        MKMapView()
    }

    func updateUIView(_ view: MKMapView, context: Context) {
        // sync SwiftUI state → UIKit view
    }
}
```

### UIKit → SwiftUI: `UIHostingController`

Nhúng SwiftUI view vào UIKit view controller hierarchy.

```swift
let hostingVC = UIHostingController(rootView: FeedView())
addChild(hostingVC)                          // 1. thêm làm child VC
view.addSubview(hostingVC.view)              // 2. thêm view vào hierarchy
hostingVC.view.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([                // 3. đặt layout cho view
    hostingVC.view.topAnchor.constraint(equalTo: view.topAnchor),
    hostingVC.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
    hostingVC.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
    hostingVC.view.trailingAnchor.constraint(equalTo: view.trailingAnchor)
])
hostingVC.didMove(toParent: self)            // 4. báo cho child biết đã gắn xong
```

Đây là trình tự containment chuẩn của UIKit: `addChild` → add view → layout → `didMove(toParent:)`. Khi gỡ ra thì làm ngược lại: `willMove(toParent: nil)` → `view.removeFromSuperview()` → `removeFromParent()`.

## Khi nào nên dùng

- UIKit (qua Representable): khi cần chức năng chưa có hoặc chưa đủ trong SwiftUI — ví dụ camera (`AVCaptureVideoPreviewLayer`), một số view controller của hệ thống, text editing nâng cao, hay một component UIKit có sẵn trong codebase. Kiểm tra API SwiftUI mới trước khi wrap: MapKit cho SwiftUI (iOS 17) đã phủ phần lớn nhu cầu map, và từ iOS 18 có `UIGestureRecognizerRepresentable` để dùng gesture recognizer của UIKit trực tiếp trong SwiftUI.
- Hosting Controller: khi migrate dần app UIKit sang SwiftUI — màn mới viết bằng SwiftUI rồi nhúng vào navigation UIKit. Với cell của `UICollectionView`/`UITableView`, dùng `UIHostingConfiguration` (iOS 16+) thay vì tạo hosting controller cho từng cell.

## Câu hỏi luyện tập

- Tại sao cần một Coordinator khi wrap UIColorPickerViewController bằng UIViewControllerRepresentable để truyền UIColor được chọn về qua @Binding<Color>, và lifecycle của nó so với Representable ra sao?

## Góc nhìn Senior

Interop thêm độ phức tạp. Ưu tiên native SwiftUI khi có thể. Khi wrap UIKit, giữ `Representable` gọn nhẹ — đưa logic vào view model hoặc coordinator, không phải `makeUIView`.

## Đáp án câu hỏi luyện tập

### Tại sao cần một Coordinator khi wrap UIColorPickerViewController bằng UIViewControllerRepresentable để truyền UIColor được chọn về qua @Binding<Color>, và lifecycle của nó so với Representable ra sao?

Cần Coordinator vì `UIColorPickerViewController` báo kết quả qua delegate, và delegate phải là một object sống ổn định — cụ thể là class kế thừa `NSObject`, vì `UIColorPickerViewControllerDelegate` là protocol Objective-C (kế thừa `NSObjectProtocol`) — điều mà struct Representable không thể làm được.

Representable là value type, bị SwiftUI tạo lại mỗi khi parent re-render; nó không thể conform làm delegate kiểu class, và nếu có thì instance cũng biến mất ngay sau đó. UIKit lại giữ delegate bằng tham chiếu `weak`, nên phải có ai đó giữ object delegate sống. SwiftUI làm việc này: gọi `makeCoordinator()` một lần, trước `makeUIViewController`, và giữ Coordinator suốt thời gian view controller còn trong cây; khi view bị gỡ, `static func dismantleUIViewController(_:coordinator:)` được gọi (nơi dọn dẹp, ví dụ gỡ delegate/observer) và sau đó Coordinator được giải phóng cùng với view controller. Nói cách khác: struct Representable thay đổi liên tục, còn Coordinator và view controller thì sống cùng nhau, một lần.

```swift
final class Coordinator: NSObject, UIColorPickerViewControllerDelegate {
    var parent: ColorPickerSheet
    init(_ parent: ColorPickerSheet) { self.parent = parent }

    func colorPickerViewController(_ picker: UIColorPickerViewController,
                                   didSelect color: UIColor, continuously: Bool) {
        parent.selection = Color(uiColor: color)
        if !continuously { parent.isPresented = false } // chọn xong (không phải đang kéo)
    }

    func colorPickerViewControllerDidFinish(_ picker: UIColorPickerViewController) {
        parent.isPresented = false // user bấm nút đóng của picker
    }
}
// trong ColorPickerSheet:
func makeCoordinator() -> Coordinator { Coordinator(self) }
func updateUIViewController(_ vc: UIColorPickerViewController, context: Context) {
    context.coordinator.parent = self // giữ binding mới nhất
}
```

Trade-off: SwiftUI đã có `ColorPicker` native từ iOS 14; chỉ wrap `UIColorPickerViewController` khi cần hành vi mà `ColorPicker` không cung cấp.

## Bẫy phỏng vấn

### "Lưu parent trong Coordinator lúc makeCoordinator là đủ?"

**Dễ trả lời sai:** Cho rằng `Coordinator(self)` trong `makeCoordinator()` giữ một tham chiếu "sống" tới Representable, nên binding và closure luôn mới.

**Nên trả lời:** `parent` là bản copy của struct tại thời điểm tạo Coordinator. Khi SwiftUI tạo lại Representable với binding hoặc closure mới (ví dụ `onSelect` capture state mới), Coordinator vẫn cầm bản cũ. Binding thường vẫn trỏ đúng nguồn state, nhưng closure và giá trị thường thì bị cũ. Cách an toàn là cập nhật `context.coordinator.parent = self` trong `updateUIViewController`.

### "updateUIViewController chỉ chạy một lần sau makeUIViewController?"

**Dễ trả lời sai:** Coi `updateUIViewController` như một bước setup thứ hai, nên cứ gán lại mọi thuộc tính hoặc thay đổi SwiftUI state trong đó.

**Nên trả lời:** Nó được gọi mỗi khi bất kỳ input nào của Representable thay đổi, có thể rất nhiều lần. Code trong đó phải idempotent: so sánh trước khi gán (`if vc.selectedColor != newColor`) để không reset lựa chọn đang dở của user. Không được sửa `@State`/`@Binding` đồng bộ trong đó — SwiftUI cảnh báo "Modifying state during view update" và có thể tạo vòng lặp update vô tận.

### "Nhúng UIHostingController chỉ cần addChild và addSubview?"

**Dễ trả lời sai:** Chỉ viết ba dòng `UIHostingController(rootView:)`, `addChild`, `addSubview` và coi là xong.

**Nên trả lời:** View controller containment đầy đủ cần gọi `hostingVC.didMove(toParent: self)` sau khi add subview và đặt layout, và phải đặt constraint hoặc frame cho `hostingVC.view` (xem ví dụ đầy đủ ở phần UIKit → SwiftUI phía trên), nếu không child không được thông báo là đã gắn xong và sizing có thể sai. Khi nội dung SwiftUI thay đổi kích thước, dùng `sizingOptions = .intrinsicContentSize` (iOS 16+) để hosting controller cập nhật intrinsic size. Ngoài ra, giữ tham chiếu tới hosting controller và cập nhật `rootView` thay vì tạo mới mỗi lần.

## Bài tập

Wrap `UIColorPickerViewController` dùng `UIViewControllerRepresentable`. Dùng `Coordinator` conform `UIColorPickerViewControllerDelegate` để truyền `UIColor` được chọn về SwiftUI qua `@Binding<Color>`. Dismiss picker sau khi chọn. Giải thích trong comment tại sao cần Coordinator và lifecycle của nó so với Representable.
