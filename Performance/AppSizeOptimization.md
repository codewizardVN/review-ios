[English](./AppSizeOptimization.md) | [Tiếng Việt](./AppSizeOptimization.vi.md)

[← Performance](./README.md)

# App Size Optimization

## Key Idea

App size affects install conversion, cellular download limits, and update friction. Optimization happens at the asset, binary, and delivery-mechanism level, not just "compress the images."

## What To Review

- App thinning — App Store Connect builds and serves a variant matched to the device (only the needed image resolutions/architectures), driven by `Asset Catalog` and on-demand resources
- On-Demand Resources (ODR) — tag assets to download after install instead of bundling them in the initial download (e.g., game levels, rarely-used feature assets)
- Asset catalogs vs loose images — catalogs enable slicing and better compression (HEIC, ASTC for textures)
- Dead code stripping — unused Swift/Obj-C code, unused localizations, unused third-party SDK modules
- Static vs dynamic frameworks — dynamic frameworks add load-time cost and duplicate Swift runtime overhead per framework; static linking reduces launch time and binary duplication for small internal modules
- Dependency audit — a single heavy SDK (analytics, ad network) can add tens of MBs; know what's actually being used vs installed
- `App Size Report` in Xcode Organizer — breaks down install size by component (executable, frameworks, resources, assets)

## Practice Questions

- Why can adding a single CocoaPod increase both binary size and app launch time?
- When would you use On-Demand Resources instead of bundling everything upfront?

## Senior Take

App size is a cross-cutting cost, not a one-time cleanup task — every new dependency, every unused localization, every uncompressed asset compounds. The senior-level answer isn't "run a size report once before release," it's having a size budget tracked in CI (fail the build if binary size regresses beyond a threshold) so growth is caught per-PR instead of discovered at submission time.

## Exercise

Your app's install size grew from 45MB to 78MB over two release cycles and marketing is asking why conversion dropped. Using the Xcode Organizer size report categories (executable, frameworks, resources), write the investigation steps you'd take to find the top 3 contributors, and propose one fix for each category (e.g., a dynamic framework you could statically link, an asset you could move to ODR, a dependency you could remove or replace).
