[English](./MVC.md) | [Tiếng Việt](./MVC.vi.md)

[← Architecture](./README.vi.md)

# MVC (Model-View-Controller)

## Ý chính

Pattern mặc định trong UIKit apps. Controller là cầu nối giữa Model (data/business logic) và View (UI).

## Ưu điểm

- Đơn giản để bắt đầu
- Quen thuộc với hầu hết iOS developer
- Hoạt động tốt cho các màn hình nhỏ, độc lập

## Hạn chế

- Controller có xu hướng phình to ("Massive View Controller")
- Khó unit test vì controller gắn chặt với UIKit lifecycle
- Business logic, navigation và UI thường dồn vào cùng một chỗ

## Câu hỏi luyện tập

- Sau khi tách lời gọi URLSession, việc format giá inline, và push sang detail screen của một ProductListViewController thành Model, Controller và một Service riêng, cái gì trở nên unit-test được và cái gì vẫn không thể test trong UIKit MVC dù có tách?

## Góc nhìn Senior

MVC không hỏng về bản chất — nó thường bị áp dụng sai. MVC có kỷ luật với thin controller, model layer riêng biệt và service được tách ra có thể bảo trì được. Vấn đề thực sự là UIKit khiến việc đổ tất cả vào controller trở nên quá dễ.

## Đáp án câu hỏi luyện tập

### Sau khi tách lời gọi URLSession, việc format giá inline, và push sang detail screen của một ProductListViewController thành Model, Controller và một Service riêng, cái gì trở nên unit-test được và cái gì vẫn không thể test trong UIKit MVC dù có tách?

Test được là mọi thứ không còn phụ thuộc UIKit: Service lấy dữ liệu, logic format giá và việc map dữ liệu thành Model. Phần khó test vẫn là những gì còn ở Controller: push sang detail screen, cấu hình table view/cell và việc lifecycle kích hoạt load.

Sau khi tách, `ProductListViewController` chỉ gọi một `ProductService` (protocol, ví dụ `func fetchProducts() async throws -> [Product]`). Trong test bạn inject fake service trả dữ liệu cố định, hoặc test implementation thật bằng một `URLProtocol` stub để không gọi mạng. Format giá chuyển thành một hàm thuần như `PriceFormatter.format(_ price: Decimal, locale: Locale) -> String`: truyền `Locale` cố định vào test thì kết quả không phụ thuộc cài đặt máy. Model và việc decode JSON cũng test được như code Swift bình thường.

Phần còn lại vẫn dính UIKit:

- Push sang detail cần `UINavigationController` thật: bạn nhúng controller vào một navigation controller, giả lập việc chọn cell rồi kiểm tra `topViewController`. Làm được, nhưng đó đã là test tích hợp với UIKit: phải push không animation (hoặc chờ animation xong), và các transition phức tạp hơn như present thường cần view nằm trong một window.
- Việc load dữ liệu gắn vào `viewDidLoad`, nên test phải gọi `loadViewIfNeeded()`.
- Hiển thị cell đúng hay chưa thường phải dùng snapshot test hoặc UI test.

Nếu muốn test luôn cả navigation, bạn thay việc push trực tiếp bằng closure `onSelectProduct` hoặc một coordinator. Làm vậy là bạn đã bước sang MVVM/Coordinator. Trong MVC thuần, controller luôn là lớp "keo dán" không test rẻ được, nên mục tiêu là giữ nó càng mỏng càng tốt.

## Bẫy phỏng vấn

### "Apple MVC có giống MVC gốc của Smalltalk không?"

**Dễ trả lời sai:** "Giống, View quan sát Model và tự cập nhật khi Model thay đổi." Đó là MVC kinh điển, không phải cách Cocoa làm.

**Nên trả lời:** Trong Cocoa MVC, Controller là mediator: View và Model không biết nhau, mọi thay đổi đều đi qua Controller. Thêm nữa, `UIViewController` sở hữu luôn view và lifecycle của nó, nên thực tế View và Controller dính thành một khối. Đây chính là lý do controller dễ phình to và khó test.

### "Massive View Controller là lỗi của MVC, chuyển sang MVVM là hết?"

**Dễ trả lời sai:** "Đúng, MVVM giải quyết Massive View Controller." Nếu chỉ chuyển code từ controller sang ViewModel mà không tách trách nhiệm, bạn có Massive ViewModel.

**Nên trả lời:** Nguyên nhân gốc là thiếu phân tách trách nhiệm, không phải bản thân pattern. Trong MVC vẫn có thể tách service, data source riêng, child view controller và đẩy navigation ra ngoài. MVVM giúp chủ yếu ở chỗ presentation logic test được mà không cần UIKit, nhưng business logic vẫn cần tầng service/use case riêng.

### "Có unit test được UIViewController không? Test viewDidLoad thế nào?"

**Dễ trả lời sai:** "Không test được", hoặc "gọi thẳng `vc.viewDidLoad()` trong test".

**Nên trả lời:** Test được, nhưng phải để UIKit tự điều khiển lifecycle: gọi `vc.loadViewIfNeeded()` để view được load và `viewDidLoad` chạy đúng một lần. Gọi thẳng `viewDidLoad()` có thể khiến nó chạy hai lần khi `view` được truy cập sau đó. Những thứ như `viewDidAppear`, animation push/present cần window, nên chậm và dễ flaky; hãy giữ chúng mỏng và test logic ở chỗ khác.

## Bài tập

Lấy `ProductListViewController` (1) gọi URLSession trực tiếp, (2) format giá inline, (3) push sang detail screen. Xác định cái gì thuộc Model, Controller và một Service riêng biệt. Phác thảo sự phân tách trong comment — không cần viết code đầy đủ. Sau đó giải thích cái gì có thể unit test nếu code được cấu trúc như vậy, và cái gì vẫn không thể test trong UIKit MVC.
