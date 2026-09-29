[English](./Modularization.md) | [Tiếng Việt](./Modularization.vi.md)

[← Architecture](./README.md)

# Modularization

## Key Idea

Split the app into separate Swift packages or targets to reduce coupling, speed up builds, and enforce boundaries between features.

## Common Split Strategies

- **By layer** — `CoreDomain`, `DataLayer`, `UIComponents`
- **By feature** — `FeedFeature`, `ProfileFeature`, `AuthFeature`
- **Hybrid** — feature modules + shared core modules

## Benefits

- Faster incremental builds (only rebuild changed modules)
- Hard boundaries prevent accidental cross-feature coupling
- Teams can own modules independently

## Practice Questions

- What criteria would you use to split the first module?
- Should module boundaries be drawn by feature or by layer?

## Senior Take

Start modularizing when build times hurt or when team ownership becomes unclear — not as a default from day one. Over-modularization adds dependency management overhead without proportional benefit in small codebases.

## Practice Question Answers

### What criteria would you use to split the first module?

The first module should be a part with a clear boundary, few dependencies on the rest of the app, and a measurable pain it solves, usually a foundational module like `Networking` or `DesignSystem`.

Concrete criteria:

- **A real pain exists**: slow builds (check Xcode's Build Timeline or build timing reports), repeated merge conflicts in the same area, or unclear ownership between teams. Don't split just because "big apps should be modular".
- **It's a leaf in the dependency graph**: a module can't depend back on the app target, so extract bottom-up. Code that only uses Foundation and doesn't call into any feature is the best candidate.
- **Stable API and low coupling**: if pulling the module out drags half the app with it, or it touches lots of singletons, it's not time yet.
- **Widely reused**: networking, design system, and analytics are used by every feature, so extracting them pays off immediately.

Splitting the first module is also a test: you are forced to declare `public` API explicitly, and hidden dependencies (singletons, shared extensions) surface right away. Costs to account for: setting up a local Swift package, dealing with access control, and resources that must be accessed via `Bundle.module` instead of `Bundle.main`.

### Should module boundaries be drawn by feature or by layer?

Usually combine them: vertical feature modules on top, a few horizontal core modules below such as `Networking`, `DesignSystem`, `Analytics`.

If you split only by layer, for example every ViewModel in a `Presentation` module and every repository in `DataLayer`, then changing one feature touches every module. You get no build isolation, and no team owns a whole module. Splitting by feature, like `CartFeature` or `ProfileFeature`, lets you build and test a feature on its own and assign clear ownership.

Key rule: feature modules don't import each other directly. When `Cart` needs to open a product screen, use a small interface module (e.g. `ProductCatalogInterface` holding protocols and models), or let the app target connect the two features through a closure or protocol. Inside a feature module, layers can just be folders, or sub-targets if the feature is large enough.

Splitting by layer still has its place: for a small app, two modules `Domain` and `Data` are a cheap way to let the compiler enforce Clean Architecture's dependency rule.

## Interview Traps

### "More modules always means faster builds?"

**Common wrong answer:** "Yes, each module builds separately, so it's always faster."

**Better answer:** Incremental builds are only faster when the change is in a leaf module. Editing a core module that every feature depends on still rebuilds everything, especially when public API changes. Too many tiny modules also add build-planning and link time. If you use many dynamic frameworks, app launch gets slower because dyld loads each one; default (automatic) SPM library products are usually linked statically, and Xcode 15 added mergeable libraries to reduce this problem.

### "`Cart` needs `ProductCatalog`, and `ProductCatalog` needs an 'Add to cart' button, so let the two modules import each other?"

**Common wrong answer:** Allow the circular import, or dump everything shared into a `Common`/`Utils` module.

**Better answer:** SwiftPM doesn't allow circular dependencies, so the first option won't build. The second creates a "god module" every feature depends on, so any change rebuilds everything. The right move is to invert the dependency: extract an interface module holding only protocols and models, or have the app target inject a closure like `onAddToCart` into `ProductCatalog`. The two features only know abstractions, not each other.

### "To share code between modules in the same package, does it have to be `public`?"

**Common wrong answer:** "It has to be `public`, since `internal` is only visible within one module." The result is internal details exposed to every client.

**Better answer:** Since Swift 5.9 there is the `package` access level (SE-0386): the symbol is visible to every module in the same Swift package but not outside it. Separately, `@testable import` lets tests reach `internal` symbols, but only when the module is built with testability enabled (the Debug default), so don't rely on it for production code.

## Exercise

Design a module map (ASCII diagram in comments) for an e-commerce app with: Auth, ProductCatalog, Cart, Orders, UserProfile. Identify which are feature modules vs shared core modules (DesignSystem, Networking, Analytics). Draw dependency arrows. Mark which dependencies would create a circular dependency. Explain which specific pain point — build time, coupling, or ownership — would trigger you to split the first module.
