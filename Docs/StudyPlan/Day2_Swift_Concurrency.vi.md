[English](./Day2_Swift_Concurrency.md) | [Tiếng Việt](./Day2_Swift_Concurrency.vi.md)

# Day 2: Swift Concurrency

## Goal

Hiểu concurrency theo cách đủ để áp dụng vào app production.

## Topics

- `async/await`
- `Task`
- Task cancellation
- `MainActor`
- `Actor`
- Structured concurrency
- Race conditions

## What You Should Be Able To Explain

- Vì sao `async/await` dễ maintain hơn callback chains
- Khi nào nên cancel task
- Vai trò của `MainActor`
- `Actor` giải quyết vấn đề gì
- Structured concurrency giúp quản lý lifecycle ra sao

## Practice Questions

- Nếu user rời màn hình, request đang chạy nên xử lý thế nào?
- `Task.detached` khác gì `Task` thông thường?
- Khi nào vẫn có thể xảy ra bug dù đã dùng `Actor`?

## Senior Notes

- Ở level senior, concurrency không chỉ là syntax.
- Bạn cần nói rõ ownership, cancellation, thread-safety, UI consistency.
