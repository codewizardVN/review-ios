[English](./NetworkSecurity.md) | [Tiếng Việt](./NetworkSecurity.vi.md)

[← Security](./README.md)

# Network Security

## Key Idea

Transport security is not just "use HTTPS." App Transport Security (ATS) enforces TLS baseline requirements by default, and certificate/public key pinning adds defense against compromised or rogue CAs — at the cost of operational risk if not managed carefully.

## What To Review

- App Transport Security (ATS) — by default requires HTTPS with TLS 1.2 or later, forward-secrecy cipher suites and strong enough certificates (SHA-256 signatures, RSA ≥ 2048-bit or ECC ≥ 256-bit keys); exceptions in `NSAppTransportSecurity` (e.g. `NSExceptionDomains`) must be justified per domain, not blanket-disabled with `NSAllowsArbitraryLoads`
- Certificate pinning vs public key pinning — pinning the full cert breaks on every cert rotation; pinning the public key (or CA) survives renewal if the key doesn't change
- `URLSessionDelegate` — `urlSession(_:didReceive:completionHandler:)` is where pinning validation is implemented: run the default trust evaluation with `SecTrustEvaluateWithError`, then compare the public keys in the certificate chain with the pinned keys (see the example)
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
    // Only handle server-trust challenges; let the system handle other kinds (client certs, HTTP auth...) by default
    guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
          let serverTrust = challenge.protectionSpace.serverTrust else {
        completionHandler(.performDefaultHandling, nil)
        return
    }

    // 1. Run the default trust evaluation first: CA chain, expiry, hostname. Without it, an expired/wrong-domain cert still passes if the key matches
    guard SecTrustEvaluateWithError(serverTrust, nil) else {
        completionHandler(.cancelAuthenticationChallenge, nil)
        return
    }

    // 2. Only then compare pins: SecTrustCopyCertificateChain (iOS 15+) replaces the deprecated SecTrustGetCertificateAtIndex
    let chain = (SecTrustCopyCertificateChain(serverTrust) as? [SecCertificate]) ?? []
    let matchesPin = chain.contains { certificate in
        guard let key = SecCertificateCopyKey(certificate),
              let keyData = SecKeyCopyExternalRepresentation(key, nil) as Data? else {
            return false
        }
        // pinnedPublicKeys: Set<Data> holds the current key + a backup key. This is the raw key from
        // SecKeyCopyExternalRepresentation, NOT the SPKI; to compare against SPKI hashes (as NSPinnedDomains uses)
        // you must prepend the ASN.1 header for the key type and then hash with SHA-256
        return pinnedPublicKeys.contains(keyData)
    }

    if matchesPin {
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

## Practice Question Answers

### Why is pinning the public key generally preferred over pinning the leaf certificate?

Because certificates are replaced regularly while the public key can stay the same across many renewals, so pinning the key keeps the app from breaking every time the backend swaps its certificate.

How it works: a certificate consists of a public key plus information such as the domain name, expiry date and the CA's signature. On renewal, the CA signs a new certificate — completely different bytes — so a pin on the hash of the whole cert fails immediately. But if the team generates the new CSR from the same key pair, the public key (and its SPKI hash) does not change, so the pin still matches. This matters more and more as certificate lifetimes shrink: Let's Encrypt issues 90-day certificates, and the CA/Browser Forum has approved a schedule that gradually reduces the maximum lifetime to 47 days by 2029.

In practice:
- Pin the SHA-256 hash of the SubjectPublicKeyInfo, and always have at least one backup key.
- Run the default trust evaluation (`SecTrustEvaluateWithError`) first, then compare pins — in the same order as the example in this file.
- Since iOS 14 you can declare `NSPinnedDomains` in `Info.plist` instead of writing a delegate yourself.

Trade-off: pinning an intermediate CA's key is even more durable (independent of the server's key), but then every cert that CA issues for your domain is trusted — weaker protection. And pinning by key means you cannot rotate keys casually; if the key is compromised, you need a backup pin already shipped in the app.

### What is your rollback plan if a pinned key needs to change on short notice (e.g., a CA compromise)?

The plan must exist before the incident: the app versions already in the field must contain backup pins, because when you need to switch urgently you cannot wait for every user to update.

Layers of the plan:
1. **Backup pins in every build**: besides the key in use, the app pins at least one backup key that was generated ahead of time, stored offline and never used on a server — ideally with a different CA. When the current key or CA has a problem, the backend switches to a cert using the backup key and old app versions keep connecting.
2. **Ship a new app version** with a new pin set (the new key as primary plus a new backup), together with a minimum-version force-update mechanism to retire old versions.
3. **A controlled kill switch**: a signed remote config (verified with a key embedded in the app) that can disable pinning for a domain in an emergency. It must never arrive over an unverified channel, or an attacker could disable pinning too.
4. **Monitoring**: log and report pin failures per app version to catch problems early, before they become an outage.
5. **An upgrade path**: the version-check endpoint should keep working when pinning fails, so the app can at least tell the user to update.

Trade-off: each layer reduces the risk of hard-locking the app but loosens part of the protection (a kill switch is a new attack surface). For many apps, pinning a CA or relying on ATS plus Certificate Transparency is enough; pinning is only really worth it when the threat model (banking, healthcare) demands it.

## Interview Traps

### Is it enough for pinning code to compare the server's public key with the pinned key?

**Common wrong answer:** "Yes, if the key matches, it is the real server."

**Better answer:** If you only compare the key and skip the system's trust evaluation, the app will accept an expired certificate, a wrong hostname or a revoked cert, as long as the key matches. Call `SecTrustEvaluateWithError(serverTrust, nil)` first, then check pins against the certificate chain. Also, `SecTrustGetCertificateAtIndex` has been deprecated since iOS 15, so use `SecTrustCopyCertificateChain`; and the delegate should only handle `NSURLAuthenticationMethodServerTrust`, returning `.performDefaultHandling` for other challenge types.

### Does pinning stop someone from using Charles/Proxyman to read your app's API traffic?

**Common wrong answer:** "Yes, once you pin, nobody can MITM the app anymore."

**Better answer:** Pinning protects users from an attacker in the middle of the connection (public Wi-Fi, a rogue CA), but not from someone who controls the device itself: on a jailbroken device, tools like Frida can hook and disable the pinning logic. So do not treat your API as "secret" just because you pin; real security has to live on the server (authentication, authorization, rate limiting), optionally with App Attest to verify requests come from your genuine app.

### Does ATS protect every network connection in the app?

**Common wrong answer:** "Yes, ATS is on by default for the whole app."

**Better answer:** ATS applies to the URL Loading System (`URLSession` and APIs built on it); it does not apply to lower-level APIs such as the Network framework (`NWConnection`) or sockets, and web content has its own key, `NSAllowsArbitraryLoadsInWebContent`. Third-party SDKs with their own network stack can bypass ATS. To guarantee a TLS baseline on those paths, you must configure TLS yourself or review the SDK. Also, using `NSAllowsArbitraryLoads` requires a justification during App Store review.

## Exercise

Write the ATS exception justification you'd bring to a security review for allowing a single third-party analytics domain to use TLS 1.0. State the specific risk this introduces and the compensating control (e.g., scope of data sent to that domain) you'd propose instead of a blanket ATS opt-out. Note: Apple deprecated TLS 1.0/1.1 in iOS 15 and announced they will be removed in a future release, so this exception may stop working on newer iOS versions — another risk to state.
