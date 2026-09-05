[English](./Keychain.md) | [Tiếng Việt](./Keychain.vi.md)

[← Security](./README.vi.md)

# Keychain

## Ý chính

Keychain là nơi duy nhất phù hợp để lưu secret trên iOS — token, password, refresh token. `UserDefaults` và file thường không được mã hóa at-rest cho mục đích này và không bao giờ nên chứa credential.

## Những điều cần nắm

- `kSecClassGenericPassword` / `kSecClassInternetPassword` — các item class
- `kSecAttrAccessible*` — khi nào item có thể đọc được (`WhenUnlocked`, `AfterFirstUnlock`, `WhenPasswordSetByUser`), ảnh hưởng đến truy cập ở background
- `kSecAttrAccessControl` với `SecAccessControlCreateFlags` — yêu cầu biometric (`.biometryCurrentSet`) hoặc passcode thiết bị để đọc item
- Keychain item mặc định tồn tại sau khi xóa app — cần quyết định có muốn vậy không (thường là không, với session token)
- Keychain sharing giữa các app extension qua access group (`kSecAttrAccessGroup`)

## Ví dụ

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

## Câu hỏi luyện tập

- Tại sao bạn sẽ chọn `AfterFirstUnlock` thay vì `WhenUnlocked` cho một token cần dùng bởi background refresh task?
- Bạn cần làm gì tường minh để token không âm thầm còn tồn tại sau khi user xóa và cài lại app?

## Góc nhìn Senior

Lỗi phổ biến không phải là "không dùng Keychain" — mà là dùng sai accessibility level và access control, khiến hoặc là gãy chức năng background (token không đọc được trước lần unlock đầu tiên), hoặc là lộ secret quá mức (đọc được ngay cả khi máy đang khóa). Ngoài ra: phải xóa tường minh Keychain item khi logout — chúng không tự gắn với vòng đời của app theo mặc định.

## Bài tập

Thiết kế một protocol `TokenStore` với `save`, `read`, `delete`, dùng Keychain làm nền. Yêu cầu xác thực biometric để đọc riêng refresh token (không phải access token). Giải thích bạn chọn giá trị `kSecAttrAccessible` nào cho mỗi loại token và tại sao một tính năng silent-refresh ở background sẽ hoạt động hoặc không hoạt động với lựa chọn đó.
