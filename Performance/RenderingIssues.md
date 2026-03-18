[English](./RenderingIssues.md) | [Tiếng Việt](./RenderingIssues.vi.md)

[← Performance](./README.md)

# Rendering Performance

## Frame Budget

At 60fps, each frame has ~16ms. At 120fps (ProMotion), ~8ms. Any work on the main thread that exceeds this budget causes a dropped frame.

## Common Issues

| Issue | Cause | Fix |
| --- | --- | --- |
| Offscreen rendering | `cornerRadius` + `masksToBounds`, shadows without `shadowPath` | Set `shadowPath`, use `CAShapeLayer` |
| Blending | Transparent views composited over each other | Set `isOpaque = true`, avoid alpha where possible |
| Image decoding on main thread | Large image loaded synchronously | Decode in background, display on main |
| Expensive `body` computation | Heavy logic in SwiftUI `body` | Extract to ViewModel, memoize |

## Detection Tools

- **Core Animation instrument** — shows frame rate and offscreen rendering passes
- **Debug → Color Blended Layers** — highlights transparency cost (green = ok, red = blending)
- **Debug → Color Offscreen-Rendered** — highlights GPU offscreen passes (yellow)

## Practice Questions

- Why does the UI drop frames?
- Why can image loading make an app feel janky?

## Senior Take

Answer with a process: observe the symptom, open Instruments, isolate the layer causing the frame drop, measure the actual cost before optimizing. Never guess.

## Exercise

Take a `CardView` that uses `cornerRadius` with `masksToBounds` and a `shadow`. Enable "Color Offscreen-Rendered" in the simulator and confirm yellow highlighting appears. Fix it by setting an explicit `shadowPath` and removing `masksToBounds`. Verify the yellow disappears.
