[English](./BackwardCompatibility.md) | [Tiếng Việt](./BackwardCompatibility.vi.md)

[← Chủ đề Senior](./README.vi.md)

# Backward Compatibility

## Ý chính

Backward compatibility nghĩa là code mới không làm hỏng client cũ, dữ liệu đã persist, hoặc các OS version còn được hỗ trợ nếu chưa có migration plan rõ ràng.

## Cần ôn

- Thay đổi API contract và fallback behavior
- Migration cho database hoặc cache
- Feature flag để rollout theo giai đoạn
- Availability check theo OS và graceful degradation

## Ví dụ

Nếu server thêm một field mới vào response, app cũ thường không sao, vì `Codable` bỏ qua key thừa. Rủi ro thật nằm ở những thay đổi khác: server bắt đầu **bắt buộc** một field mới trong request (app cũ không gửi field đó nên request bị từ chối), đổi tên hoặc xóa một field mà app cũ decode bắt buộc, cho field có thể trả về `null`, hoặc thêm giá trị enum mới. Khi đó app version cũ có thể fail, trừ khi decoding đủ tolerant hoặc backend hỗ trợ một giai đoạn chuyển tiếp (chấp nhận cả request cũ lẫn mới).

## Câu hỏi thực hành

- Làm sao ship feature mới mà vẫn hỗ trợ app version cũ?
- Khi nào bạn cần migration thay vì silent fallback?

## Câu hỏi luyện tập

- Bạn ship một feature mới trong khi vẫn hỗ trợ các version app cũ như thế nào?
- Khi nào bạn cần một migration thay vì một fallback âm thầm?

## Góc nhìn senior

Compatibility không chỉ là chuyện kỹ thuật. Nó là product work. Một câu trả lời senior tốt sẽ nghĩ tới người dùng thật đang ở build cũ, staged release, và recovery path khi giả định bị sai trong production.

## Đáp án câu hỏi luyện tập

### Bạn ship một feature mới trong khi vẫn hỗ trợ các version app cũ như thế nào?

Tôi giả định version cũ sẽ còn tồn tại hàng tháng, nên thay đổi phía API phải là additive, còn phía app thì bật feature bằng flag và kiểm tra OS availability.

Cụ thể:

- **API:** chỉ thêm field mới dạng optional, không đổi nghĩa hay xóa field cũ. Nếu bắt buộc phải breaking change thì tạo endpoint hoặc version API mới và giữ bản cũ cho đến khi phần lớn người dùng đã update. Backend có thể đọc header app version để trả response phù hợp.
- **Decoding ở app:** field mới là optional hoặc có giá trị mặc định; enum có case `unknown` để khi server thêm giá trị mới, version cũ không fail khi decode.
- **Feature flag / remote config:** code mới ship ở trạng thái tắt, bật dần theo phần trăm hoặc theo version, và luôn có kill switch.
- **OS:** dùng `if #available` và có UI fallback cho API chỉ có trên iOS mới.
- **Minimum supported version** (force update) chỉ dùng cho trường hợp thật sự phải bỏ version cũ, ví dụ lỗi bảo mật.

Trade-off: giữ tương thích nghĩa là backend phải duy trì nhiều nhánh logic, và feature flag phải được dọn sau khi rollout xong, nếu không code sẽ đầy nhánh chết. Tôi thường đặt điều kiện rõ: khi version cũ xuống dưới một ngưỡng (ví dụ 2–5% active user) thì mới xóa đường cũ.

### Khi nào bạn cần một migration thay vì một fallback âm thầm?

Cần migration khi dữ liệu cũ có giá trị với người dùng hoặc khi đọc sai sẽ gây hậu quả; fallback âm thầm chỉ phù hợp khi dữ liệu có thể tạo lại và mất nó thì không ai để ý.

Ví dụ:

- **Fallback được:** cache feed, thumbnail, response có thể tải lại. Decode fail thì xóa cache và tải lại từ server; người dùng chỉ thấy chậm một chút.
- **Cần migration:** draft chưa gửi, dữ liệu offline chưa sync, cài đặt người dùng, dữ liệu mua hàng lưu local. Fallback âm thầm ở đây đồng nghĩa với mất dữ liệu.
- **Fallback nguy hiểm:** khi nghĩa của dữ liệu thay đổi, ví dụ đổi số tiền từ `Double` sang số nguyên theo cent. App vẫn đọc được nhưng hiểu sai.

Migration nên có schema version, idempotent, chạy đúng khi người dùng nhảy nhiều version (từ 2.1 lên thẳng 2.5), và được test bằng dữ liệu thật từ version cũ. Với Core Data thì dùng lightweight migration nếu đủ, staged migration (iOS 17+) khi phức tạp hơn; với SwiftData thì dùng `SchemaMigrationPlan`.

Kể cả khi chọn fallback, đừng để nó "âm thầm" hoàn toàn: log một non-fatal event để biết tỷ lệ fallback trong production. Trade-off: migration tốn công và có thể làm chậm lần mở app đầu tiên sau update; nếu dữ liệu lớn, cân nhắc chạy nền và hiển thị trạng thái chờ.

## Bẫy phỏng vấn

### "Server thêm một giá trị mới vào field enum. Có breaking không?"

**Dễ trả lời sai:** "Thêm thì không bao giờ breaking, chỉ xóa mới breaking." Câu này đúng với field mới, nhưng sai với giá trị enum mới.

**Nên trả lời:** Với `Codable`, key thừa trong JSON bị bỏ qua nên thêm field thường an toàn. Nhưng nếu app decode một `enum` strict, giá trị lạ sẽ làm fail cả object, và thường kéo theo fail cả mảng chứa nó — version cũ có thể mất toàn bộ màn hình. Tương tự, đổi một field từ luôn có thành có thể `null` cũng làm version cũ fail. Cách phòng là có case `unknown`, decode tolerant từng phần tử, và thống nhất với backend những thay đổi nào được coi là breaking.

### "Chỉ cần bọc `if #available` là hỗ trợ được iOS cũ đúng không?"

**Dễ trả lời sai:** "Đúng, compiler đã cảnh báo hết rồi." `#available` chỉ đảm bảo bạn không gọi API không tồn tại, không đảm bảo behavior đúng.

**Nên trả lời:** Vẫn phải test trên OS thấp nhất được hỗ trợ (cài simulator runtime tương ứng hoặc máy thật), vì cùng một API có thể hoạt động khác nhau giữa các version iOS. Ngoài ra, khi nâng deployment target, người dùng trên OS cũ không bị mất app: app đã cài vẫn chạy, chỉ không nhận được update mới; nếu họ đã từng tải app thì App Store còn cho tải lại version cuối cùng tương thích với OS của họ. Nghĩa là version cũ đó sẽ tiếp tục gọi API của bạn rất lâu, và backend phải tiếp tục hỗ trợ nó.

### "Bạn test migration như thế nào?"

**Dễ trả lời sai:** "Cài bản mới lên máy dev và kiểm tra app chạy." Đó là fresh install, không phải migration.

**Nên trả lời:** Phải test đường upgrade: cài bản cũ (từ TestFlight hoặc build tag cũ), tạo dữ liệu thật, rồi cài bản mới đè lên và kiểm tra dữ liệu. Cần test thêm trường hợp nhảy nhiều version, fresh install, và migration bị gián đoạn giữa chừng (app bị kill). Nếu được, viết unit test migration với file store mẫu từ các version cũ để CI chạy mỗi lần.

## Bài tập

Team muốn thay schema của local cache và ship thêm một bước onboarding mới trong cùng release. Hãy mô tả các compatibility risk và cách bạn sắp rollout an toàn.
