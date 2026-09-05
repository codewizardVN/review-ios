[English](./OpaqueTypes.md) | [Tiếng Việt](./OpaqueTypes.vi.md)

[← Swift Core](./README.vi.md)

# Opaque Types: `any` vs `some`

## Ý chính

- `some Protocol` — kiểu cụ thể được ẩn đi nhưng cố định tại compile time (reverse generics)
- `any Protocol` — existential storage có thể chứa bất kỳ conforming type nào tại runtime

## Ví dụ

```swift
// some: caller không biết kiểu cụ thể, nhưng nó cố định
func makeView() -> some View { ... }

// any: có thể chứa bất kỳ conforming type nào — linh hoạt hơn, hiệu năng thấp hơn
var repo: any UserRepository
```

## Câu hỏi luyện tập

- Tại sao some Shape phù hợp cho một factory function như makeDefaultShape() nhưng any Shape lại cần thiết cho một function như largestShape(from shapes: [any Shape])?

## Góc nhìn Senior

Bạn cần hiểu đủ sâu để thảo luận về API design, các đánh đổi về hiệu năng, và khi nào existential type là lựa chọn phù hợp hơn.

## Bài tập

Viết một protocol `Shape` với property `var area: Double`. Tạo hai conforming type: `Circle` và `Rectangle`. Viết một function `makeDefaultShape() -> some Shape` trả về một `Circle`. Sau đó viết một function `largestShape(from shapes: [any Shape]) -> any Shape`. Giải thích trong comment tại sao `some` phù hợp cho factory function nhưng `any` lại cần thiết cho tham số array.
