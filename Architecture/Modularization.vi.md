[English](./Modularization.md) | [Tiếng Việt](./Modularization.vi.md)

[← Architecture](./README.vi.md)

# Modularization

## Ý chính

Tách app thành các Swift package hoặc target riêng biệt để giảm coupling, tăng tốc build và tạo ranh giới rõ ràng giữa các tính năng.

## Chiến lược tách module phổ biến

- **Theo tầng** — `CoreDomain`, `DataLayer`, `UIComponents`
- **Theo tính năng** — `FeedFeature`, `ProfileFeature`, `AuthFeature`
- **Kết hợp** — feature modules + shared core modules

## Lợi ích

- Build tăng dần nhanh hơn (chỉ build lại module bị thay đổi)
- Ranh giới cứng ngăn coupling ngoài ý muốn giữa features
- Các team có thể sở hữu module độc lập

## Câu hỏi thực hành

- Tiêu chí nào để tách module đầu tiên?
- Ranh giới module nên chia theo tính năng hay theo tầng?

## Câu hỏi luyện tập

- Bạn dùng tiêu chí gì để tách module đầu tiên?
- Ranh giới module nên tách theo feature hay theo layer?

## Góc nhìn Senior

Bắt đầu modularize khi build time ảnh hưởng năng suất hoặc khi ownership team trở nên không rõ ràng — không phải mặc định từ ngày đầu. Over-modularization thêm overhead quản lý dependency mà không có lợi ích tương xứng với codebase nhỏ.

## Đáp án câu hỏi luyện tập

### Bạn dùng tiêu chí gì để tách module đầu tiên?

Module đầu tiên nên là phần có ranh giới rõ, ít phụ thuộc vào phần còn lại của app, và giải quyết một nỗi đau đo được, thường là một module nền tảng như `Networking` hoặc `DesignSystem`.

Các tiêu chí cụ thể:

- **Có nỗi đau thật**: build time chậm (xem Build Timeline hoặc báo cáo thời gian build của Xcode), merge conflict liên tục ở cùng một vùng code, hoặc không rõ team nào sở hữu phần nào. Không tách chỉ vì "app lớn thì nên modular".
- **Là lá trong dependency graph**: module không được phụ thuộc ngược vào app target, nên tách từ dưới lên. Code chỉ dùng Foundation và không gọi vào feature nào là ứng viên tốt nhất.
- **API ổn định và ít coupling**: nếu kéo module ra mà phải kéo theo nửa app, hoặc nó đụng tới hàng loạt singleton, thì chưa phải lúc.
- **Được dùng lại nhiều**: networking, design system, analytics dùng ở mọi feature nên tách ra có lợi ngay.

Tách module đầu tiên còn là bài kiểm tra: bạn buộc phải khai báo `public` rõ ràng, và các dependency ẩn (singleton, extension dùng chung) lộ ra ngay. Chi phí cần tính: thiết lập local Swift package, xử lý access control, resource phải truy cập qua `Bundle.module` thay vì `Bundle.main`.

### Ranh giới module nên tách theo feature hay theo layer?

Thường nên kết hợp: feature module dọc ở trên, một vài core module ngang ở dưới như `Networking`, `DesignSystem`, `Analytics`.

Nếu chỉ tách theo layer, ví dụ mọi ViewModel nằm trong module `Presentation` và mọi repository trong `DataLayer`, thì sửa một feature phải chạm vào mọi module. Bạn không có build isolation, và không team nào sở hữu trọn một module. Tách theo feature như `CartFeature`, `ProfileFeature` cho phép build và test một feature riêng, và giao ownership rõ ràng.

Quy tắc quan trọng: feature module không import trực tiếp lẫn nhau. Khi `Cart` cần mở màn hình sản phẩm, hãy dùng một interface module nhỏ (ví dụ `ProductCatalogInterface` chứa protocol và model) hoặc để app target nối hai feature với nhau qua closure hay protocol. Bên trong một feature module, layer có thể chỉ là thư mục, hoặc target con nếu feature đủ lớn.

Tách theo layer vẫn có chỗ đứng: với app nhỏ, hai module `Domain` và `Data` là cách rẻ để compiler ép quy tắc phụ thuộc của Clean Architecture.

## Bẫy phỏng vấn

### "Càng tách nhiều module thì build càng nhanh?"

**Dễ trả lời sai:** "Đúng, mỗi module build riêng nên luôn nhanh hơn."

**Nên trả lời:** Incremental build chỉ nhanh khi thay đổi nằm ở module lá. Sửa một core module mà mọi feature phụ thuộc vẫn khiến tất cả rebuild, nhất là khi đổi public API. Quá nhiều module nhỏ còn tăng thời gian lập kế hoạch build và link. Nếu dùng nhiều dynamic framework, app launch chậm hơn vì dyld phải load từng cái; library SPM mặc định (automatic) thường được link static, và Xcode 15 có mergeable libraries để giảm vấn đề này.

### "`Cart` cần `ProductCatalog` và `ProductCatalog` cần nút 'Thêm vào giỏ', vậy cho hai module import nhau?"

**Dễ trả lời sai:** Cho import vòng, hoặc dồn mọi thứ chung vào một module `Common`/`Utils`.

**Nên trả lời:** SwiftPM không cho phép dependency vòng, nên cách đầu không build được. Cách thứ hai tạo ra một "god module" mà mọi feature phụ thuộc, sửa gì cũng rebuild tất cả. Cách đúng là đảo phụ thuộc: tách interface module chỉ chứa protocol và model, hoặc để app target inject closure như `onAddToCart` vào `ProductCatalog`. Hai feature chỉ biết abstraction, không biết nhau.

### "Muốn dùng chung code giữa các module trong cùng package thì phải để `public`?"

**Dễ trả lời sai:** "Phải `public`, vì `internal` chỉ thấy trong một module." Kết quả là chi tiết nội bộ bị lộ ra cho mọi client.

**Nên trả lời:** Từ Swift 5.9 có access level `package` (SE-0386): symbol thấy được bởi mọi module trong cùng Swift package nhưng không lộ ra ngoài package. Ngoài ra `@testable import` cho test truy cập `internal`, nhưng chỉ khi module được build với testability bật (mặc định ở Debug), nên đừng dựa vào nó cho code production.

## Bài tập

Thiết kế module map (ASCII diagram trong comment) cho e-commerce app với: Auth, ProductCatalog, Cart, Orders, UserProfile. Xác định module nào là feature module vs shared core module (DesignSystem, Networking, Analytics). Vẽ dependency arrows. Đánh dấu dependency nào sẽ tạo circular dependency. Giải thích pain point cụ thể nào — build time, coupling, hay ownership — sẽ thúc đẩy bạn tách module đầu tiên.
