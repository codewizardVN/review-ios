[English](./Keychain.md) | [Tiếng Việt](./Keychain.vi.md)

[← Security](./README.vi.md)

# Keychain

## Ý chính

Keychain là nơi phù hợp để lưu secret trên iOS — token, password, refresh token. `UserDefaults` chỉ là một file plist trong container của app: nó không được mã hóa riêng (chỉ có Data Protection mặc định của hệ thống file), đi vào backup và có thể bị đọc trên máy jailbreak hoặc từ bản backup, nên không bao giờ được chứa credential. File thường cũng vậy, trừ khi bạn tự mã hóa.

## Những điều cần nắm

- `kSecClassGenericPassword` / `kSecClassInternetPassword` — các item class
- `kSecAttrAccessible*` — quyết định khi nào item đọc được, ảnh hưởng trực tiếp đến truy cập ở background:
  - `kSecAttrAccessibleWhenUnlocked` (mặc định nếu không chỉ định): chỉ đọc được khi máy đang mở khóa.
  - `kSecAttrAccessibleAfterFirstUnlock`: đọc được bất cứ lúc nào sau lần mở khóa đầu tiên kể từ khi bật máy — cần cho task chạy ở background.
  - `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly`: chỉ đọc được khi máy mở khóa và máy có đặt passcode; nếu user gỡ passcode thì item bị xóa.
  - Các biến thể `...ThisDeviceOnly` (ví dụ `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`, `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`): item không đi vào backup và không được chuyển sang máy mới.
  - `kSecAttrAccessibleAlways` và `kSecAttrAccessibleAlwaysThisDeviceOnly` đã deprecated từ iOS 12, không dùng.
- `kSecAttrAccessControl` với `SecAccessControlCreateFlags` — yêu cầu biometric (`.biometryCurrentSet`) hoặc passcode thiết bị để đọc item
- Keychain item mặc định tồn tại sau khi xóa app — cần quyết định có muốn vậy không (thường là không, với session token)
- Keychain sharing giữa các app extension qua access group (`kSecAttrAccessGroup`)

## Ví dụ

```swift
enum KeychainError: Error {
    case unableToSave(OSStatus)
}

func saveToken(_ token: String, service: String, account: String) throws {
    // Query chỉ gồm các attribute định danh item: class + service + account
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: service,
        kSecAttrAccount as String: account
    ]
    // Dữ liệu và attribute muốn ghi (ThisDeviceOnly: không đi vào backup, không chuyển sang máy mới)
    let attributes: [String: Any] = [
        kSecValueData as String: Data(token.utf8),
        kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
    ]

    // 1. Thử add trước
    let addQuery = query.merging(attributes) { _, new in new }
    let addStatus = SecItemAdd(addQuery as CFDictionary, nil)

    switch addStatus {
    case errSecSuccess:
        return
    case errSecDuplicateItem:
        // 2. Item đã tồn tại → cập nhật tại chỗ; không có lúc nào token biến mất như delete-rồi-add
        let updateStatus = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        guard updateStatus == errSecSuccess else { throw KeychainError.unableToSave(updateStatus) }
    default:
        throw KeychainError.unableToSave(addStatus)
    }
}
```

## Câu hỏi luyện tập

- Tại sao bạn sẽ chọn `AfterFirstUnlock` thay vì `WhenUnlocked` cho một token cần dùng bởi background refresh task?
- Bạn cần làm gì tường minh để token không âm thầm còn tồn tại sau khi user xóa và cài lại app?

## Góc nhìn Senior

Lỗi phổ biến không phải là "không dùng Keychain" — mà là dùng sai accessibility level và access control, khiến hoặc là gãy chức năng background (token không đọc được trước lần unlock đầu tiên), hoặc là lộ secret quá mức (đọc được ngay cả khi máy đang khóa). Ngoài ra: phải xóa tường minh Keychain item khi logout — chúng không tự gắn với vòng đời của app theo mặc định.

## Đáp án câu hỏi luyện tập

### Tại sao bạn sẽ chọn `AfterFirstUnlock` thay vì `WhenUnlocked` cho một token cần dùng bởi background refresh task?

Vì item `WhenUnlocked` chỉ đọc được khi máy đang mở khóa, trong khi background refresh thường chạy lúc máy đang khóa; còn item `AfterFirstUnlock` đọc được bất cứ lúc nào sau lần mở khóa đầu tiên kể từ khi khởi động máy.

Cơ chế: Keychain mã hóa mỗi item bằng một class key tùy theo mức accessibility. Với `WhenUnlocked`, class key bị xóa khỏi memory ngay sau khi máy khóa (có trễ vài giây), nên `SecItemCopyMatching` gọi từ `BGAppRefreshTask` hay silent push lúc đó trả về `errSecInteractionNotAllowed`. Kết quả là silent refresh thất bại và user mở app ra thấy phiên đăng nhập đã hết hạn. Với `AfterFirstUnlock`, class key được giữ trong memory từ lần unlock đầu tiên sau khi boot cho tới khi tắt máy, nên task ở background đọc được token.

Nên dùng biến thể `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` để token không đi vào backup và không được chuyển sang máy mới — token phiên đăng nhập nên gắn với một thiết bị.

Trade-off: `AfterFirstUnlock` yếu hơn — nếu máy bị lấy khi đang khóa nhưng đã được unlock một lần từ lúc bật, về lý thuyết secret vẫn giải mã được. Vì vậy chỉ dùng mức này cho token thật sự cần ở background. Secret không cần ở background (như refresh token yêu cầu biometric) nên dùng `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` hoặc `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly`.

### Bạn cần làm gì tường minh để token không âm thầm còn tồn tại sau khi user xóa và cài lại app?

Bạn phải tự phát hiện "đây là lần chạy đầu tiên sau khi cài" và xóa Keychain item của app, vì iOS giữ lại Keychain item sau khi app bị xóa.

Cơ chế: Keychain nằm ngoài sandbox container của app. Xóa app thì container (gồm `UserDefaults`, file, database) mất, nhưng item Keychain vẫn còn, và app cài lại với cùng team/access group sẽ đọc được. Nếu không xử lý, user cài lại app sẽ tự động đăng nhập bằng token cũ — gây bất ngờ, và nguy hiểm nếu máy đã đổi chủ.

Cách phổ biến là dùng một cờ trong `UserDefaults` (mất khi xóa app) để phát hiện lần chạy đầu:

```swift
let key = "hasLaunchedBefore"
if UIApplication.shared.isProtectedDataAvailable,
   !UserDefaults.standard.bool(forKey: key) {
    try? tokenStore.deleteAll()
    UserDefaults.standard.set(true, forKey: key)
}
```

Thêm vào đó, logout phải xóa tường minh cả access token lẫn refresh token. Lưu ý `ThisDeviceOnly` không giúp gì ở đây — nó chỉ ngăn item đi vào backup, không làm item bị xóa cùng app. Và đừng đặt token phiên là `kSecAttrSynchronizable` (iCloud Keychain), vì khi đó nó còn xuất hiện trên các thiết bị khác của user.

Trade-off: có trường hợp muốn giữ lại qua lần cài lại (ví dụ một device ID ẩn danh để chống lạm dụng); khi đó tách riêng item đó ra khỏi logic xóa.

## Bẫy phỏng vấn

### Upsert bằng `SecItemDelete` rồi `SecItemAdd` có vấn đề gì?

**Dễ trả lời sai:** "Không có vấn đề, xóa cái cũ rồi thêm cái mới là cách đơn giản nhất."

**Nên trả lời:** Giữa hai lời gọi có một khoảng thời gian không có token, nên code khác đọc đúng lúc đó sẽ tưởng user đã logout; nếu `SecItemAdd` fail thì token cũ cũng đã mất. Kết quả của `SecItemDelete` cũng bị bỏ qua. Cách chuẩn là upsert không xóa: như ví dụ trong file, gọi `SecItemAdd` trước, nếu nhận `errSecDuplicateItem` thì gọi `SecItemUpdate` với query tìm item (class + service + account) và dictionary attribute cần đổi; hoặc làm ngược lại — `SecItemUpdate` trước, chỉ khi nhận `errSecItemNotFound` mới `SecItemAdd`. Lỗi nào khác cũng phải được throw, không bỏ qua. Nên gom mọi truy cập vào một type duy nhất (ví dụ actor `TokenStore`) để tránh race.

### Đặt refresh token sau `.biometryCurrentSet` thì silent refresh ở background còn chạy không?

**Dễ trả lời sai:** "Có, biometric chỉ làm item an toàn hơn thôi."

**Nên trả lời:** Đọc item có access control biometric cần hiện prompt Face ID/Touch ID, mà background task không thể tương tác với user, nên việc đọc thất bại và silent refresh không chạy được. Thêm nữa, với `.biometryCurrentSet`, khi user thêm hoặc xóa vân tay/khuôn mặt, item bị vô hiệu vĩnh viễn và user phải đăng nhập lại — đó là tính năng bảo mật, nhưng app phải xử lý được. Thiết kế thường gặp: access token đọc được ở background, còn refresh token sau biometric chỉ dùng khi user đang mở app.

### Đọc Keychain ngay lúc app launch có luôn thành công không?

**Dễ trả lời sai:** "Có, token có ở đó thì đọc được."

**Nên trả lời:** App có thể được launch trước khi user unlock máy lần đầu sau khi khởi động (prewarming, hoặc background launch do push hay location), lúc protected data chưa sẵn sàng: item Keychain trả về `errSecInteractionNotAllowed`, và file được bảo vệ, kể cả `UserDefaults`, có thể đọc về rỗng. Nếu code coi "không đọc được" là "không có token" thì sẽ logout user, hoặc tệ hơn, tưởng là lần cài mới và xóa sạch Keychain. Hãy phân biệt `errSecItemNotFound` với các lỗi khác, và kiểm tra `isProtectedDataAvailable` trước khi chạy logic xóa.

## Bài tập

Thiết kế một protocol `TokenStore` với `save`, `read`, `delete`, dùng Keychain làm nền. Yêu cầu xác thực biometric để đọc riêng refresh token (không phải access token). Giải thích bạn chọn giá trị `kSecAttrAccessible` nào cho mỗi loại token và tại sao một tính năng silent-refresh ở background sẽ hoạt động hoặc không hoạt động với lựa chọn đó.
