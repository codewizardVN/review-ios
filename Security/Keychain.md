[English](./Keychain.md) | [Tiếng Việt](./Keychain.vi.md)

[← Security](./README.md)

# Keychain

## Key Idea

Keychain is the only appropriate place to store secrets on iOS — tokens, passwords, refresh tokens. `UserDefaults` and plain files are not encrypted at rest for this purpose and should never hold credentials.

## What To Review

- `kSecClassGenericPassword` / `kSecClassInternetPassword` — item classes
- `kSecAttrAccessible*` — when the item is readable (`WhenUnlocked`, `AfterFirstUnlock`, `WhenPasswordSetByUser`), affects background access
- `kSecAttrAccessControl` with `SecAccessControlCreateFlags` — require biometric (`.biometryCurrentSet`) or device passcode to read an item
- Keychain items survive app deletion by default — decide whether that is desired (usually not, for session tokens)
- Keychain sharing across app extensions via access groups (`kSecAttrAccessGroup`)

## Example

```swift
func saveToken(_ token: String, service: String, account: String) throws {
    let data = Data(token.utf8)
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: service,
        kSecAttrAccount as String: account,
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock
    ]
    SecItemDelete(query as CFDictionary)
    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else { throw KeychainError.unableToSave(status) }
}
```

## Practice Questions

- Why would you choose `AfterFirstUnlock` over `WhenUnlocked` for a token needed by a background refresh task?
- What must you do explicitly so a token does not silently persist after the user deletes and reinstalls the app?

## Senior Take

The common mistake is not "not using Keychain" — it's using the wrong accessibility level and access control, which either breaks background functionality (token unreadable before first unlock) or over-exposes secrets (readable even when device is locked). Also: explicitly delete Keychain items on logout — they are not tied to the app's own lifecycle by default.

## Exercise

Design a `TokenStore` protocol with `save`, `read`, and `delete`, backed by Keychain. Require biometric authentication to read the refresh token specifically (not the access token). Explain which `kSecAttrAccessible` value you chose for each token type and why a background silent-refresh feature would or would not work with your choice.
