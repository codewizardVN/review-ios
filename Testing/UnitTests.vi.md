[English](./UnitTests.md) | [Tiếng Việt](./UnitTests.vi.md)

[← Testing](./README.vi.md)

# Unit Tests

## Ý tưởng chính

Unit test kiểm tra một đơn vị hành vi duy nhất trong môi trường cô lập, không có network thật, database hay UI.

## Nội dung cần ôn

- XCTest — `XCTestCase`, `XCTAssert*`
- Cấu trúc Given / When / Then
- Kiểm tra ViewModel thông qua input và output
- Async testing với `async/await` hoặc `XCTestExpectation`

## Ví dụ

```swift
final class FeedViewModelTests: XCTestCase {
    func test_load_populatesItems() async throws {
        // Given
        let repository = FakeFeedRepository(items: [.fixture()])
        let sut = FeedViewModel(repository: repository)

        // When
        await sut.load()

        // Then
        XCTAssertEqual(sut.items.count, 1)
    }
}
```

## Câu hỏi thực hành

- Nên viết test cho những phần nào và không nên viết cho phần nào?
- Nếu code khó test, vấn đề thường nằm ở đâu?

## Câu hỏi luyện tập

- Test nào nên viết và test nào không nên?
- Nếu code khó test, vấn đề thường nằm ở đâu?

## Góc nhìn senior

Code khó test thường là dấu hiệu thiết kế kém: code có dependency ẩn, global state, hoặc pha trộn nhiều trách nhiệm. Khi test khó, hãy refactor thay vì tìm cách vượt qua.

## Bài tập

Viết unit test cho `LoginViewModel` có method `login(email:password:)`. Dùng `FakeAuthService` để stub phản hồi thành công. Cấu trúc test theo Given / When / Then. Sau đó viết thêm test cho trường hợp thất bại — assert rằng `errorMessage` được set khi service throw lỗi.
