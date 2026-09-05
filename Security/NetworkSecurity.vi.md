[English](./NetworkSecurity.md) | [Tiếng Việt](./NetworkSecurity.vi.md)

[← Security](./README.vi.md)

# Network Security

## Ý chính

Transport security không chỉ đơn giản là "dùng HTTPS". App Transport Security (ATS) mặc định enforce baseline TLS, và certificate/public key pinning bổ sung lớp phòng thủ trước CA bị xâm phạm hoặc giả mạo — đổi lại rủi ro vận hành nếu không quản lý cẩn thận.

## Những điều cần nắm

- App Transport Security (ATS) — mặc định enforce TLS 1.2+; exception `NSAppTransportSecurity` phải được justify theo từng domain, không tắt tràn lan
- Certificate pinning vs public key pinning — pin toàn bộ cert sẽ gãy mỗi lần cert được rotate; pin public key (hoặc CA) vẫn sống sót qua renewal nếu key không đổi
- `URLSessionDelegate` — `urlSession(_:didReceive:completionHandler:)` là nơi implement validation cho pinning
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
    guard let serverTrust = challenge.protectionSpace.serverTrust,
          let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
        completionHandler(.cancelAuthenticationChallenge, nil)
        return
    }

    let serverPublicKey = SecCertificateCopyKey(certificate)
    let serverKeyData = SecKeyCopyExternalRepresentation(serverPublicKey!, nil) as Data?

    if serverKeyData == pinnedPublicKeyData {
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

## Bài tập

Viết justification cho ATS exception mà bạn sẽ trình bày trong security review để cho phép một domain analytics bên thứ ba dùng TLS 1.0. Nêu rõ rủi ro cụ thể mà việc này đưa vào và compensating control (ví dụ giới hạn phạm vi dữ liệu gửi tới domain đó) bạn sẽ đề xuất thay vì tắt ATS tràn lan.
