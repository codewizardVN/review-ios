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

- `NWPathMonitor` (Network framework) — observes the network path status (`.satisfied`, `.unsatisfied`, interface type, whether it is expensive/constrained); use it as a signal to trigger sync or update the UI, not to gate requests (see the trap below).
- Optimistic UI — apply the change to local data and show it immediately, before the server confirms; if the server rejects it, roll back and tell the user.
- Sync queue (outbox) — store write operations in a queue persisted on disk while offline, then send them in order when the network is back.
- Conflict resolution — when both the client and the server changed the same record: last-write-wins (the latest edit wins), server-wins (the server copy always wins), or merge (combine per field or ask the user).

## Practice Questions

- If the API is slow or unstable, how would you design the data flow?

## Senior Take

Offline-first is a UX decision before it is a technical one. Define what "offline" means for each feature: read-only cache? Allow writes? Show staleness indicators? Get product alignment before building the sync layer.

## Practice Question Answers

### If the API is slow or unstable, how would you design the data flow?

I would make the local database the single source of truth for the UI, and treat the network only as something that updates the database in the background — the UI never has to wait for the API before showing something.

Read flow:
1. The screen observes data from the database (`@Query`, `NSFetchedResultsController`, or an `AsyncStream` provided by the repository) and shows whatever is there immediately.
2. The repository triggers a refresh: call the API with a reasonable timeout and retry with backoff on transient errors.
3. When fresh data arrives, the repository writes it to the database; the UI updates on its own because it is observing, with no separate callback.
4. If the refresh fails, the old data stays on screen with a non-blocking "Last updated X" banner based on `lastUpdated`.

Write flow:
- Apply the change to the database first (optimistic UI) and, in the same transaction, write a record into an outbox (sync queue) persisted on disk.
- A sync worker sends the outbox when the network is available, with an idempotency key so retries are safe, then marks it done — or rolls back and reports an error if the server rejects it.
- Have an explicit conflict policy: server-wins, versions/`ETag` to detect conflicts, or per-field merge.

Trade-off: this design is far more complex than "call the API, then display" — it needs a local schema, migrations, sync and conflict handling. Not every feature needs it: a payment or account balance screen must show the latest data, so there it is better to wait and show a clear error than to display stale data.

## Interview Traps

### Should you check `NWPathMonitor` before sending a request and skip it if there is "no network"?

**Common wrong answer:** "Yes, send if the path is `.satisfied`, otherwise report offline right away."

**Better answer:** Reachability is only a hint: a `.satisfied` path can still be a captive-portal Wi-Fi or a server that is down, and "no network" can change right after you check. Apple recommends simply attempting the request and handling the error, and enabling `waitsForConnectivity = true` so `URLSession` waits for connectivity itself. `NWPathMonitor` is useful for triggering a sync-queue flush or updating the UI, not as a gate in front of requests.

### Can you keep the sync queue in memory or in `UserDefaults`?

**Common wrong answer:** "Sure, the queue is small; store it temporarily and send when online."

**Better answer:** Memory is lost when the app is killed, and `UserDefaults` has no transactions, so the local change and the queue entry can drift apart if the app crashes halfway. The queue should live in the same database as the data and be written in the same transaction. Even then, deleting the app wipes the whole container, so unsynced writes are lost with it — show the user a "not yet synced" state.

### Is last-write-wins based on the device timestamp enough to resolve conflicts?

**Common wrong answer:** "Yes, whichever record has the newer `updatedAt` wins."

**Better answer:** Device clocks can be wrong or changed by the user, so "newer" is unreliable, and LWW silently drops one side's changes. A safer approach is for the server to issue a version or `ETag`; the client sends `If-Match`, the server returns `412 Precondition Failed` if the data has changed, and the app decides whether to merge or ask the user. LWW is only acceptable for low-stakes data such as settings.

## Exercise

Design an offline-first feed screen in pseudocode/comments: (1) load from cache → show immediately, (2) fetch from network in background → merge and refresh UI, (3) on network error → keep cached data + show non-blocking "Last updated X" banner. Identify which layer owns cache reads/writes, which layer decides to show the stale banner, and what happens to queued writes if the user reinstalls the app.
