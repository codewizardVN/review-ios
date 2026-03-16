[English](./Day5_Networking_DataFlow.md) | [Tiếng Việt](./Day5_Networking_DataFlow.vi.md)

# Day 5: Networking and Data Flow

## Goal

Hiểu cách dữ liệu đi từ API tới UI theo hướng production-ready.

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

- Cách thiết kế API client rõ ràng và testable
- Domain model khác DTO thế nào
- Khi nào nên retry, khi nào không
- Cache nên đặt ở layer nào
- Dữ liệu lỗi cần propagate ra UI ra sao

## Practice Questions

- Nếu API chậm hoặc không ổn định, bạn thiết kế flow thế nào?
- Pagination nên xử lý ở ViewModel hay service?
- Làm sao tránh duplicate requests khi user thao tác nhanh?

## Senior Notes

- Câu trả lời tốt nên thể hiện rõ reliability, observability, UX impact.
