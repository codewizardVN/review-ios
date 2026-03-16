[English](./Day2_Swift_Concurrency.md) | [Tiếng Việt](./Day2_Swift_Concurrency.vi.md)

# Day 2: Swift Concurrency

## Goal

Understand concurrency well enough to apply it safely in production apps.

## Topics

- `async/await`
- `Task`
- Task cancellation
- `MainActor`
- `Actor`
- Structured concurrency
- Race conditions

## What You Should Be Able To Explain

- Why `async/await` is easier to maintain than callback chains
- When a task should be cancelled
- The role of `MainActor`
- What problem `Actor` solves
- How structured concurrency helps manage lifecycle

## Practice Questions

- If the user leaves the screen, how should an in-flight request be handled?
- What is the difference between `Task.detached` and a regular `Task`?
- When can bugs still happen even if you use `Actor`?

## Senior Notes

- At senior level, concurrency is not just syntax.
- You should be able to explain ownership, cancellation, thread safety, and UI consistency.
