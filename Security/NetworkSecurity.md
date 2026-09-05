[English](./NetworkSecurity.md) | [Tiếng Việt](./NetworkSecurity.vi.md)

[← Security](./README.md)

# Network Security

## Key Idea

Transport security is not just "use HTTPS." App Transport Security (ATS) enforces TLS baseline requirements by default, and certificate/public key pinning adds defense against compromised or rogue CAs — at the cost of operational risk if not managed carefully.

## What To Review

- App Transport Security (ATS) — enforces TLS 1.2+ by default; `NSAppTransportSecurity` exceptions must be justified per-domain, not blanket-disabled
- Certificate pinning vs public key pinning — pinning the full cert breaks on every cert rotation; pinning the public key (or CA) survives renewal if the key doesn't change
- `URLSessionDelegate` — `urlSession(_:didReceive:completionHandler:)` is where pinning validation is implemented
- Pinning failure modes — a mismanaged pin (expired, not rotated with the backend) can lock out an entire app version with no way to fix except a store update
- Jailbreak/root detection — best-effort only, not a security boundary; useful as one signal among several (e.g., for a banking app's risk scoring), not as a hard gate
- Man-in-the-middle risk on public Wi-Fi — the actual threat pinning defends against

## Example

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

## Practice Questions

- Why is pinning the public key generally preferred over pinning the leaf certificate?
- What is your rollback plan if a pinned key needs to change on short notice (e.g., a CA compromise)?

## Senior Take

Pinning is a trade-off, not a free win: it raises the bar against MITM attacks but introduces an operational failure mode where a backend cert rotation you didn't coordinate can hard-break the app for every user, recoverable only via app update. A senior engineer pins with a rotation plan already in place (e.g., pin two keys — current and next — before rotating), not just the validation code.

## Exercise

Write the ATS exception justification you'd bring to a security review for allowing a single third-party analytics domain to use TLS 1.0. State the specific risk this introduces and the compensating control (e.g., scope of data sent to that domain) you'd propose instead of a blanket ATS opt-out.
