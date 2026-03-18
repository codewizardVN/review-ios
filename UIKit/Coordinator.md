[English](./Coordinator.md) | [Tiếng Việt](./Coordinator.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Coordinator and Router

## Key Idea

Navigation is application flow, not view rendering. Coordinator or router patterns keep screens from owning too much knowledge about the rest of the app.

## What To Review

- Root coordinator vs child coordinator
- How screens communicate navigation intent upward
- Deep links entering existing flows
- Ownership and lifetime of coordinators

## Practice Questions

- When should a screen trigger navigation directly?
- Who should respond to a deep link that opens a nested flow?

## Senior Take

Coordinator patterns are useful when navigation complexity is real. If there is only one simple flow, adding layers may not pay off. The key is matching indirection to product complexity.

## Exercise

Take a checkout flow with cart, shipping, payment, and confirmation screens. Sketch a root coordinator plus one child coordinator. Then explain where deep link handling should enter that flow.
