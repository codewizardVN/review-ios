[English](./Keychain.md) | [Tiếng Việt](./Keychain.vi.md)

[← Security](./README.md)

# Keychain

## Key Idea

Keychain is the appropriate place to store secrets on iOS — tokens, passwords, refresh tokens. `UserDefaults` is just a plist file inside the app container: it is not encrypted on its own (only by the file system's default Data Protection), it is included in backups and can be read on a jailbroken device or from a backup, so it must never hold credentials. The same goes for plain files unless you encrypt them yourself.

## What To Review

- `kSecClassGenericPassword` / `kSecClassInternetPassword` — item classes
- `kSecAttrAccessible*` — decides when the item is readable, which directly affects background access:
  - `kSecAttrAccessibleWhenUnlocked` (the default if you do not specify one): readable only while the device is unlocked.
  - `kSecAttrAccessibleAfterFirstUnlock`: readable any time after the first unlock since the device booted — needed for tasks that run in the background.
  - `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly`: readable only while unlocked and only if the device has a passcode; if the user removes the passcode, the item is deleted.
  - The `...ThisDeviceOnly` variants (for example `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`, `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`): the item is not included in backups and is not migrated to a new device.
  - `kSecAttrAccessibleAlways` and `kSecAttrAccessibleAlwaysThisDeviceOnly` have been deprecated since iOS 12; do not use them.
- `kSecAttrAccessControl` with `SecAccessControlCreateFlags` — require biometric (`.biometryCurrentSet`) or device passcode to read an item
- Keychain items survive app deletion by default — decide whether that is desired (usually not, for session tokens)
- Keychain sharing across app extensions via access groups (`kSecAttrAccessGroup`)

## Example

```swift
enum KeychainError: Error {
    case unableToSave(OSStatus)
}

func saveToken(_ token: String, service: String, account: String) throws {
    // The query holds only the attributes that identify the item: class + service + account
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: service,
        kSecAttrAccount as String: account
    ]
    // The data and attributes to write (ThisDeviceOnly: not in backups, not migrated to a new device)
    let attributes: [String: Any] = [
        kSecValueData as String: Data(token.utf8),
        kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
    ]

    // 1. Try to add first
    let addQuery = query.merging(attributes) { _, new in new }
    let addStatus = SecItemAdd(addQuery as CFDictionary, nil)

    switch addStatus {
    case errSecSuccess:
        return
    case errSecDuplicateItem:
        // 2. The item already exists → update it in place; there is never a moment without a token, unlike delete-then-add
        let updateStatus = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        guard updateStatus == errSecSuccess else { throw KeychainError.unableToSave(updateStatus) }
    default:
        throw KeychainError.unableToSave(addStatus)
    }
}
```

## Practice Questions

- Why would you choose `AfterFirstUnlock` over `WhenUnlocked` for a token needed by a background refresh task?
- What must you do explicitly so a token does not silently persist after the user deletes and reinstalls the app?

## Senior Take

The common mistake is not "not using Keychain" — it's using the wrong accessibility level and access control, which either breaks background functionality (token unreadable before first unlock) or over-exposes secrets (readable even when device is locked). Also: explicitly delete Keychain items on logout — they are not tied to the app's own lifecycle by default.

## Practice Question Answers

### Why would you choose `AfterFirstUnlock` over `WhenUnlocked` for a token needed by a background refresh task?

Because a `WhenUnlocked` item can only be read while the device is unlocked, whereas background refresh often runs while the device is locked; an `AfterFirstUnlock` item can be read any time after the first unlock since the device booted.

How it works: Keychain encrypts each item with a class key chosen by its accessibility level. For `WhenUnlocked`, the class key is discarded from memory shortly after the device locks (with a few seconds' delay), so `SecItemCopyMatching` called from a `BGAppRefreshTask` or a silent push at that point returns `errSecInteractionNotAllowed`. The silent refresh fails and the user opens the app to find their session expired. For `AfterFirstUnlock`, the class key stays in memory from the first unlock after boot until the device is shut down, so the background task can read the token.

Prefer the `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` variant so the token is not included in backups or migrated to a new device — a session token should be tied to one device.

Trade-off: `AfterFirstUnlock` is weaker — if the device is taken while locked but after it has been unlocked once since boot, the secret can in theory still be decrypted. So use this level only for tokens that genuinely need background access. Secrets that are not needed in the background (like a biometric-protected refresh token) should use `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` or `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly`.

### What must you do explicitly so a token does not silently persist after the user deletes and reinstalls the app?

You must detect "this is the first run after install" yourself and delete the app's Keychain items, because iOS keeps Keychain items after the app is deleted.

How it works: Keychain lives outside the app's sandbox container. Deleting the app removes the container (including `UserDefaults`, files and databases), but Keychain items remain, and a reinstalled app with the same team/access group can read them. If you do nothing, a user who reinstalls is automatically signed in with the old token — surprising, and dangerous if the device has changed hands.

A common approach is a flag in `UserDefaults` (which is wiped with the app) to detect the first run:

```swift
let key = "hasLaunchedBefore"
if UIApplication.shared.isProtectedDataAvailable,
   !UserDefaults.standard.bool(forKey: key) {
    try? tokenStore.deleteAll()
    UserDefaults.standard.set(true, forKey: key)
}
```

In addition, logout must explicitly delete both the access token and the refresh token. Note that `ThisDeviceOnly` does not help here — it only keeps the item out of backups; it does not delete it with the app. And do not make session tokens `kSecAttrSynchronizable` (iCloud Keychain), because then they also appear on the user's other devices.

Trade-off: sometimes you do want something to survive a reinstall (for example an anonymous device ID for abuse prevention); in that case exclude that item from the deletion logic.

## Interview Traps

### What is wrong with upserting via `SecItemDelete` followed by `SecItemAdd`?

**Common wrong answer:** "Nothing, delete the old one and add the new one is the simplest way."

**Better answer:** Between the two calls there is a window with no token, so other code reading at that moment will think the user is logged out; if `SecItemAdd` fails, the old token is already gone. The result of `SecItemDelete` is also ignored. The standard approach is an upsert without deleting: as the example in this file does, call `SecItemAdd` first and, on `errSecDuplicateItem`, call `SecItemUpdate` with a query that finds the item (class + service + account) and a dictionary of attributes to change; or the other way round — `SecItemUpdate` first, and `SecItemAdd` only on `errSecItemNotFound`. Any other status must be thrown, not ignored. Route all access through a single type (for example an actor `TokenStore`) to avoid races.

### If the refresh token is protected with `.biometryCurrentSet`, does background silent refresh still work?

**Common wrong answer:** "Yes, biometrics just make the item more secure."

**Better answer:** Reading an item with biometric access control requires a Face ID/Touch ID prompt, and a background task cannot interact with the user, so the read fails and silent refresh cannot run. Also, with `.biometryCurrentSet`, when the user adds or removes a fingerprint/face, the item is permanently invalidated and the user must sign in again — that is a security feature, but the app must handle it. A common design: the access token is readable in the background, while the biometric-protected refresh token is only used while the user has the app open.

### Does reading Keychain right at app launch always succeed?

**Common wrong answer:** "Yes, if the token is there, you can read it."

**Better answer:** The app can be launched before the user's first unlock after boot (prewarming, or a background launch from a push or location event), when protected data is not yet available: Keychain items return `errSecInteractionNotAllowed`, and protected files, including `UserDefaults`, may read back as empty. If your code treats "could not read" as "no token", it logs the user out — or worse, assumes a fresh install and wipes the Keychain. Distinguish `errSecItemNotFound` from other errors, and check `isProtectedDataAvailable` before running any deletion logic.

## Exercise

Design a `TokenStore` protocol with `save`, `read`, and `delete`, backed by Keychain. Require biometric authentication to read the refresh token specifically (not the access token). Explain which `kSecAttrAccessible` value you chose for each token type and why a background silent-refresh feature would or would not work with your choice.
