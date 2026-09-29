[English](./FeatureFlagsExperimentation.md) | [Tiếng Việt](./FeatureFlagsExperimentation.vi.md)

[← Chủ đề cấp Senior](./README.vi.md)

# Feature Flags và Experimentation

## Ý chính

Một feature flag là một nhánh runtime tồn tại lâu hơn cả PR đã thêm nó, trừ khi có ai đó chủ động xóa nó đi. Coi flag là miễn phí chính là cách một codebase tích lũy logic điều kiện rối rắm, vĩnh viễn mà không ai dám xóa.

## Những điều cần nắm

- Các loại flag — release flag (tạm thời, gate một feature đang làm dở), ops/kill-switch flag (vĩnh viễn, tắt một feature rủi ro khi tải cao hoặc gặp sự cố), permission flag (dựa trên entitlement), experiment flag (gán variant cho A/B test)
- Remote config vs local build flag — flag cấu hình từ xa có thể đổi hành vi mà không cần submit App Store mới, đổi lại phải định nghĩa rõ hành vi mặc định khi offline/cache-miss
- Cơ chế A/B test — gán variant (thường là hash ổn định của user ID, không phải random mỗi session), sample ratio mismatch (SRM — chia 50/50 nhưng thực tế thu được ví dụ 52/48 với lượng user lớn, chênh lệch vượt xa mức ngẫu nhiên) như một tín hiệu cho thấy randomization hoặc việc log exposure đang bị lỗi, nên kết quả experiment đó không đáng tin; guardrail metric (crash rate, doanh thu, tỷ lệ hủy…) có thể tự động abort một experiment khi variant đang gây hại
- Cơ bản về tính hợp lệ thống kê — tại sao nhìn trộm kết quả sớm và dừng ngay khi thấy "có vẻ significant" làm tăng false positive, và tại sao sample size phải được quyết định trước khi bắt đầu
- Vòng đời và dọn dẹp flag — mỗi release flag cần một owner và một ngày xóa; một flag còn sót trong code sau khi đã rollout toàn bộ là gánh nặng chết và nguồn gốc của bug kiểu "sao nhánh này còn tồn tại"
- Test dưới các flag — một flag nhân lên tổ hợp trạng thái app; quyết định tổ hợp nào thực sự đáng test (thường là: trạng thái mặc định, từng flag bật riêng lẻ, không phải tích đầy đủ)
- Rủi ro phía client — SDK flag bị outage hoặc fetch chậm phải có default an toàn; một feature fail open (bật) khi lẽ ra phải fail closed (tắt) là một sự cố production phổ biến
- Nhất quán UI theo flag — user không nên thấy một feature "nhấp nháy" bật lên giữa session vì flag vừa re-fetch; trạng thái flag thường được snapshot theo mỗi session/lần mở app

## Ví dụ

```swift
enum PaywallVariant { case control, redesign }

func paywallVariant(for userId: String) -> PaywallVariant {
    // Bucketing dựa trên hash ổn định — cùng một user luôn rơi vào cùng một variant
    // stableHash là hàm hash xác định tự viết, trả về UInt64 (không âm) — xem bẫy phỏng vấn bên dưới
    let bucket = stableHash(userId) % 100
    return bucket < 50 ? .control : .redesign
}
```

## Câu hỏi luyện tập

- Tại sao gán variant random mỗi session thường là sai cho một A/B test?
- Chuyện gì nên xảy ra nếu network call fetch flag fail lúc cold launch?
- Tại sao một release flag "tạm thời" từ sáu tháng trước được tính là tech debt?

## Góc nhìn Senior

Tín hiệu phỏng vấn ở đây là ai đó đã thực sự chịu trách nhiệm dọn dẹp mớ hỗn độn mà hệ thống flag tạo ra theo thời gian, chứ không chỉ dùng nó. Câu trả lời tốt nêu được một failure mode cụ thể: một experiment ship ra false positive vì ai đó dừng sớm, một kill-switch fail open trong lúc sự cố vì default không được đặt phòng thủ, hoặc một codebase với hàng chục release flag không ai nhớ mục đích. Cách fix trong mỗi trường hợp là quy trình (ownership của flag, ngày xóa, guardrail metric), không chỉ là "chúng tôi dùng LaunchDarkly."

## Đáp án câu hỏi luyện tập

### Tại sao gán variant random mỗi session thường là sai cho một A/B test?

Vì cùng một user sẽ lần lượt thấy cả control lẫn variant mới, nên bạn không còn đo được tác động của từng variant lên một người, và trải nghiệm của user cũng bị xáo trộn.

A/B test so sánh hai nhóm người tách biệt. Nếu random lại ở mỗi session:

- Kết quả bị nhiễm: user mua hàng ở session thứ ba có thể bị ảnh hưởng bởi paywall redesign ở session thứ hai, nhưng được tính cho control.
- Các quan sát không còn độc lập: một user hoạt động nhiều đóng góp vào cả hai nhóm, làm sai lệch thống kê.
- Metric theo user (retention, doanh thu trên mỗi user) không tính được vì user không thuộc về nhóm nào.
- UX tệ: hôm nay giá hiển thị một kiểu, ngày mai kiểu khác.

Vì vậy ví dụ trong file dùng `stableHash(userId) % 100`: cùng user luôn rơi vào cùng bucket. Nên thêm tên experiment vào input hash để các experiment khác nhau không chia user giống hệt nhau:

```swift
let bucket = stableHash("paywall_redesign_v1:" + userId) % 100
```

Với user chưa đăng nhập, dùng một install ID được lưu lại (ví dụ trong Keychain) và chấp nhận rằng user đổi thiết bị sẽ bị bucket lại.

Trade-off: random theo session chỉ hợp lý khi đơn vị phân tích thật sự là session và thay đổi không có ảnh hưởng kéo dài, ví dụ thứ tự kết quả tìm kiếm — nhưng khi đó phải phân tích theo session, không theo user.

### Chuyện gì nên xảy ra nếu network call fetch flag fail lúc cold launch?

App vẫn phải mở bình thường với giá trị an toàn: dùng giá trị đã cache từ lần fetch thành công trước, nếu không có thì dùng default được compile sẵn trong app — không bao giờ chặn launch để chờ network.

Thứ tự ưu tiên thường là:

1. Giá trị cache của lần trước, đã được "activate" từ session trước.
2. Default trong bundle nếu là lần mở đầu tiên hoặc cache hỏng.
3. Fetch ở background với timeout ngắn; giá trị mới chỉ áp dụng từ lần mở app sau để UI không nhấp nháy giữa session.

Default phải được chọn theo loại flag. Release flag cho feature đang làm dở nên fail closed (tắt). Kill switch cho feature đã ổn định thường có default là feature vẫn chạy, vì offline không phải sự cố. Feature rủi ro (thanh toán mới) luôn tắt khi không chắc chắn.

Với experiment, user chưa có assignment nên nhận control và không được log exposure, để không làm nhiễm dữ liệu. Chỉ log exposure ở thời điểm user thật sự thấy variant.

Trade-off: áp dụng ở lần mở sau nghĩa là một kill switch cần hiệu lực ngay sẽ chậm một session. Với flag loại đó, có thể cho phép áp dụng ngay tại các điểm an toàn, ví dụ trước khi mở màn hình checkout, thay vì đổi UI đang hiển thị.

### Tại sao một release flag "tạm thời" từ sáu tháng trước được tính là tech debt?

Vì nó giữ lại một nhánh code không còn ai dùng nhưng vẫn phải được đọc, build, test và bảo trì, và bất kỳ lúc nào cũng có thể bị bật sai.

Release flag sinh ra để gate một feature đang làm dở. Khi feature đã rollout 100%, nhánh `else` trở thành code chết, nhưng chi phí vẫn còn:

- Mỗi flag nhân đôi số trạng thái app; mười flag cũ là 1024 tổ hợp về lý thuyết.
- Người mới đọc code không biết nhánh nào là thật, phải hỏi hoặc đoán.
- Nhánh cũ không được test nữa; nếu ai đó hoặc một lỗi config ở remote đổi giá trị, user thấy UI cũ kèm bug đã được sửa từ lâu.
- Refactor bị cản vì phải giữ cả hai đường chạy được.

Cách xử lý mang tính quy trình: mỗi release flag có owner và ngày hết hạn ngay khi tạo; khi rollout xong thì mở ticket xóa flag; CI hoặc lint cảnh báo flag quá hạn.

```swift
@Flag(owner: "checkout-team", expires: "2026-12-01")
var newCheckout = false
```

(`@Flag` ở đây là property wrapper tự viết của team, không phải API hệ thống.)

Trade-off: kill switch và permission flag được thiết kế để tồn tại lâu dài, không phải nợ. Vấn đề chỉ xảy ra khi release flag bị để lại như thể nó là kill switch.

## Bẫy phỏng vấn

### "`stableHash` trong ví dụ có thể viết là `userId.hashValue` không?"

**Dễ trả lời sai:** Được, `hashValue` của cùng một `String` luôn ra cùng một số nên bucket ổn định.

**Nên trả lời:** Không. `Hasher` của Swift được seed ngẫu nhiên mỗi lần process khởi động, nên `hashValue` đổi sau mỗi lần mở app — user sẽ nhảy variant mỗi launch, đúng cái lỗi random-per-session. Nó cũng khác giữa iOS và server, nên backend không tính lại được bucket. Hãy dùng một hàm hash xác định như FNV-1a, hoặc lấy vài byte đầu của `SHA256` (CryptoKit), trên input `experimentKey + userId`.

### "Có remote config rồi thì ship feature mới mà không cần qua App Review được không?"

**Dễ trả lời sai:** Được, cứ ship code ẩn sau flag tắt, review xong thì bật lên cho user.

**Nên trả lời:** Flag chỉ nên bật/tắt code đã được review. Theo guideline 2.3.1, app không được chứa feature ẩn, ngủ đông hoặc không được mô tả với App Review; giấu một feature khỏi reviewer rồi bật sau có thể dẫn tới bị gỡ app. Guideline 2.5.2 cấm tải code thực thi mới làm thay đổi chức năng. Cách đúng là bật feature cho tài khoản review hoặc mô tả nó trong review notes; remote config dùng để rollout dần, không phải để né review.

### "Experiment đã significant ở ngày thứ ba, dừng sớm để ship luôn được không?"

**Dễ trả lời sai:** Được, p-value dưới 0,05 nghĩa là kết quả đã chắc chắn, chờ thêm chỉ phí thời gian.

**Nên trả lời:** Nếu mỗi ngày đều xem kết quả và dừng ngay lần đầu thấy p < 0,05, tỷ lệ false positive thật cao hơn 5% rất nhiều, vì bạn đang cho nhiễu ngẫu nhiên nhiều cơ hội vượt ngưỡng. Sample size và thời gian chạy (thường gồm ít nhất một chu kỳ tuần) phải được quyết định trước. Nếu cần dừng sớm, dùng phương pháp được thiết kế cho việc đó như sequential testing; còn guardrail metric thì được phép abort sớm khi variant đang gây hại.

## Bài tập

Thiết kế setup flag và experimentation để test một luồng onboarding mới so với luồng hiện tại. Nêu rõ: loại flag và cách variant được bucket, chuyện gì xảy ra ở lần mở đầu tiên nếu remote config chưa fetch xong, một guardrail metric sẽ tự động abort experiment, và kế hoạch của bạn (owner, deadline, điều kiện) để xóa flag khi đã có kết quả thắng.
