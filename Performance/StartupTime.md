[English](./StartupTime.md) | [Tiếng Việt](./StartupTime.vi.md)

[← Performance](./README.md)

# Startup Time

## Two Phases

1. **Pre-main** — dylib loading, ObjC runtime initialization (`+load`, class registration)
2. **Post-main** — `application(_:didFinishLaunchingWithOptions:)`, initial view hierarchy setup

## What Slows Startup

- Too many dynamic frameworks (each adds dylib load time)
- Heavy `+load` or `static let` initializers
- Synchronous network or disk access at launch
- Complex initial view setup before first frame

## How to Measure

- Instruments → App Launch
- `DYLD_PRINT_STATISTICS=1` in scheme environment variables
- Xcode Organizer → Launch Time metrics

## Improvements

- Reduce dynamic framework count (merge small modules)
- Move expensive setup to background after first frame
- Defer non-critical initialization (`lazy var`, on-demand)
- Use pre-warming (iOS 15+) — system launches app in background before user opens it

## Senior Take

A 400ms improvement in launch time is real user value. But measure before optimizing — pre-main and post-main have different root causes and different fixes. Instrument first.

## Exercise

Enable `DYLD_PRINT_STATISTICS=1` in your scheme and record the pre-main time. Then open Instruments → App Launch and identify the three most expensive operations in post-main. Propose one concrete change to reduce each.
