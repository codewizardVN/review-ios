[English](./Coordinator.md) | [Tiếng Việt](./Coordinator.vi.md)

[← UIKit và App Lifecycle](./README.vi.md)

# Coordinator và Router

## Ý chính

Navigation là application flow, không phải view rendering. Coordinator hoặc router pattern giúp screen không phải sở hữu quá nhiều hiểu biết về phần còn lại của app.

## Cần ôn

- Root coordinator vs child coordinator: root (thường gọi là `AppCoordinator`) được SceneDelegate tạo ra, sở hữu window hoặc root view controller và quyết định flow lớn (onboarding, login, main tab). Child coordinator sở hữu một flow con (checkout, auth), được parent tạo và giữ, và báo lại cho parent khi flow kết thúc.
- Cách screen gửi ý định navigation lên trên: screen không tự tạo màn hình tiếp theo mà gọi closure hoặc delegate kiểu "user muốn checkout", coordinator nhận ý định đó và quyết định đi đâu.
- Deep link đi vào flow đang tồn tại như thế nào: deep link được đổi thành route, đi từ root xuống dần các child coordinator, mỗi tầng xử lý phần của mình (xem đáp án bên dưới).
- Ownership và lifetime của coordinator: ai giữ strong reference tới coordinator, khi nào nó được giải phóng, và làm sao tránh retain cycle giữa coordinator, navigation controller và view controller.

## Câu hỏi thực hành

- Khi nào screen nên trigger navigation trực tiếp?
- Ai nên phản ứng với deep link mở vào nested flow?

## Câu hỏi luyện tập

- Khi nào một screen nên tự trigger navigation trực tiếp?
- Ai nên xử lý một deep link mở ra một flow lồng nhau?

## Góc nhìn senior

Coordinator pattern hữu ích khi độ phức tạp của navigation là có thật. Nếu chỉ có một flow đơn giản, thêm layer có thể không đáng. Điểm quan trọng là mức độ indirection phải khớp với độ phức tạp của sản phẩm.

## Đáp án câu hỏi luyện tập

### Khi nào một screen nên tự trigger navigation trực tiếp?

Screen nên tự navigate khi điểm đến là một phần "nội bộ" của chính nó: không được dùng lại ở flow khác, không phụ thuộc vào trạng thái app, và không ai khác cần biết. Ví dụ: present một `UIAlertController`, một image picker, một `UIActivityViewController` để share, hay một màn hình chi tiết nhỏ chỉ thuộc về feature đó. Trong những trường hợp này, việc bắt screen gửi intent lên coordinator chỉ thêm code mà không đem lại lợi ích gì.

Screen không nên tự navigate khi:

- Điểm đến thuộc feature khác. Screen phải import và khởi tạo view controller của module khác, nên dependency bị rối.
- Bước tiếp theo phụ thuộc vào ngữ cảnh. Ví dụ màn hình cart đi tới shipping hay login tùy user đã đăng nhập chưa.
- Cùng một screen được dùng trong nhiều flow, mỗi flow muốn đi tiếp một kiểu khác nhau.
- Cần hỗ trợ deep link đi thẳng tới giữa flow.

Khi đó screen chỉ nên báo ý định, ví dụ closure `onCheckoutTapped` hoặc delegate `cartDidRequestCheckout()`, và coordinator quyết định đi đâu. Trade-off: indirection giúp screen dễ test và dễ tái sử dụng, nhưng mỗi lớp thêm vào là thêm chỗ phải đọc khi debug. Hãy bắt đầu đơn giản và chỉ tách navigation ra khi thật sự có một trong các lý do ở trên.

### Ai nên xử lý một deep link mở ra một flow lồng nhau?

Coordinator cấp app nên nhận deep link trước, rồi chuyển tiếp xuống coordinator đang sở hữu flow đích. Screen không nên tự xử lý. Lý do là chỉ tầng cao nhất mới biết đủ ngữ cảnh: user đã đăng nhập chưa, đang ở tab nào, có modal nào đang mở cần đóng không.

Luồng hợp lý thường như sau:

1. SceneDelegate nhận URL và đưa cho một parser để đổi thành `Route`, ví dụ `.checkout(.payment)`.
2. `AppCoordinator` kiểm tra điều kiện (đăng nhập, dữ liệu cần thiết), dismiss modal đang mở, chọn đúng tab.
3. `AppCoordinator` tạo hoặc tái sử dụng `CheckoutCoordinator` rồi gọi `checkoutCoordinator.handle(.payment)`.
4. `CheckoutCoordinator` là bên duy nhất biết thứ tự cart, shipping, payment. Nó tự dựng navigation stack cho đúng, ví dụ push cart và shipping bên dưới để nút back vẫn hợp lý.

Mỗi coordinator chỉ hiểu phần route của mình và chuyển phần còn lại xuống con, giống chain of responsibility. Trade-off: nếu flow chưa sẵn sàng (thiếu địa chỉ giao hàng chẳng hạn), coordinator con phải có fallback, như dừng ở bước shipping thay vì nhảy thẳng vào payment.

## Bẫy phỏng vấn

### "User bấm nút back hệ thống, child coordinator có được giải phóng không?"

**Dễ trả lời sai:** Có, khi view controller bị pop thì coordinator cũng tự mất.

**Nên trả lời:** Parent thường giữ child trong mảng `childCoordinators`. Nút back hoặc cử chỉ vuốt back do `UINavigationController` xử lý, coordinator không được báo. Vì vậy child coordinator vẫn nằm trong mảng, gây leak và đôi khi xử lý event cũ. Cần lắng nghe `navigationController(_:didShow:animated:)` của `UINavigationControllerDelegate`, lấy view controller vừa rời màn hình qua `navigationController.transitionCoordinator?.viewController(forKey: .from)`, kiểm tra nó không còn trong `navigationController.viewControllers` (tức là bị pop, không phải bị push đè lên), rồi gọi `childDidFinish` cho child coordinator sở hữu màn hình đó.

### "View controller giữ coordinator, coordinator giữ navigation controller, có vấn đề gì?"

**Dễ trả lời sai:** Không sao, cứ để view controller giữ strong reference tới coordinator để gọi navigation cho tiện.

**Nên trả lời:** Coordinator giữ navigation controller, navigation controller giữ view controller, nếu view controller lại giữ coordinator mạnh thì thành retain cycle và cả flow không bao giờ được giải phóng. View controller nên giữ coordinator qua `weak var coordinator` hoặc tốt hơn là chỉ nhận closure như `var onFinish: (() -> Void)?` mà coordinator gán vào với `[weak self]`. Cách closure còn giúp view controller không cần biết kiểu coordinator.

### "Mọi app UIKit đều nên dùng Coordinator?"

**Dễ trả lời sai:** Có, Coordinator là best practice, mỗi screen nên có một coordinator riêng.

**Nên trả lời:** Coordinator giải quyết vấn đề navigation phức tạp: nhiều flow, flow dùng lại, deep link, điều kiện đăng nhập. Với app vài màn hình, một coordinator cho mỗi screen chỉ tạo boilerplate và làm việc debug khó hơn. Câu trả lời senior là chia coordinator theo flow (auth, checkout, onboarding), không theo screen, và giải thích mình chọn nó vì vấn đề cụ thể nào.

## Bài tập

Lấy một checkout flow gồm cart, shipping, payment, và confirmation screen. Phác thảo một root coordinator cùng một child coordinator. Sau đó giải thích deep link nên đi vào flow này ở điểm nào.
