[English](./StartupTime.md) | [Tiếng Việt](./StartupTime.vi.md)

[← Performance](./README.vi.md)

# Startup Time

## Hai giai đoạn

1. **Pre-main** — mọi thứ xảy ra trước khi `main()` chạy: kernel tạo process, dyld load và liên kết các dynamic library/framework, Objective-C runtime đăng ký class/category và chạy các method `+load`, chạy static initializer của C/C++ (`__attribute__((constructor))`, constructor của biến global C++)
2. **Post-main** — từ `main()` / `UIApplicationMain` đến khi frame đầu tiên hiển thị: khởi tạo UIKit/SwiftUI, `application(_:didFinishLaunchingWithOptions:)`, tạo scene và view hierarchy ban đầu, render frame đầu

## Nguyên nhân làm chậm startup

- Quá nhiều dynamic framework (mỗi cái thêm việc cho dyld: map file, kiểm tra chữ ký, fix-up pointer)
- Code nặng trong `+load` hoặc static initializer C/C++ (chạy ở pre-main). Lưu ý: `static let` và biến global của Swift được khởi tạo lười (lazy) ở lần truy cập đầu tiên, không chạy ở pre-main — nhưng nếu bạn truy cập chúng trong `didFinishLaunching` thì chi phí vẫn tính vào post-main
- Truy cập network hoặc disk đồng bộ lúc launch
- Thiết lập view phức tạp trước frame đầu tiên

## Cách đo lường

- Instruments → template App Launch: chia launch thành các phase (process creation, dyld, static initializers, UIKit init, initial frame rendering) và cho biết code nào chạy trong từng phase
- Xcode Organizer → Metrics → Launch Time: số liệu launch từ thiết bị của người dùng thật (theo phiên bản app, percentile)
- MetricKit `MXAppLaunchMetric`: histogram time-to-first-draw và thời gian resume, lấy trong app ở production
- `XCTApplicationLaunchMetric` trong performance test để đo tự động và phát hiện regression
- (`DYLD_PRINT_STATISTICS=1` là cách cũ thời dyld2; trên iOS hiện đại với dyld3/dyld4 nó không còn cho kết quả hữu ích)

## Cải thiện

- Giảm số lượng dynamic framework (gộp module nhỏ, link static, hoặc dùng mergeable libraries từ Xcode 15)
- Chuyển setup nặng ra sau frame đầu, và chạy ở background nếu nó không cần main thread
- Defer khởi tạo không cần thiết (`lazy var`, khởi tạo khi thật sự dùng)
- Hiểu prewarming (iOS 15+): đây không phải tính năng bạn bật, mà là hành vi của hệ thống — có thể chạy sẵn phần pre-main của app khi người dùng chưa mở để lần mở sau nhanh hơn. Code của bạn phải chịu được điều đó (xem Bẫy phỏng vấn)

## Câu hỏi luyện tập

- Sau khi đo thời gian pre-main và xác định ba thao tác tốn kém nhất trong post-main bằng template App Launch của Instruments, bạn sẽ đề xuất thay đổi cụ thể nào cho mỗi thao tác?

## Góc nhìn senior

Cải thiện 400ms startup time là giá trị thực cho người dùng. Nhưng hãy đo trước khi tối ưu — pre-main và post-main có nguyên nhân và cách sửa khác nhau. Instrument trước.

## Đáp án câu hỏi luyện tập

### Sau khi đo thời gian pre-main và xác định ba thao tác tốn kém nhất trong post-main bằng template App Launch của Instruments, bạn sẽ đề xuất thay đổi cụ thể nào cho mỗi thao tác?

Nguyên tắc chung: việc gì không cần cho frame đầu tiên thì dời ra sau frame đầu, làm nền, hoặc làm lazy khi thật sự cần. Lưu ý về cách đo: trước đây nhiều tài liệu đo pre-main bằng `DYLD_PRINT_STATISTICS=1`, nhưng trên iOS hiện đại (dyld3 rồi dyld4) biến này hầu như không còn in gì hữu ích cho app. Vì vậy hãy lấy số pre-main từ chính template App Launch — nó chia launch thành các phase như process creation, dyld, static initializers, UIKit init và initial frame rendering; phần pre-main là các phase trước UIKit init.

Ba thao tác post-main tốn kém thường gặp và cách sửa:

- **Khởi tạo SDK trong `didFinishLaunching`** (analytics, quảng cáo, remote config, A/B test): chỉ giữ crash reporter chạy đồng bộ; các SDK còn lại khởi tạo sau khi màn hình đầu hiển thị, với priority thấp. Cẩn thận: trong `didFinishLaunching` (chạy trên `@MainActor`), `Task(priority: .utility) { ... }` vẫn kế thừa main actor, nên code đồng bộ bên trong vẫn chạy trên main; nếu SDK cho phép khởi tạo ngoài main thì dùng `Task.detached(priority: .utility)` hoặc hàm `@concurrent`, còn nếu SDK bắt buộc main thread thì chỉ dời nó ra sau frame đầu.
- **Disk/database đồng bộ:** load Core Data store, chạy migration, đọc file JSON/plist lớn, đọc Keychain. Chuyển sang async, hiển thị skeleton UI trong lúc chờ, chạy migration nặng ở background.
- **View hierarchy ban đầu quá nặng:** root tab bar tạo sẵn cả 5 tab, storyboard lớn, load font hoặc ảnh lớn. Chỉ tạo tab đang hiển thị, lazy các tab còn lại, đơn giản hoá màn hình đầu.

Nếu pre-main lớn: giảm số dynamic framework (link static, hoặc dùng mergeable libraries từ Xcode 15), bỏ code trong `+load` và static initializer nặng.

Sau mỗi thay đổi, đo lại trong cùng điều kiện (cold launch, thiết bị thật, release build), có thể tự động bằng `XCTApplicationLaunchMetric` trong performance test; sau khi release, xác nhận bằng Launch Time trong Xcode Organizer hoặc `MXAppLaunchMetric` của MetricKit. Trade-off: dời việc ra sau frame đầu có thể chỉ chuyển độ trễ sang màn hình kế tiếp, nên cần kiểm tra cả trải nghiệm ngay sau launch.

## Bẫy phỏng vấn

### "Bạn đo pre-main bằng cách nào?"

**Dễ trả lời sai:** Bật `DYLD_PRINT_STATISTICS=1` trong scheme và đọc log trong console.

**Nên trả lời:** Đây là kiến thức cũ: từ khi dyld3 (dùng cho app từ iOS 13) rồi dyld4 (các bản iOS mới hơn) thay thế dyld2, biến môi trường này hầu như không còn hiệu lực với app iOS. Cách hiện tại là template App Launch trong Instruments (có phase dyld và static initializers riêng), Launch Time trong Xcode Organizer cho số liệu từ người dùng thật, và `MXAppLaunchMetric` của MetricKit.

### "Chạy app từ Xcode thấy launch 2 giây, vậy app launch chậm?"

**Dễ trả lời sai:** Đo launch bằng cách bấm Run trong Xcode với debug build là đủ tin cậy.

**Nên trả lời:** Debugger attach và debug build (không tối ưu, có thêm các diagnostic) làm launch chậm hơn nhiều so với thực tế. Phải phân biệt cold launch (sau khi khởi động lại máy hoặc lâu không mở, dylib chưa nằm trong bộ nhớ) và warm launch (vừa mở gần đây). Đo trên thiết bị thật, release build, không attach debugger, lấy trung bình nhiều lần.

### "Prewarming giúp app launch nhanh hơn, vậy code trong static initializer chắc chắn chạy khi người dùng mở app?"

**Dễ trả lời sai:** Pre-main luôn chạy ngay trước khi người dùng thấy app, nên có thể dựa vào nó để đo thời gian hoặc chuẩn bị dữ liệu của người dùng.

**Nên trả lời:** Từ iOS 15, hệ thống có thể prewarm: chạy process tới trước `UIApplicationMain` (dyld, static initializers) khi người dùng chưa mở app, rồi suspend nó có khi hàng giờ. Vì vậy đừng lấy thời điểm process start làm mốc đo launch (biến môi trường `ActivePrewarm` bằng `"1"` cho biết đang prewarm), và đừng truy cập dữ liệu có data protection, Keychain hay state của người dùng trong initializer — lúc đó máy có thể đang khoá.

## Bài tập

Build release và profile app bằng template App Launch của Instruments trên thiết bị thật (cold launch: xoá app khỏi bộ nhớ, tốt nhất khởi động lại máy trước lần đo đầu). Ghi lại thời gian pre-main (các phase dyld và static initializers) và tổng thời gian đến initial frame, rồi xác định ba thao tác tốn kém nhất trong post-main. Đề xuất một thay đổi cụ thể để giảm mỗi thao tác đó. Viết một performance test dùng `XCTApplicationLaunchMetric` để đo trước/sau, và mô tả bạn sẽ theo dõi kết quả ở production như thế nào (Launch Time trong Xcode Organizer, `MXAppLaunchMetric` của MetricKit).
