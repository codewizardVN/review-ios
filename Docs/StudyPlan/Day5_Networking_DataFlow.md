[English](./Day5_Networking_DataFlow.md) | [Tiếng Việt](./Day5_Networking_DataFlow.vi.md)

# Day 5: Networking and Data Flow

## Goal

Understand how data should move from API to UI in a production-ready way.

## Topics

- URLSession
- Codable
- Request / response mapping
- Pagination
- Retry
- Timeout
- Cancellation
- Cache strategy
- Offline-first thinking

## What You Should Be Able To Explain

- How to design an API client that is clear and testable
- How domain models differ from DTOs
- When retry makes sense and when it does not
- Which layer should own caching
- How errors should propagate to the UI

## Practice Questions

- If the API is slow or unstable, how would you design the flow?
- Should pagination live in the ViewModel or the service layer?
- How do you avoid duplicate requests when users interact quickly?

## Senior Notes

- Strong answers here should show reliability, observability, and UX awareness.
