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
- Whether module boundaries should be split by feature or by layer?

## Senior Take

Start modularizing when build times hurt or when team ownership becomes unclear — not as a default from day one. Over-modularization adds dependency management overhead without proportional benefit in small codebases.

## Exercise

Design a module map (ASCII diagram in comments) for an e-commerce app with: Auth, ProductCatalog, Cart, Orders, UserProfile. Identify which are feature modules vs shared core modules (DesignSystem, Networking, Analytics). Draw dependency arrows. Mark which dependencies would create a circular dependency. Explain which specific pain point — build time, coupling, or ownership — would trigger you to split the first module.
