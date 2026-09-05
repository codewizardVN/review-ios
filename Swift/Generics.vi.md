[English](./Generics.md) | [Tiếng Việt](./Generics.vi.md)

[← Swift Core](./README.vi.md)

# Generics

## Ý chính

Generics cho phép bạn viết các API có thể tái sử dụng và type-safe mà không cần dùng đến weakly typed code.

## Ví dụ

```swift
struct APIResponse<T: Decodable>: Decodable {
    let data: T
}
```

## Câu hỏi luyện tập

- Tại sao constraint Equatable lại cần thiết cho method contains(_:) của EquatableStack, điều mà một Stack<Element> generic thông thường không thể hỗ trợ?

## Góc nhìn Senior

Một câu trả lời cấp Senior tốt giải thích khi nào generics cải thiện sự rõ ràng của API và khi nào thiết kế generic nặng nề trở nên khó đọc và khó bảo trì.

## Bài tập

Implement một generic `Stack<Element>` với `push(_:)`, `pop() -> Element?`, và `peek() -> Element?`. Thêm một phiên bản thứ hai `EquatableStack<Element: Equatable>` có thêm method `contains(_ element: Element) -> Bool`. Viết 3 ví dụ sử dụng cho thấy tại sao generic constraint trên phiên bản thứ hai là cần thiết.
