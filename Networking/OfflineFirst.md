[English](./OfflineFirst.md) | [Tiếng Việt](./OfflineFirst.vi.md)

[← Networking](./README.md)

# Offline-First Design

## Key Idea

Show cached data immediately, fetch updates in the background, and handle the no-network case gracefully instead of blocking the UI.

## Pattern

```text
1. Load from cache → show immediately
2. Fetch from network in background
3. Update UI when fresh data arrives
4. Handle network failure silently (or with a non-blocking banner)
```

## What To Review

- `NWPathMonitor` — observe network reachability
- Optimistic UI — apply changes locally before server confirms
- Sync queue — queue writes when offline, flush when online
- Conflict resolution — last-write-wins, server-wins, or merge

## Practice Questions

- If the API is slow or unstable, how would you design the data flow?

## Senior Take

Offline-first is a UX decision before it is a technical one. Define what "offline" means for each feature: read-only cache? Allow writes? Show staleness indicators? Get product alignment before building the sync layer.

## Exercise

Design an offline-first feed screen in pseudocode/comments: (1) load from cache → show immediately, (2) fetch from network in background → merge and refresh UI, (3) on network error → keep cached data + show non-blocking "Last updated X" banner. Identify which layer owns cache reads/writes, which layer decides to show the stale banner, and what happens to queued writes if the user reinstalls the app.
