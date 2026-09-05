[English](./InterviewQA.md) | [Tiếng Việt](./InterviewQA.vi.md)

[← Docs](./README.vi.md) · [← Quay lại trang chủ](../README.vi.md)

# Bộ Câu Hỏi Phỏng Vấn

Mọi câu hỏi dưới đây được lấy trực tiếp từ mục "Câu hỏi luyện tập" (hoặc, với chủ đề chưa có mục đó, từ "Bài tập") của file chủ đề tương ứng — không có gì trong danh sách này được bịa ra riêng cho tài liệu này. Dùng nó như một bài drill nhanh sau khi đã học xong chủ đề của một ngày trong [PROGRESS.vi.md](../PROGRESS.vi.md): che câu trả lời, nói to ra kèm một trade-off, rồi kiểm tra lại file gốc nếu bị bí.

## Ngày 1 — Swift Core

### [Value Types và Reference Types](../Swift/ValueTypes.vi.md)
- Bạn sẽ dùng một kiểu `BankAccount` cài đặt cả dưới dạng struct lẫn class như thế nào để giải thích việc copy một struct account so với gán một class account làm thay đổi ngữ nghĩa của lời gọi `transfer(to:amount:)` ra sao?

### [ARC và Quản lý bộ nhớ](../Swift/ARC.vi.md)
- Bạn sẽ chứng minh retain cycle gây ra bởi completion closure của `DataLoader` capture `self` mạnh như thế nào, và tại sao `[weak self]` là cách sửa đúng thay vì `unowned`?

### [Protocol-Oriented Programming](../Swift/Protocols.vi.md)
- Tại sao việc inject protocol `AnalyticsService` (với `FirebaseAnalytics` và `NoOpAnalytics`) vào initializer của `CheckoutViewModel` lại giúp ViewModel có thể test được?

### [Generics](../Swift/Generics.vi.md)
- Tại sao constraint `Equatable` lại cần thiết cho method `contains(_:)` của `EquatableStack`, điều mà một `Stack<Element>` generic thông thường không thể hỗ trợ?

### [Opaque Types](../Swift/OpaqueTypes.vi.md)
- Tại sao `some Shape` phù hợp cho một factory function như `makeDefaultShape()` nhưng `any Shape` lại cần thiết cho một function như `largestShape(from shapes: [any Shape])`?

### [Xử lý lỗi](../Swift/ErrorHandling.vi.md)
- Một `do-catch` đầy đủ xử lý từng case của `ParseError` (`missingField`, `invalidFormat`, `unsupportedVersion`) với thông báo riêng cho người dùng khác gì so với việc chỉ dùng `try?`?

### [Access Control](../Swift/AccessControl.vi.md)
- Bạn sẽ thiết kế struct `KeychainStore` với các access level phù hợp cho `items` được lưu trữ, các method public read/write, và helper encrypt nội bộ như thế nào, và điều gì sẽ hỏng nếu `items` là public?

## Ngày 2 — Swift Concurrency

### [async/await](../Concurrency/AsyncAwait.vi.md)
- Sau khi viết lại function `fetchUser` dùng completion handler bằng async/await, trong tình huống thực tế nào bạn vẫn cần wrap nó trở lại thành completion-handler API bằng `withCheckedThrowingContinuation`?

### [Task và Cancellation](../Concurrency/Tasks.vi.md)
- Tại sao một `SearchViewModel` cần tự cancel task search trước đó bằng `task?.cancel()` và bắt `CancellationError` trước khi bắt đầu một `search(query:)` mới, để chỉ kết quả của lần gọi cuối cùng trong ba lần gọi liên tiếp được áp dụng?

### [Actor và MainActor](../Concurrency/Actors.vi.md)
- Loại state corruption nào có thể xảy ra trong một actor `RequestCounter` nếu bạn chèn `await` giữa `increment()` và `decrement()`, dù actor vẫn đảm bảo an toàn cho 100 task đồng thời gọi cả hai method?

### [Structured Concurrency](../Concurrency/StructuredConcurrency.vi.md)
- Khi nào `async let` rõ ràng hơn cho một function `loadProfile()` fetch đồng thời user, posts và followers, và khi nào `withThrowingTaskGroup` trở nên cần thiết thay thế?

### [Combine](../Concurrency/Combine.vi.md)
- Tại sao quên lưu `Cancellable` lại khiến subscription âm thầm ngừng hoạt động?
- Khi nào bạn vẫn nên dùng Combine trong codebase đã chuyển hẳn sang `async/await`?

### [Objective-C Interop](../Swift/ObjCInterop.vi.md)
- Tại sao một method `@objc` đánh dấu `private` lại fail lúc runtime khi gọi qua `perform(_:)`?
- Chuyện gì xảy ra nếu quên `NS_ASSUME_NONNULL_BEGIN` trong một header legacy mà module Swift import?
- Tại sao một `enum` Swift có associated value không thể expose cho Objective-C?

## Ngày 3 — SwiftUI

### [Vòng đời View](../SwiftUI/ViewLifecycle.vi.md)
- Tại sao `.task` được ưu tiên hơn `onAppear` kết hợp quản lý task thủ công cho một `CountdownView` cần cancel đếm ngược dựa trên `Task.sleep` khi user navigate away?

### [Quản lý State](../SwiftUI/StateManagement.vi.md)
- Điều gì xảy ra nếu dùng `@ObservedObject` thay vì `@StateObject` cho `CartViewModel` trong `ShoppingCartView` khi navigate sang detail screen rồi quay lại?

### [Navigation](../SwiftUI/Navigation.vi.md)
- Bạn sẽ pre-populate `NavigationPath` của `NavigationStack` lúc app launch như thế nào để một deep link đi thẳng đến màn Reviews cho một item cụ thể, bỏ qua màn List và Detail?

### [Hiệu năng Rendering](../SwiftUI/RenderingPerformance.vi.md)
- Tại sao thay đổi `selectedTab` lại khiến mọi row trong `UserListView` re-render không cần thiết, và tách row thành view riêng với observation scope hẹp hơn giải quyết vấn đề đó như thế nào?

### [Dependency Injection trong SwiftUI](../SwiftUI/DependencyInjection.vi.md)
- Giữa initializer injection và environment injection cho `UserRepository` trong `ProfileView`, cách nào bạn ưu tiên cho một session dependency dùng chung toàn app, và vì sao?

### [Tương tác với UIKit](../SwiftUI/UIKitInterop.vi.md)
- Tại sao cần một Coordinator khi wrap `UIColorPickerViewController` bằng `UIViewControllerRepresentable` để truyền `UIColor` được chọn về qua `@Binding<Color>`, và lifecycle của nó so với Representable ra sao?

### [Widgets và Live Activities](../SwiftUI/WidgetsLiveActivities.vi.md)
- Tại sao widget không thể đọc trực tiếp view model `@Observable` của app?
- Chuyện gì xảy ra với UI Live Activity trên Lock Screen nếu push update ngừng gửi đến?
- Tại sao hệ thống giới hạn tần suất `reloadTimelines` thực sự trigger redraw?

## Ngày 4 — Architecture

### [MVC](../Architecture/MVC.vi.md)
- Sau khi tách lời gọi `URLSession`, việc format giá inline, và push sang detail screen của một `ProductListViewController` thành Model, Controller và một Service riêng, cái gì trở nên unit-test được và cái gì vẫn không thể test trong UIKit MVC dù có tách?

### [MVVM](../Architecture/MVVM.vi.md)
- Tại sao việc inject một protocol `WeatherService` trả về Kelvin thô vào `WeatherViewModel` (chuyển đổi sang định dạng như "23°C") và test bằng `FakeWeatherService` lại xác nhận được rằng file ViewModel không có UIKit import?

### [Clean Architecture](../Architecture/CleanArchitecture.vi.md)
- Làm sao bạn wire Domain (`Article` entity, `ArticleRepository` protocol, `GetArticlesUseCase`), Data (`RemoteArticleRepository`) và Presentation (`ArticleListViewModel`) trong một unit test không dùng network thật, đồng thời xác nhận domain layer không có UIKit hay networking import?

### [Coordinator Pattern](../Architecture/Coordinator.vi.md)
- Sau khi chuyển trách nhiệm push sang `ForgotPasswordViewController` từ `LoginViewController` sang một coordinator, object nào nên sở hữu coordinator đó và vì sao?

### [Dependency Injection](../Architecture/DependencyInjection.vi.md)
- Tại sao constructor injection lại được ưu tiên hơn property injection cho các dependency bắt buộc như `PaymentServiceProtocol` và `AnalyticsProtocol` trong `CheckoutViewModel`?

### [Modularization](../Architecture/Modularization.vi.md)
- Pain point cụ thể nào — build time, coupling, hay ownership — sẽ thúc đẩy bạn tách module đầu tiên trong một e-commerce app có Auth, ProductCatalog, Cart, Orders, UserProfile và các shared core module như DesignSystem, Networking, Analytics?

### [Design Patterns](../Architecture/DesignPatterns.vi.md)
- Tại sao protocol `Repository` quan trọng cho testability hơn là cho chính implementation trong production?
- Khi nào Singleton là lựa chọn đúng, và khi nào nó là dấu hiệu dependency injection đã bị bỏ qua?

## Ngày 5 — Networking, Persistence và Security

### [URLSession](../Networking/URLSession.vi.md)
- Tại sao việc inject `URLSession` qua init lại giúp bạn test được `fetch(_:from:)` của một `APIClient` generic bằng `URLProtocol` stub cho cả trường hợp decode JSON hợp lệ lẫn trường hợp status non-200 ném ra `APIError.invalidResponse`?

### [Codable](../Networking/Codable.vi.md)
- Điều gì sẽ hỏng nếu domain model `User` decode JSON trực tiếp thay vì đi qua `UserDTO` với `CodingKeys` mapping và chuyển đổi `toDomain()`?

### [Request/Response Mapping](../Networking/RequestResponseMapping.vi.md)
- Bạn sẽ xử lý field thiếu hoặc invalid ở đâu khi map một `FeedItemDTO` (với `created_at`, `author_name`, `image_url` optional) sang domain `FeedItem` dùng cho UI?

### [Pagination](../Networking/Pagination.vi.md)
- Làm sao bạn ngăn duplicate request khi user chạm đáy danh sách nhiều lần trong một infinite feed dùng cursor pagination với các state success, empty, loading-more, error?

### [Retry / Timeout](../Networking/RetryTimeout.vi.md)
- Tại sao một `fetchWithRetry(url:maxAttempts:)` dùng exponential backoff nên chỉ retry với `URLError` chứ không phải lỗi HTTP 4xx, và tại sao POST request thường KHÔNG nên được retry?

### [Cache Strategy](../Networking/CacheStrategy.vi.md)
- Tại sao `NSCache` lại phù hợp hơn Dictionary thông thường cho một `ThumbnailCache` giới hạn 50 item, điều gì xảy ra với cached item dưới memory pressure, và tầng cache nào bạn thêm nếu thumbnail cần persist qua các lần launch?

### [Offline-First](../Networking/OfflineFirst.vi.md)
- Trong một offline-first feed screen, tầng nào nên sở hữu việc đọc/ghi cache, tầng nào quyết định hiển thị banner dữ liệu cũ, và điều gì xảy ra với một queued write nếu người dùng xóa và cài lại app?

### [Core Data](../Persistence/CoreData.vi.md)
- Tại sao không bao giờ được truyền `NSManagedObject` trực tiếp giữa các thread?
- Điều gì xảy ra nếu hai context save các thay đổi xung đột lên cùng một object?

### [SwiftData](../Persistence/SwiftData.vi.md)
- Trade-off khi áp dụng SwiftData vào một app đã có dữ liệu Core Data nhiều năm là gì?
- Tại sao `@Query` giảm bớt boilerplate kiểu `NSFetchedResultsController`?

### [Keychain](../Security/Keychain.vi.md)
- Tại sao bạn sẽ chọn `AfterFirstUnlock` thay vì `WhenUnlocked` cho một token cần dùng bởi background refresh task?
- Bạn cần làm gì tường minh để token không âm thầm còn tồn tại sau khi user xóa và cài lại app?

### [Network Security](../Security/NetworkSecurity.vi.md)
- Tại sao pin public key thường được ưu tiên hơn pin leaf certificate?
- Kế hoạch rollback của bạn là gì nếu pinned key cần đổi gấp (ví dụ CA bị xâm phạm)?

## Ngày 6 — Testing

### [Unit Tests](../Testing/UnitTests.vi.md)
- Bạn sẽ cấu trúc unit test theo Given/When/Then cho `LoginViewModel.login(email:password:)` dùng `FakeAuthService` như thế nào để assert `errorMessage` được set đúng khi service throw lỗi?

### [UI Tests](../Testing/UITests.vi.md)
- Khi chọn một flow quan trọng trong app để viết UI test, bạn xác định launch setup, accessibility identifier cần có, và assertion có ý nghĩa mà không bám quá chặt vào chi tiết UI như thế nào?

### [Mocking](../Testing/Mocking.vi.md)
- Một `FakeAnalyticsService` ghi lại tên mỗi event được inject vào `CheckoutViewModel` để assert `trackPurchase()` được gọi đúng một lần là mock, stub, hay spy?

### [Testable Design](../Testing/TestableDesign.vi.md)
- Làm sao bạn refactor một `ProfileViewController` gọi `URLSession.shared.dataTask` trực tiếp trong `viewDidLoad` để có thể test được, bằng cách tách ra một protocol `ProfileService` và inject qua initializer?

### [Snapshot Tests](../Testing/SnapshotTests.vi.md)
- Bạn cần thiết lập CI như thế nào để giữ cho snapshot test của `PriceTagView` (giá thường, giá khuyến mãi, miễn phí) không sinh false positive trên các máy khác nhau?

## Ngày 7 — Performance và Debugging

### [Main Thread Discipline](../Performance/MainThread.vi.md)
- Tại sao việc decode JSON và filter kết quả của `SearchViewModel` phải chuyển ra khỏi main thread bằng `Task.detached`, rồi publish kết quả về trên `@MainActor`, thay vì làm trực tiếp trong `didReceiveData`?

### [Memory Leaks](../Performance/MemoryLeaks.vi.md)
- Nếu `deinit` của một view controller không bao giờ được gọi sau khi navigate away vì một `Timer` hoặc `NotificationCenter` observer, bạn sẽ dùng Memory Graph Debugger như thế nào để tìm và sửa retain cycle?

### [Rendering Issues](../Performance/RenderingIssues.vi.md)
- Tại sao set `shadowPath` rõ ràng và xóa `masksToBounds` lại loại bỏ offscreen rendering (highlight vàng) của một `CardView` dùng `cornerRadius` kèm shadow?

### [Startup Time](../Performance/StartupTime.vi.md)
- Sau khi ghi lại thời gian pre-main bằng `DYLD_PRINT_STATISTICS=1` và xác định ba thao tác tốn kém nhất trong post-main bằng công cụ App Launch của Instruments, bạn sẽ đề xuất thay đổi cụ thể nào cho mỗi thao tác?

### [Large List Optimization](../Performance/LargeListOptimization.vi.md)
- So sánh hiệu năng scroll giữa một `UICollectionViewDiffableDataSource` hiển thị 10.000 item và một SwiftUI `List` cùng dữ liệu dùng id ổn định, bạn sẽ dùng Time Profiler để phát hiện khác biệt gì về frame rate?

### [App Size Optimization](../Performance/AppSizeOptimization.vi.md)
- Tại sao thêm một CocoaPod duy nhất có thể tăng cả binary size lẫn thời gian launch app?
- Khi nào bạn dùng On-Demand Resources thay vì bundle tất cả ngay từ đầu?

## Ngày 8 — Senior Review và Interview Scenarios

### [System Design cho iOS Apps](../Senior/SystemDesign.vi.md)
- Khi phác thảo một tính năng notification inbox với sync strategy, cập nhật read/unread, pagination và điểm vào từ push notification, phần nào bạn sẽ cố ý chưa xây ở version 1?

### [Tư duy Code Review](../Senior/CodeReview.vi.md)
- Bạn xử lý phản đối từ tác giả PR không đồng ý với comment [blocking] của bạn về việc gọi `URLSession.shared` trực tiếp trong init của `UserProfileViewModel` như thế nào?

### [Chiến lược Refactoring](../Senior/Refactoring.vi.md)
- Sau khi viết characterization test cho ba behavior quan trọng nhất của một `MassiveViewController`, bạn tách một trách nhiệm ra class mới bằng Strangler Fig pattern như thế nào mà vẫn giữ tất cả test pass?

### [Backward Compatibility](../Senior/BackwardCompatibility.vi.md)
- Rủi ro tương thích nào phát sinh khi đổi schema cache local và ship thêm một bước onboarding mới trong cùng một release, và bạn sẽ sắp xếp rollout an toàn ra sao?

### [Release Process](../Senior/ReleaseProcess.vi.md)
- Một release checklist cho một bản cập nhật payments gấp trước chiến dịch marketing nên gồm những pre-release check, rollout strategy, monitoring signal và stop-ship criteria nào?

### [CI/CD cho Mobile](../Senior/CICD.vi.md)
- Bạn giữ đồng bộ signing credential giữa các thành viên team như thế nào mà không phải gửi file `.p12` qua email?
- Chiến lược của bạn khi CI build fail dù build local pass?
- Bạn sẽ tăng tốc một pipeline CI 40 phút như thế nào mà không cắt giảm test coverage?

### [Debug vấn đề Production](../Senior/ProductionDebugging.vi.md)
- Trước khi reproduce được ở local một crash force-unwrap nil trong `CartViewController.viewDidLoad` chỉ ảnh hưởng user iOS 16 ở version 2.3.1, bạn đặt ra những giả thuyết nào và cần thu thập thêm dữ liệu gì?

### [Technical Leadership](../Senior/TechnicalLeadership.vi.md)
- Khi team bị chia đôi giữa migrate sang SwiftUI ngay và giữ UIKit với deadline product còn 6 tuần, bạn sẽ viết một tài liệu quyết định gồm trade-off và khuyến nghị như thế nào để truyền đạt cho cả engineering lẫn product manager?

## Ngày 9 — UIKit và App Lifecycle

### [App Lifecycle](../UIKit/AppLifecycle.vi.md)
- Làm sao bạn phân định phần nào là app-level orchestration và phần nào là feature-level behavior trong các hành động app cần làm khi cold launch, xuống background, và quay lại foreground?

### [View Controller Lifecycle](../UIKit/ViewControllerLifecycle.vi.md)
- Bạn sẽ chuyển lời gọi API ra khỏi `viewDidAppear`, việc set constraints ra khỏi `viewWillAppear`, và việc subscribe notification không cleanup ra khỏi `viewDidLoad` sang những vị trí phù hợp nào, và vì sao?

### [Coordinator và Router](../UIKit/Coordinator.vi.md)
- Trong một checkout flow gồm cart, shipping, payment và confirmation với một root coordinator và một child coordinator, deep link nên đi vào flow này ở điểm nào?

### [Auto Layout](../UIKit/AutoLayout.vi.md)
- Bạn đặt priority như thế nào cho một profile header (avatar, name, subtitle, action button) để tên dài vẫn truncate đúng trong khi button vẫn giữ đủ vùng chạm?

### [Collection View và Diffable Data Source](../UIKit/CollectionViewDiffable.vi.md)
- Bạn định nghĩa item identifier và cập nhật một item từ section unread sang read trong một collection view hai section (unread/read) như thế nào để không tạo ra animation khó hiểu?

### [Deep Link, Universal Link, và Notification Flow](../UIKit/DeepLinks.vi.md)
- Routing cho `myapp://orders/123` và universal link tương ứng nên hoạt động thế nào khi app cold launch, khi đang ở tab khác, và khi user chưa đăng nhập?

### [Push Notifications](../UIKit/PushNotifications.vi.md)
- Tại sao silent push không đáng tin cậy cho các cập nhật background mang tính thời gian thực?
- Bạn sẽ test luồng tap-to-navigate như thế nào khi app đã bị terminate hoàn toàn?

### [Background Execution](../UIKit/BackgroundExecution.vi.md)
- Tại sao phải reschedule một `BGAppRefreshTask` ngay đầu handler thay vì ở cuối?
- Sự khác biệt về đảm bảo giữa background URLSession upload và `BGProcessingTask` là gì?
- Tại sao `beginBackgroundTask` không thể thay thế cho `BGTaskScheduler`?

## Ngày 10 — Platform Quality và Growth

### [Accessibility](../Accessibility/Accessibility.vi.md)
- Tại sao `accessibilityLabel("Heart icon")` cho một nút favorite là một label tệ?
- Điều gì bị gãy trong một cell thiết kế chiều cao cố định khi user đặt cỡ Dynamic Type lớn nhất?
- Tại sao một biểu đồ tự vẽ (Canvas/Core Graphics) cần công sức accessibility tường minh mà một `List` gốc được miễn phí?

### [Localization và Internationalization](../Accessibility/Localization.vi.md)
- Tại sao `String(format: "%d items", count)` sai khi ship cho locale Ả Rập hoặc Nga?
- Layout UIKit dựng bằng constraint `.left`/`.right` gãy chỗ nào khi app chạy ở tiếng Ả Rập?
- Tại sao một feature flag hoặc analytics event không bao giờ nên dùng string đã localize làm key?

### [App Store Submission và Review](../Senior/AppStoreSubmission.vi.md)
- Tại sao tài khoản demo bật 2FA gần như chắc chắn dẫn đến reject?
- Tại sao việc thiếu privacy manifest là reject tự động chứ không phải một quyết định phán đoán của con người?
- Khi nào nên kháng cáo một rejection thay vì chỉ sửa vấn đề bị gắn cờ?

### [Crash Reporting và Analytics](../Senior/CrashReportingAnalytics.vi.md)
- Tại sao một dSYM bị thiếu quan trọng hơn một dòng comment code bị thiếu?
- Tại sao "crash-free users" thường là release gate tốt hơn số crash thô?
- Tại sao tên event analytics nên được review như một API, chứ không thêm tùy tiện theo từng feature?

### [Feature Flags và Experimentation](../Senior/FeatureFlagsExperimentation.vi.md)
- Tại sao gán variant random mỗi session thường là sai cho một A/B test?
- Chuyện gì nên xảy ra nếu network call fetch flag fail lúc cold launch?
- Tại sao một release flag "tạm thời" từ sáu tháng trước được tính là tech debt?
