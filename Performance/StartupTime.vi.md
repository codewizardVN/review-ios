[English](./StartupTime.md) | [Tiếng Việt](./StartupTime.vi.md)

[← Performance](./README.vi.md)

# Startup Time

## Hai giai đoạn

1. **Pre-main** — dylib loading, ObjC runtime initialization (`+load`, đăng ký class)
2. **Post-main** — `application(_:didFinishLaunchingWithOptions:)`, thiết lập view hierarchy ban đầu

## Nguyên nhân làm chậm startup

- Quá nhiều dynamic framework (mỗi cái thêm thời gian dylib load)
- `+load` hoặc `static let` initializer nặng
- Truy cập network hoặc disk đồng bộ lúc launch
- Thiết lập view phức tạp trước frame đầu tiên

## Cách đo lường

- Instruments → App Launch
- `DYLD_PRINT_STATISTICS=1` trong scheme environment variables
- Xcode Organizer → Launch Time metrics

## Cải thiện

- Giảm số lượng dynamic framework (merge module nhỏ)
- Chuyển setup nặng sang background sau frame đầu
- Defer khởi tạo không cần thiết (`lazy var`, on-demand)
- Dùng pre-warming (iOS 15+) — hệ thống launch app ở background trước khi người dùng mở

## Góc nhìn senior

Cải thiện 400ms startup time là giá trị thực cho người dùng. Nhưng hãy đo trước khi tối ưu — pre-main và post-main có nguyên nhân và cách sửa khác nhau. Instrument trước.

## Bài tập

Bật `DYLD_PRINT_STATISTICS=1` trong scheme và ghi lại thời gian pre-main. Sau đó mở Instruments → App Launch và xác định ba thao tác tốn kém nhất trong post-main. Đề xuất một thay đổi cụ thể để giảm mỗi thao tác đó.
