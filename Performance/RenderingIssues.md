[English](./RenderingIssues.md) | [Tiếng Việt](./RenderingIssues.vi.md)

[← Performance](./README.md)

# Rendering Performance

## Frame Budget

At 60fps, each frame has ~16.7ms. At 120fps (ProMotion), ~8.3ms. Within that time both the app's work on the main thread (event handling, layout, drawing, commit) and the render server's work on the GPU (compositing the layers) must finish. If either stage exceeds the budget, the frame is late (a hitch) and the screen shows the previous frame again.

## Common Issues

| Issue | Cause | Fix |
| --- | --- | --- |
| Offscreen rendering | Clipping content/sublayers with `cornerRadius` + `masksToBounds`, using a `mask`, shadows without `shadowPath`, group opacity | Set `shadowPath` for shadows; only enable `masksToBounds` when content really must be clipped (if only the background needs rounding, `cornerRadius` alone is enough); for images, round the corners when decoding |
| Blending | Transparent views stacked on each other, the GPU must blend every pixel | Use an opaque `backgroundColor` and `alpha = 1` where possible (`isOpaque = true` is only a drawing hint; it doesn't make the view opaque by itself) |
| Image decoding on main thread | Large image loaded synchronously | Decode in background, display on main |
| Expensive `body` computation | Heavy logic in SwiftUI `body` | Extract to ViewModel, memoize |

## Detection Tools

- **Instruments → Animation Hitches** — shows which frames are late, by how much, and whether it's a commit hitch or a render hitch (this is the main tool today; the colour-overlay options of the old Core Animation instrument moved into Xcode/Simulator)
- **Color Blended Layers** — highlights transparency cost (green = no blending, red = blending)
- **Color Offscreen-Rendered** — highlights layers rendered offscreen (yellow)
- Both overlays are in the Simulator's Debug menu, or on a real device: Xcode → Debug → View Debugging → Rendering

## Practice Questions

- Why does the UI drop frames?
- Why can image loading make an app feel janky?

## Senior Take

Answer with a process: observe the symptom, open Instruments, isolate the layer causing the frame drop, measure the actual cost before optimizing. Never guess.

## Practice Question Answers

### Why does the UI drop frames?

The UI drops a frame when a frame isn't finished before the display's deadline (about 16.7ms at 60Hz, 8.3ms at 120Hz ProMotion), so the screen has to show the previous frame again — the user sees a stutter, which Apple calls a hitch. Each frame goes through two main stages:

- **Commit in the app, on the main thread:** handle events, run your code, layout (Auto Layout, `layoutSubviews`, SwiftUI `body`), drawing (`draw(_:)`), image decoding, then send the layer tree to the render server. If the main thread is busy (decoding JSON, synchronous I/O, complex layout) the commit is late — a commit hitch.
- **Render in the render server (a separate process, using the GPU):** composite the layers into the final image. If the layer tree is too heavy — many offscreen passes from masks or `cornerRadius` + `masksToBounds`, shadows without `shadowPath`, many overlapping transparent layers (blending), blur — the GPU can't keep up, a render hitch.

Telling these apart matters because the fixes differ: commit hitches are fixed by doing less on the main thread; render hitches by simplifying layers. Use the Animation Hitches template in Instruments to see which frames are late and at which stage, then Time Profiler or Color Offscreen-Rendered / Color Blended Layers to find the specific cause. Trade-off: don't reflexively remove every shadow and rounded corner; only optimize the layers that actually appear in late frames.

### Why can image loading make an app feel janky?

Because an image must be decoded from compressed data (JPEG/PNG/HEIC) into a bitmap before it can be shown, and by default this happens lazily on the main thread exactly when the image is first rendered. `UIImage(named:)` or `UIImage(data:)` only create an object wrapping the compressed data; when it's assigned to a `UIImageView` and Core Animation commits, the image is decoded — on the main thread, within that very frame. A 12MP image (4032×3024) decodes into a bitmap of about 4032 × 3024 × 4 bytes ≈ 48MB and can take tens of ms, blowing the frame budget. In a list, every new cell that appears is another decode, so scrolling stutters and memory spikes (the system may kill the app for running out of memory).

How to fix it:

- Downsample to the displayed size with ImageIO (`CGImageSourceCreateThumbnailAtIndex`) or `UIImage.preparingThumbnail(of:)` (iOS 15+).
- Pre-decode in the background with `byPreparingForDisplay()` / `prepareForDisplay(completionHandler:)` (iOS 15+), then assign on main.
- Cache decoded images (e.g. `NSCache`) and cancel requests when a cell is reused (in `prepareForReuse`).
- Never read files or the network synchronously on main.

Trade-off: decoded bitmaps use far more memory than compressed data, so the cache needs limits. SwiftUI's `AsyncImage` is convenient but doesn't let you downsample and has no cache of decoded images (it only relies on `URLSession`'s HTTP cache), so it's often not enough for large image lists.

## Interview Traps

### "`cornerRadius` always causes offscreen rendering, right?"

**Common wrong answer:** Setting `cornerRadius` always triggers offscreen rendering, so avoid rounding corners with layers.

**Better answer:** `cornerRadius` alone only rounds the layer's background and border, which the GPU draws directly without an offscreen pass. Offscreen passes usually appear when content and sublayers must be clipped (`masksToBounds = true` with many sublayers), when using a `mask`, shadows without a `shadowPath`, or group opacity. Don't assert this from memory — turn on Color Offscreen-Rendered and check.

### "To fix `CardView`, just keep `masksToBounds` and add `shadowPath` on the same layer?"

**Common wrong answer:** Put the shadow, `shadowPath` and `masksToBounds = true` on the same layer and you're done.

**Better answer:** `masksToBounds` clips everything outside the bounds, including the shadow, so the two can't live on the same layer. If the content (e.g. an image) must be clipped to the rounded corners, split it into two views: an outer container with the shadow + `shadowPath`, and an inner view with `cornerRadius` + `masksToBounds`. And `shadowPath` must be updated in `layoutSubviews` when the bounds change, otherwise the shadow has the wrong size.

```swift
layer.shadowPath = UIBezierPath(roundedRect: bounds, cornerRadius: 12).cgPath
```

### "It runs at a smooth 60fps in the simulator, so it's fine?"

**Common wrong answer:** Measuring FPS in the simulator or a debug build is enough to conclude anything about rendering.

**Better answer:** The simulator renders using the Mac's GPU and CPU, so it doesn't reflect a real device; debug builds are also slower than release. FPS is a poor metric too, since low FPS is normal when the screen is idle. Apple uses the hitch time ratio (milliseconds of delay per second of animation/scrolling). Measure on a real device, in a release build, preferably on the weakest device you support, and remember ProMotion only gives about 8ms per frame.

## Exercise

Take a `CardView` that uses `cornerRadius` with `masksToBounds` and a `shadow`. Enable "Color Offscreen-Rendered" (the Simulator's Debug menu, or Xcode → Debug → View Debugging → Rendering on a device) and confirm yellow highlighting appears. Fix it by setting an explicit `shadowPath` (updated in `layoutSubviews`) and removing `masksToBounds`; if the inner content still needs clipping to the rounded corners, split it into a container with the shadow and a child view with `cornerRadius` + `masksToBounds`, as in Interview Traps. Verify the yellow disappears, then re-measure with Animation Hitches on a real device.
