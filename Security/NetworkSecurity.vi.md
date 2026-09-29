[English](./NetworkSecurity.md) | [Tiếng Việt](./NetworkSecurity.vi.md)

[← Security](./README.vi.md)

# Network Security

## Ý chính

Transport security không chỉ đơn giản là "dùng HTTPS". App Transport Security (ATS) mặc định enforce baseline TLS, và certificate/public key pinning bổ sung lớp phòng thủ trước CA bị xâm phạm hoặc giả mạo — đổi lại rủi ro vận hành nếu không quản lý cẩn thận.

## Những điều cần nắm

- App Transport Security (ATS) — mặc định bắt buộc HTTPS với TLS 1.2 trở lên, cipher suite có forward secrecy và certificate đủ mạnh (ký bằng SHA-256, key RSA ≥ 2048 bit hoặc ECC ≥ 256 bit); exception trong `NSAppTransportSecurity` (ví dụ `NSExceptionDomains`) phải được justify theo từng domain, không tắt tràn lan bằng `NSAllowsArbitraryLoads`
- Certificate pinning vs public key pinning — pin toàn bộ cert sẽ gãy mỗi lần cert được rotate; pin public key (hoặc CA) vẫn sống sót qua renewal nếu key không đổi
- `URLSessionDelegate` — `urlSession(_:didReceive:completionHandler:)` là nơi implement validation cho pinning: đánh giá trust mặc định bằng `SecTrustEvaluateWithError`, rồi so public key trong chuỗi certificate với key đã pin (xem ví dụ)
- Failure mode của pinning — một pin quản lý sai (hết hạn, không rotate cùng backend) có thể khóa cả một version app mà không có cách fix nào ngoài update trên store
- Jailbreak/root detection — chỉ mang tính best-effort, không phải một security boundary; hữu ích như một tín hiệu trong nhiều tín hiệu (ví dụ risk scoring cho app ngân hàng), không phải một cổng chặn cứng
- Rủi ro man-in-the-middle trên Wi-Fi công cộng — mối đe dọa thực sự mà pinning phòng chống

## Ví dụ

```swift
func urlSession(
    _ session: URLSession,
    didReceive challenge: URLAuthenticationChallenge,
    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
) {
    // Chỉ xử lý challenge server trust; loại khác (client cert, HTTP auth...) để hệ thống xử lý mặc định
    guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
          let serverTrust = challenge.protectionSpace.serverTrust else {
        completionHandler(.performDefaultHandling, nil)
        return
    }

    // 1. Đánh giá trust mặc định trước: chuỗi CA, hạn dùng, hostname. Thiếu bước này thì cert hết hạn/sai domain vẫn qua được nếu key khớp
    guard SecTrustEvaluateWithError(serverTrust, nil) else {
        completionHandler(.cancelAuthenticationChallenge, nil)
        return
    }

    // 2. Mới so pin: SecTrustCopyCertificateChain (iOS 15+) thay cho SecTrustGetCertificateAtIndex đã deprecated
    let chain = (SecTrustCopyCertificateChain(serverTrust) as? [SecCertificate]) ?? []
    let matchesPin = chain.contains { certificate in
        guard let key = SecCertificateCopyKey(certificate),
              let keyData = SecKeyCopyExternalRepresentation(key, nil) as Data? else {
            return false
        }
        // pinnedPublicKeys: Set<Data> chứa key hiện tại + key dự phòng. Đây là raw key từ
        // SecKeyCopyExternalRepresentation, KHÔNG phải SPKI; muốn so với hash SPKI (như NSPinnedDomains)
        // phải ghép thêm ASN.1 header theo loại key rồi hash SHA-256
        return pinnedPublicKeys.contains(keyData)
    }

    if matchesPin {
        completionHandler(.useCredential, URLCredential(trust: serverTrust))
    } else {
        completionHandler(.cancelAuthenticationChallenge, nil)
    }
}
```

## Câu hỏi luyện tập

- Tại sao pin public key thường được ưu tiên hơn pin leaf certificate?
- Kế hoạch rollback của bạn là gì nếu pinned key cần đổi gấp (ví dụ CA bị xâm phạm)?

## Góc nhìn Senior

Pinning là một trade-off, không phải cái lợi miễn phí: nó nâng cao rào cản trước MITM nhưng đưa vào một failure mode vận hành — một lần rotate cert backend mà bạn không phối hợp trước có thể làm gãy hoàn toàn app cho mọi user, chỉ khắc phục được qua update app. Một kỹ sư senior pin kèm sẵn kế hoạch rotation (ví dụ pin hai key — hiện tại và kế tiếp — trước khi rotate), chứ không chỉ viết code validation.

## Đáp án câu hỏi luyện tập

### Tại sao pin public key thường được ưu tiên hơn pin leaf certificate?

Vì certificate được thay mới định kỳ, còn public key có thể giữ nguyên qua nhiều lần renew, nên pin theo key giúp app không bị gãy mỗi lần backend thay certificate.

Cơ chế: một certificate gồm public key cộng với thông tin như tên miền, ngày hết hạn và chữ ký của CA. Khi renew, CA ký ra một certificate mới — bytes khác hẳn, nên pin theo hash của cả cert sẽ fail ngay. Nhưng nếu team tạo CSR mới từ cùng key pair, public key (và hash SPKI của nó) không đổi, nên pin vẫn khớp. Điều này ngày càng quan trọng vì thời hạn certificate đang ngắn lại: Let's Encrypt là 90 ngày, và CA/Browser Forum đã thông qua lộ trình giảm dần thời hạn tối đa xuống 47 ngày vào năm 2029.

Cách làm thực tế:
- Pin hash SHA-256 của SubjectPublicKeyInfo, và luôn có ít nhất một backup key.
- Chạy đánh giá trust mặc định (`SecTrustEvaluateWithError`) trước, rồi mới so pin — đúng thứ tự như ví dụ trong file.
- Từ iOS 14 có thể khai báo `NSPinnedDomains` trong `Info.plist` thay vì tự viết delegate.

Trade-off: pin key của intermediate CA còn bền hơn nữa (không phụ thuộc key của server), nhưng khi đó mọi cert mà CA đó cấp cho domain của bạn đều được tin — bảo vệ yếu hơn. Và pin theo key nghĩa là không được tùy tiện rotate key; nếu key bị lộ, bạn cần backup pin đã có sẵn trong app.

### Kế hoạch rollback của bạn là gì nếu pinned key cần đổi gấp (ví dụ CA bị xâm phạm)?

Kế hoạch phải có sẵn trước khi sự cố xảy ra: các bản app đang chạy ngoài thực tế phải đã chứa pin dự phòng, vì lúc cần đổi gấp bạn không thể chờ mọi user cập nhật app.

Các lớp của kế hoạch:
1. **Backup pin trong mọi bản build**: ngoài key đang dùng, app pin thêm ít nhất một key dự phòng được tạo sẵn, cất offline, chưa từng dùng trên server — tốt nhất là với CA khác. Khi key hiện tại hoặc CA có vấn đề, backend chuyển sang cert dùng key dự phòng và các bản app cũ vẫn kết nối được.
2. **Phát hành bản app mới** với bộ pin mới (key mới làm chính cộng một backup mới), kèm cơ chế force update theo minimum version để dọn các bản cũ.
3. **Kill switch có kiểm soát**: một remote config có chữ ký (kiểm bằng key nhúng trong app) cho phép tắt pinning cho một domain khi khẩn cấp. Config này không được phép đến qua kênh chưa kiểm chứng, nếu không attacker cũng tắt được pinning.
4. **Giám sát**: log và report số lần pin fail theo version app để phát hiện sớm, trước khi thành outage.
5. **Đường báo nâng cấp**: endpoint kiểm tra version nên vẫn hoạt động khi pin fail, để app ít nhất báo được user cần cập nhật.

Trade-off: mỗi lớp giảm rủi ro "khóa cứng" app nhưng nới lỏng một phần bảo vệ (kill switch là một điểm tấn công mới). Với nhiều app, pin CA hoặc chỉ dựa vào ATS cùng Certificate Transparency là đủ; pinning chỉ thật sự đáng khi threat model (ngân hàng, y tế) đòi hỏi.

## Bẫy phỏng vấn

### Code pinning chỉ cần so public key của server với key đã pin là đủ?

**Dễ trả lời sai:** "Đủ, key khớp là đúng server thật."

**Nên trả lời:** Nếu chỉ so key mà bỏ qua đánh giá trust của hệ thống, app sẽ chấp nhận cả certificate hết hạn, sai hostname hoặc đã bị revoke, miễn là key khớp. Phải gọi `SecTrustEvaluateWithError(serverTrust, nil)` trước, rồi mới kiểm tra pin trên chuỗi certificate. Ngoài ra `SecTrustGetCertificateAtIndex` đã deprecated từ iOS 15, nên dùng `SecTrustCopyCertificateChain`; và delegate chỉ nên xử lý `NSURLAuthenticationMethodServerTrust`, các loại challenge khác trả về `.performDefaultHandling`.

### Pinning có ngăn được người khác dùng Charles/Proxyman để đọc traffic API của app không?

**Dễ trả lời sai:** "Có, pin xong thì không ai MITM được app nữa."

**Nên trả lời:** Pinning bảo vệ user khỏi attacker ở giữa đường truyền (Wi-Fi công cộng, CA giả mạo), nhưng không chống được người kiểm soát chính thiết bị: trên máy jailbreak, công cụ như Frida có thể hook và tắt logic pinning. Vì vậy đừng coi API là "bí mật" chỉ vì có pinning; bảo mật thật phải nằm ở server (authentication, authorization, rate limit), có thể bổ sung App Attest để xác minh request đến từ app thật.

### ATS có bảo vệ mọi kết nối mạng trong app không?

**Dễ trả lời sai:** "Có, ATS bật mặc định cho toàn bộ app."

**Nên trả lời:** ATS áp dụng cho URL Loading System (`URLSession` và các API xây trên nó); nó không áp dụng cho API tầng thấp như Network framework (`NWConnection`) hay socket, và web content có key riêng `NSAllowsArbitraryLoadsInWebContent`. SDK bên thứ ba dùng network stack riêng có thể đi vòng qua ATS. Muốn đảm bảo baseline TLS cho những đường đó, bạn phải tự cấu hình TLS hoặc review SDK. Ngoài ra, dùng `NSAllowsArbitraryLoads` phải có giải trình khi App Store review.

## Bài tập

Viết justification cho ATS exception mà bạn sẽ trình bày trong security review để cho phép một domain analytics bên thứ ba dùng TLS 1.0. Nêu rõ rủi ro cụ thể mà việc này đưa vào và compensating control (ví dụ giới hạn phạm vi dữ liệu gửi tới domain đó) bạn sẽ đề xuất thay vì tắt ATS tràn lan. Lưu ý: Apple đã deprecate TLS 1.0/1.1 từ iOS 15 và thông báo sẽ gỡ bỏ trong các bản sau, nên exception này có thể ngừng hoạt động trên iOS mới — cũng là một rủi ro cần nêu.
