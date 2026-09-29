[English](./UnitTests.md) | [Tiếng Việt](./UnitTests.vi.md)

[← Testing](./README.vi.md)

# Unit Tests

## Ý tưởng chính

Unit test kiểm tra một đơn vị hành vi duy nhất trong môi trường cô lập, không có network thật, database hay UI.

## Nội dung cần ôn

- XCTest — `XCTestCase`, `XCTAssert*`: framework test truyền thống, mỗi test là một method bắt đầu bằng `test`, kiểm tra bằng các hàm `XCTAssertEqual`, `XCTAssertTrue`, `XCTAssertThrowsError`...
- Swift Testing (có từ Xcode 16) — `@Test`, `@Suite`, `#expect`, `#require`: framework mới của Apple, dùng macro thay cho tên method, chạy test song song mặc định và hỗ trợ test tham số hoá (`@Test(arguments:)`). Hai framework có thể cùng tồn tại trong một test target.
- Cấu trúc Given / When / Then: chia test thành ba phần rõ ràng — chuẩn bị dữ liệu và dependency (Given), gọi hành động cần test (When), kiểm tra kết quả (Then) — giúp người đọc hiểu ngay test đang kiểm tra gì.
- Kiểm tra ViewModel thông qua input và output: gọi method public của ViewModel (input) rồi assert trên state mà nó expose (output), không kiểm tra chi tiết bên trong.
- Async testing: nếu code là `async`, khai báo test là `async` và `await` trực tiếp (cả XCTest và Swift Testing đều hỗ trợ). `XCTestExpectation` + `fulfillment(of:timeout:)` (hoặc `wait(for:timeout:)` trong code đồng bộ) dùng cho API kiểu callback/delegate; Swift Testing dùng `confirmation` để đếm số lần một sự kiện xảy ra, nhưng nó không tự chờ như expectation: sự kiện phải xảy ra trước khi closure của `confirmation` kết thúc, nên callback cần được bọc thành `async` (ví dụ `withCheckedContinuation`) rồi `await` bên trong closure.

## Ví dụ

```swift
import XCTest
@testable import MyApp

// ViewModel thường là @MainActor, nên test class cũng đánh dấu @MainActor
// để truy cập `sut.items` mà không bị lỗi isolation trong Swift 6.
@MainActor
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

## Đáp án câu hỏi luyện tập

### Test nào nên viết và test nào không nên?

Nên viết test cho logic có quyết định và có rủi ro, còn phần "dây nối" mỏng hoặc code của framework thì không cần test riêng.

Cách chọn đơn giản: hỏi "nếu chỗ này sai, user hoặc business có đau không, và lỗi có dễ lọt qua review không?". Những chỗ đáng test:

- Business rule: tính giá, validate form, quy tắc phân quyền.
- State transition của ViewModel: loading → loaded → error, như `FeedViewModel.load()` trong ví dụ.
- Mapping và parsing: JSON → model, model → text hiển thị.
- Edge case và nhánh lỗi: list rỗng, network lỗi, token hết hạn.
- Bug đã từng xảy ra: viết test tái hiện bug trước khi sửa để nó không quay lại.

Những chỗ không đáng test riêng: getter/setter đơn giản, initializer chỉ gán property, code chỉ chuyển tiếp lời gọi sang dependency, và hành vi của Apple framework (không cần test rằng `Array.sorted()` sắp xếp đúng). Layout thuần tuý cũng không hợp với unit test; snapshot test hoặc UI test phù hợp hơn.

Trade-off: test cũng là code phải bảo trì. Test bám vào chi tiết implementation (ví dụ assert thứ tự gọi từng method private) sẽ vỡ mỗi lần refactor mà không bắt được bug thật. Hãy test hành vi quan sát được qua input và output, không test cách code làm bên trong.

### Nếu code khó test, vấn đề thường nằm ở đâu?

Vấn đề thường nằm ở thiết kế, cụ thể là ở cách code lấy dependency và nơi đặt side effect, chứ hiếm khi nằm ở công cụ test.

Các nguyên nhân hay gặp:

- **Dependency ẩn**: code tự gọi `URLSession.shared`, `UserDefaults.standard`, `Date()` hoặc singleton ngay bên trong. Test không thể thay chúng bằng fake nên buộc phải chạm network thật hoặc phụ thuộc vào giờ hệ thống.
- **Global mutable state**: nhiều test cùng ghi vào một chỗ, nên kết quả phụ thuộc thứ tự chạy. Với Swift Testing chạy song song mặc định, lỗi này lộ ra nhanh hơn.
- **Trộn trách nhiệm**: một class vừa gọi API, vừa parse, vừa format text, vừa điều khiển UI. Muốn test một phần thì phải dựng cả khối.
- **Logic nằm trong UI**: logic trong `viewDidLoad` hay `body` cần view hierarchy mới chạy được.

Cách sửa là inject dependency qua initializer (như `FeedViewModel(repository:)`), để logic thuần tách khỏi I/O, và tách class lớn thành đơn vị nhỏ. Khi thiết kế đúng, test gần như tự viết: tạo fake, gọi method, kiểm tra output.

Khi không nên refactor ngay: code legacy lớn chưa có test nào. Lúc đó nên viết vài characterization test ở mức cao hơn để khoá hành vi hiện tại trước, rồi mới tách dần.

## Bẫy phỏng vấn

### "Coverage của team đạt 90%, vậy test suite có tốt không?"

**Dễ trả lời sai:** Coverage cao nghĩa là code được test kỹ, nên 90% là tốt và nên đẩy lên 100%.

**Nên trả lời:** Coverage chỉ đo dòng code đã được *chạy* trong lúc test, không đo xem test có *assert* đúng điều quan trọng hay không. Một test gọi `sut.load()` mà không có assertion nào vẫn tăng coverage. Coverage hữu ích để tìm vùng chưa được test, nhưng không phải thước đo chất lượng; đặt target cứng thường sinh ra test vô nghĩa. Chất lượng nên được đánh giá qua việc test có bắt được bug thật hay không, ví dụ bằng mutation testing hoặc review assertion.

### "ViewModel gọi `Task { await load() }` bên trong `onAppear()`. Test gọi `sut.onAppear()` rồi assert ngay. Có vấn đề gì?"

**Dễ trả lời sai:** Không sao, vì test là `async` nên nó sẽ tự chờ công việc bên trong hoàn thành.

**Nên trả lời:** `Task { }` tạo unstructured task; hàm `onAppear()` trả về ngay mà không chờ task đó, nên test assert trước khi dữ liệu về và sẽ fail hoặc flaky. Cách tốt nhất là cho ViewModel expose một hàm `async` (như `await sut.load()` trong ví dụ) để test await trực tiếp, hoặc giữ tham chiếu task để test `await task.value`. Tránh sửa bằng `Task.sleep` trong test, vì đó chỉ là đoán thời gian.

### "Trong XCTest, property của test class có được dùng chung giữa các test method không?"

**Dễ trả lời sai:** Có, XCTest tạo một instance cho cả class, nên phải reset state trong `setUp()` để các test không ảnh hưởng nhau.

**Nên trả lời:** XCTest tạo một instance riêng cho *mỗi* test method, nên stored property không bị chia sẻ. Gotcha thật là XCTest giữ tất cả các instance đó sống đến khi cả suite chạy xong, nên object nặng hoặc object có side effect không được giải phóng sớm; vì vậy nên gán `nil` trong `tearDown()`. Swift Testing cũng tạo instance mới cho mỗi `@Test`, và có thể dùng `deinit` của suite (class/actor) để dọn dẹp. Thứ thật sự bị chia sẻ là static và global state, nên đó mới là nơi cần cẩn thận.

## Bài tập

Viết unit test cho `LoginViewModel` có method `login(email:password:)`. Dùng `FakeAuthService` để stub phản hồi thành công. Cấu trúc test theo Given / When / Then. Sau đó viết thêm test cho trường hợp thất bại — assert rằng `errorMessage` được set khi service throw lỗi.
