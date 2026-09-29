[English](./UIKitInterop.md) | [Tiếng Việt](./UIKitInterop.vi.md)

[← SwiftUI](./README.md)

# UIKit Interoperability

## Two Directions

### SwiftUI → UIKit: `UIViewRepresentable` / `UIViewControllerRepresentable`

Wrap a UIKit component for use inside a SwiftUI view hierarchy.

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

Embed a SwiftUI view inside a UIKit view controller hierarchy.

```swift
let hostingVC = UIHostingController(rootView: FeedView())
addChild(hostingVC)                          // 1. add as a child VC
view.addSubview(hostingVC.view)              // 2. add its view to the hierarchy
hostingVC.view.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([                // 3. lay the view out
    hostingVC.view.topAnchor.constraint(equalTo: view.topAnchor),
    hostingVC.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
    hostingVC.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
    hostingVC.view.trailingAnchor.constraint(equalTo: view.trailingAnchor)
])
hostingVC.didMove(toParent: self)            // 4. tell the child it is attached
```

This is UIKit's standard containment sequence: `addChild` → add the view → layout → `didMove(toParent:)`. To remove it, do the reverse: `willMove(toParent: nil)` → `view.removeFromSuperview()` → `removeFromParent()`.

## When to Use

- UIKit (via Representable): when you need functionality SwiftUI doesn't have or doesn't cover well enough — e.g. camera (`AVCaptureVideoPreviewLayer`), some system view controllers, advanced text editing, or an existing UIKit component in your codebase. Check newer SwiftUI APIs before wrapping: MapKit for SwiftUI (iOS 17) covers most map needs, and from iOS 18 `UIGestureRecognizerRepresentable` lets you use UIKit gesture recognizers directly in SwiftUI.
- Hosting Controller: when incrementally migrating an existing UIKit app to SwiftUI — write new screens in SwiftUI and embed them in UIKit navigation. For `UICollectionView`/`UITableView` cells, use `UIHostingConfiguration` (iOS 16+) instead of a hosting controller per cell.

## Practice Questions

- Why is a Coordinator needed when wrapping UIColorPickerViewController with UIViewControllerRepresentable to pass the selected UIColor back via a @Binding<Color>, and what is its lifecycle relative to the Representable?

## Senior Take

Interop adds complexity. Prefer native SwiftUI where possible. When wrapping UIKit, keep the `Representable` thin — move logic into a view model or coordinator, not into `makeUIView`.

## Practice Question Answers

### Why is a Coordinator needed when wrapping UIColorPickerViewController with UIViewControllerRepresentable to pass the selected UIColor back via a @Binding<Color>, and what is its lifecycle relative to the Representable?

A Coordinator is needed because `UIColorPickerViewController` reports results through a delegate, and the delegate must be a stable object — specifically an `NSObject` subclass, because `UIColorPickerViewControllerDelegate` is an Objective-C protocol (inheriting `NSObjectProtocol`) — something the Representable struct cannot be.

The Representable is a value type that SwiftUI recreates whenever the parent re-renders; it can't serve as a class-type delegate, and even if it could, the instance would disappear right after. UIKit holds delegates `weak`, so something must keep the delegate object alive. SwiftUI does that: it calls `makeCoordinator()` once, before `makeUIViewController`, and keeps the Coordinator for as long as the view controller is in the tree; when the view is removed, `static func dismantleUIViewController(_:coordinator:)` is called (the place to clean up, e.g. remove delegates/observers) and afterwards the Coordinator is released along with the view controller. In other words: the Representable struct changes constantly, while the Coordinator and the view controller live together, once.

```swift
final class Coordinator: NSObject, UIColorPickerViewControllerDelegate {
    var parent: ColorPickerSheet
    init(_ parent: ColorPickerSheet) { self.parent = parent }

    func colorPickerViewController(_ picker: UIColorPickerViewController,
                                   didSelect color: UIColor, continuously: Bool) {
        parent.selection = Color(uiColor: color)
        if !continuously { parent.isPresented = false } // final pick (not mid-drag)
    }

    func colorPickerViewControllerDidFinish(_ picker: UIColorPickerViewController) {
        parent.isPresented = false // user tapped the picker's close button
    }
}
// inside ColorPickerSheet:
func makeCoordinator() -> Coordinator { Coordinator(self) }
func updateUIViewController(_ vc: UIColorPickerViewController, context: Context) {
    context.coordinator.parent = self // keep the latest binding
}
```

Trade-off: SwiftUI has had a native `ColorPicker` since iOS 14; only wrap `UIColorPickerViewController` when you need behaviour `ColorPicker` doesn't offer.

## Interview Traps

### "Storing parent in the Coordinator at makeCoordinator time is enough?"

**Common wrong answer:** Assuming `Coordinator(self)` in `makeCoordinator()` holds a "live" reference to the Representable, so bindings and closures are always current.

**Better answer:** `parent` is a copy of the struct as it was when the Coordinator was created. When SwiftUI recreates the Representable with new bindings or closures (e.g. an `onSelect` capturing new state), the Coordinator still holds the old copy. Bindings usually still point at the right state source, but closures and plain values go stale. The safe approach is to update `context.coordinator.parent = self` in `updateUIViewController`.

### "updateUIViewController runs only once after makeUIViewController?"

**Common wrong answer:** Treating `updateUIViewController` as a second setup step, so reassigning every property or changing SwiftUI state there is fine.

**Better answer:** It is called whenever any input of the Representable changes, possibly many times. Code there must be idempotent: compare before assigning (`if vc.selectedColor != newColor`) so you don't reset the user's in-progress selection. Never mutate `@State`/`@Binding` synchronously inside it — SwiftUI warns "Modifying state during view update" and it can create an endless update loop.

### "Embedding a UIHostingController just needs addChild and addSubview?"

**Common wrong answer:** Writing only the three lines `UIHostingController(rootView:)`, `addChild`, `addSubview` and calling it done.

**Better answer:** Proper view controller containment also requires `hostingVC.didMove(toParent: self)` after adding the subview and laying it out, and you must set constraints or a frame for `hostingVC.view` (see the full example in the UIKit → SwiftUI section above), otherwise the child is never told it has been attached and sizing can be wrong. When the SwiftUI content changes size, use `sizingOptions = .intrinsicContentSize` (iOS 16+) so the hosting controller updates its intrinsic size. Also keep a reference to the hosting controller and update `rootView` instead of creating a new one each time.

## Exercise

Wrap `UIColorPickerViewController` using `UIViewControllerRepresentable`. Use a `Coordinator` conforming to `UIColorPickerViewControllerDelegate` to pass the selected `UIColor` back to SwiftUI via a `@Binding<Color>`. Dismiss the picker after selection. Explain in a comment why a `Coordinator` is needed here and what its lifecycle is relative to the `Representable`.
