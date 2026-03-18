[English](./SystemDesign.md) | [Tiếng Việt](./SystemDesign.vi.md)

[← Senior Topics](./README.md)

# System Design for iOS Apps

## What To Focus On

- Feature boundaries and module ownership
- Data flow from API to storage to UI
- Offline and caching requirements
- Reliability, observability, and release risk

## A Good Senior Answer

Start from the product requirement, then explain:

- main components
- dependencies between them
- where state lives
- how failures are handled
- what you would defer for a smaller first version

## Example Scenario

Design a feed app with:

- authenticated API
- local cache for recent items
- pagination
- pull to refresh
- offline read support

One possible breakdown:

- `FeedAPIClient` for transport
- `FeedRepository` for mapping and cache coordination
- `FeedStore` for persistence
- `FeedViewModel` or reducer for screen state
- `FeedCoordinator` for navigation

## Practice Questions

- How do you split modules in a growing app?
- What would you simplify for a two-engineer team?

## Senior Take

System design answers are not about drawing the most boxes. They are about showing judgment: which complexity is justified now, which is deferred, and how the design stays operable as the product grows.

## Exercise

Sketch a notification inbox feature. Include sync strategy, read/unread updates, pagination, and push-notification entry points. Then explain which parts you would deliberately avoid building in version 1.
