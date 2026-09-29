[English](./AppSizeOptimization.md) | [Tiếng Việt](./AppSizeOptimization.vi.md)

[← Performance](./README.md)

# App Size Optimization

## Key Idea

App size affects install conversion, cellular download limits, and update friction. Optimization happens at the asset, binary, and delivery-mechanism level, not just "compress the images."

## What To Review

- App thinning — the App Store builds and serves each device a variant containing only what that device needs (e.g. only @3x images for an @3x iPhone). The main mechanism is slicing driven by the `Asset Catalog`; On-Demand Resources are also part of app thinning
- On-Demand Resources (ODR) — tag assets to download after install instead of bundling them in the initial download (e.g., game levels, rarely-used feature assets). At WWDC25 Apple called ODR a legacy technology that will be deprecated and recommended moving to Background Assets (see the answer below)
- Asset catalogs vs loose images — images in a catalog are sliced per device and compressed/optimized by Xcode at build time (with compression options, including GPU/ASTC compression for textures); loose images in the bundle are downloaded by every device
- Dead code stripping — the linker (`DEAD_CODE_STRIPPING`) only removes functions/data that nothing in your binary references; it can't remove Obj-C methods (called dynamically), localizations, resources or unused SDK modules — those you must audit and delete yourself
- Static vs dynamic frameworks — each dynamic framework is its own Mach-O binary: extra load-time work for dyld, fixed per-file overhead (headers, signature, page alignment), and it can't be dead-stripped based on what the app uses. (Since Swift 5's ABI stability, the Swift runtime ships in iOS 12.2+, so it's no longer copied into the app.) Static linking reduces launch time and enables dead stripping, which suits small internal modules well
- Dependency audit — a single heavy SDK (analytics, ad network) can add tens of MBs; know what's actually being used vs installed
- Measuring size — the App Thinning Size Report (generated when you export an archive from the Organizer with App Thinning "All compatible device variants") gives the download size (compressed) and install size (uncompressed) of each variant; the build's file sizes in App Store Connect give the real per-device numbers. To see which parts are heavy, open the `.app` inside a thinned IPA and look at the size of the executable, the `Frameworks/` folder, `Assets.car` and resource bundles, and enable the Write Link Map File build setting to see which modules/symbols take space in the executable

## Practice Questions

- Why can adding a single CocoaPod increase both binary size and app launch time?
- When would you use On-Demand Resources instead of bundling everything upfront?

## Senior Take

App size is a cross-cutting cost, not a one-time cleanup task — every new dependency, every unused localization, every uncompressed asset compounds. The senior-level answer isn't "run a size report once before release," it's having a size budget tracked in CI (fail the build if binary size regresses beyond a threshold) so growth is caught per-PR instead of discovered at submission time.

## Practice Question Answers

### Why can adding a single CocoaPod increase both binary size and app launch time?

Because a pod doesn't add just the code you call: it brings the whole library, its transitive dependencies, resource bundles, and — if the Podfile uses `use_frameworks!` — a dynamic framework that dyld must load on every app launch.

On binary size:

- Transitive dependencies: one ad or analytics SDK can pull in several other pods (check `Podfile.lock`).
- The `-ObjC` linker flag (CocoaPods often adds it to `OTHER_LDFLAGS`) forces the linker to load every object file containing Obj-C classes/categories from static libraries, including unused ones, so dead stripping can't remove them.
- A dynamic framework can't be dead-stripped based on what the app uses: the linker doesn't know which public symbols the app needs, so it keeps them all.
- The SDK's resource bundles (images, models, localizations) are copied into the app as-is.

On launch time:

- Each dynamic framework adds work for dyld: mapping the file, verifying its signature, fixing up pointers, registering Obj-C classes.
- Many SDKs run code in `+load`, static initializers, or require initialization in `didFinishLaunching` (swizzling, reading config, network calls).

How to reduce it: link statically (`use_frameworks! :linkage => :static` or drop `use_frameworks!`), use only the subspecs you need, initialize SDKs lazily after the first frame, and re-measure with the App Thinning Size Report and the App Launch template. (Note: CocoaPods has moved into maintenance mode and new projects usually use Swift Package Manager, but the same principles — transitive dependencies, static vs dynamic, `-ObjC`, resource bundles — apply.) Trade-off: if the same module is statically linked into both the app and its extensions, each binary gets its own copy; then a shared dynamic framework or mergeable libraries (Xcode 15+) make more sense.

### When would you use On-Demand Resources instead of bundling everything upfront?

Use ODR when assets are large and only some users need them, or they're only needed after a certain point: later game levels, voice/language packs, tutorial videos, content for rarely-used features. How it works: you tag assets in Xcode, the App Store hosts them separately from the main install, and at runtime the app requests them with `NSBundleResourceRequest(tags:)` and then `beginAccessingResources`. A tag can be Initial Install (downloaded with the app), Prefetched (downloaded right after install), or downloaded only on request. When the device is low on storage, the system may purge ODR resources that are no longer in use.

Don't use it when:

- The asset is needed on first launch or must work offline (e.g. the user opens the app for the first time on a plane).
- The asset is small, so the size benefit isn't worth the complexity.
- The content must update without an app release: ODR is tied to each build, so changing it means submitting a new version — use your own CDN instead.

Trade-off: you must design loading, error and retry states for every screen that uses ODR. Also, at WWDC25 (the session "Discover Apple-Hosted Background Assets") Apple called ODR a "legacy technology" that will be deprecated and recommended that apps using ODR start migrating to Background Assets; at that point Apple had not announced a specific removal timeline (check the latest SDK release notes). The Background Assets framework has existed since iOS 16 (with you hosting the assets), while Apple-hosted asset packs — the App Store hosts the asset packs for you, and you can update assets without shipping a new app version — are new in iOS 26. For new projects, choose Background Assets over ODR.

## Interview Traps

### "The archive/IPA is 150MB, so users have to download 150MB?"

**Common wrong answer:** The archive or universal IPA size is what users download.

**Better answer:** The archive contains every variant; users receive a build thinned for their device, and compressed. Distinguish download size (the compressed build, compared against the cellular download limit) from install size (space used after decompression on the device). For real numbers, export with App Thinning "All compatible device variants" to get the App Thinning Size Report, or check the build's file sizes in App Store Connect.

### "Enable bitcode so the App Store optimizes size for us?"

**Common wrong answer:** Bitcode lets Apple recompile the app and make it smaller.

**Better answer:** That's outdated: bitcode was deprecated in Xcode 14 and the App Store no longer accepts bitcode for iOS. Size optimization is now entirely on your side: enable Dead Code Stripping, strip symbols in release, consider the `-Osize` optimization level for Swift (trading a little speed), remove unused assets and localizations, audit dependencies.

### "Switching every framework to static always makes the app smaller?"

**Common wrong answer:** Static linking always reduces both launch time and size, so make everything static.

**Better answer:** Static linking reduces dyld work and allows dead stripping, but if a module is linked into the app and several extensions (widget, notification service, share extension), each binary contains its own copy, and total size can grow. In that case a shared dynamic framework is smaller. Mergeable libraries (Xcode 15+) are the compromise: dynamic in debug for fast builds, merged into the binary in release.

## Exercise

Your app's install size grew from 45MB to 78MB over two release cycles and marketing is asking why conversion dropped. Use the App Thinning Size Report (or the build's file sizes in App Store Connect) to compare the two builds, then split the growth into executable, frameworks and resources by inspecting the thinned `.app` contents and the link map. Write the investigation steps you'd take to find the top 3 contributors, and propose one fix for each category (e.g., a dynamic framework you could statically link, an asset you could download later with Background Assets (or ODR for older apps), a dependency you could remove or replace).
