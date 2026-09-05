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
addChild(hostingVC)
view.addSubview(hostingVC.view)
```

## Khi nào nên dùng

- UIKit: khi cần chức năng chưa có trong SwiftUI (gesture phức tạp, custom drawing, camera, map nâng cao)
- Hosting Controller: khi migrate dần app UIKit sang SwiftUI

## Câu hỏi luyện tập

- Tại sao cần một Coordinator khi wrap UIColorPickerViewController bằng UIViewControllerRepresentable để truyền UIColor được chọn về qua @Binding<Color>, và lifecycle của nó so với Representable ra sao?

## Góc nhìn Senior

Interop thêm độ phức tạp. Ưu tiên native SwiftUI khi có thể. Khi wrap UIKit, giữ `Representable` gọn nhẹ — đưa logic vào view model hoặc coordinator, không phải `makeUIView`.

## Bài tập

Wrap `UIColorPickerViewController` dùng `UIViewControllerRepresentable`. Dùng `Coordinator` conform `UIColorPickerViewControllerDelegate` để truyền `UIColor` được chọn về SwiftUI qua `@Binding<Color>`. Dismiss picker sau khi chọn. Giải thích trong comment tại sao cần Coordinator và lifecycle của nó so với Representable.
