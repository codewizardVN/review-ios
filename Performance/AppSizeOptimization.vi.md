[English](./AppSizeOptimization.md) | [Tiếng Việt](./AppSizeOptimization.vi.md)

[← Performance](./README.vi.md)

# App Size Optimization

## Ý chính

Kích thước app ảnh hưởng đến tỷ lệ cài đặt, giới hạn tải qua mạng di động, và ma sát khi update. Tối ưu diễn ra ở tầng asset, binary, và cơ chế phân phối — không chỉ đơn giản là "nén ảnh lại."

## Những điều cần nắm

- App thinning — App Store Connect build và phục vụ một variant khớp với thiết bị (chỉ độ phân giải/architecture ảnh cần thiết), dựa trên `Asset Catalog` và on-demand resources
- On-Demand Resources (ODR) — gắn tag để asset tải sau khi cài thay vì bundle sẵn trong bản tải ban đầu (ví dụ level game, asset của feature ít dùng)
- Asset catalog vs ảnh rời — catalog cho phép slicing và nén tốt hơn (HEIC, ASTC cho texture)
- Dead code stripping — code Swift/Obj-C không dùng, localization không dùng, module SDK bên thứ ba không dùng
- Static vs dynamic framework — dynamic framework thêm chi phí load-time và trùng lặp overhead Swift runtime theo từng framework; static linking giảm launch time và trùng lặp binary cho các module nội bộ nhỏ
- Audit dependency — một SDK nặng (analytics, ad network) có thể thêm hàng chục MB; cần biết cái gì thực sự đang dùng so với chỉ đang cài
- `App Size Report` trong Xcode Organizer — phân tích install size theo component (executable, framework, resource, asset)

## Câu hỏi luyện tập

- Tại sao thêm một CocoaPod duy nhất có thể tăng cả binary size lẫn thời gian launch app?
- Khi nào bạn dùng On-Demand Resources thay vì bundle tất cả ngay từ đầu?

## Góc nhìn Senior

Kích thước app là chi phí xuyên suốt, không phải việc dọn dẹp một lần — mỗi dependency mới, mỗi localization không dùng, mỗi asset chưa nén đều cộng dồn. Câu trả lời ở tầm senior không phải "chạy size report một lần trước release," mà là có một size budget được track trong CI (fail build nếu binary size vượt ngưỡng), để phát hiện sự tăng trưởng theo từng PR thay vì phát hiện lúc submit.

## Bài tập

Install size của app bạn tăng từ 45MB lên 78MB sau hai chu kỳ release và marketing đang hỏi tại sao conversion giảm. Dùng các category trong size report của Xcode Organizer (executable, framework, resource), viết ra các bước điều tra bạn sẽ thực hiện để tìm 3 nguyên nhân lớn nhất, và đề xuất một cách fix cho mỗi category (ví dụ một dynamic framework có thể chuyển sang static link, một asset có thể chuyển sang ODR, một dependency có thể loại bỏ hoặc thay thế).
