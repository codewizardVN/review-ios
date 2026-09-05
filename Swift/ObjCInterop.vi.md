[English](./ObjCInterop.md) | [Tiếng Việt](./ObjCInterop.vi.md)

[← Swift Core](./README.vi.md)

# Objective-C Interop

## Ý chính

Phần lớn vị trí senior sẽ đụng vào một codebase không phải pure Swift. Interop là việc biết chính xác feature nào của Swift còn sống sót khi bắc cầu sang Objective-C, và tại sao một cơ chế runtime bạn đang dựa vào (dynamic dispatch, KVO, selector) đôi khi âm thầm ngừng hoạt động.

## Những điều cần nắm

- `@objc` và `@objcMembers` — expose một khai báo Swift cho Objective-C runtime; bắt buộc cho selector, KVO, và action trong Interface Builder
- Bridging header — cách một project mixed-target expose header Objective-C cho Swift (`-Bridging-Header.h`) và khai báo Swift cho Objective-C (file `-Swift.h` tự sinh)
- Cái gì không bridge được — generic thuần Swift, enum có associated value, struct, và protocol extension không có đại diện tương ứng trong Objective-C
- `dynamic` — ép dùng Objective-C message dispatch thay vì static/vtable dispatch của Swift, cần cho method swizzling và một số đường KVO
- Subclass `NSObject` — cần cho các API đòi hỏi identity kiểu Objective-C (`isEqual:`, `hash`, `NSCoding`, nhiều delegate protocol có từ trước Swift)
- An toàn của selector — `#selector(...)` được compile-time check, nhưng selector dựng từ string, hoặc method chưa từng đánh dấu `@objc`, sẽ fail âm thầm hoặc crash lúc runtime
- Nullability annotation (`_Nullable`, `_Nonnull`, `NS_ASSUME_NONNULL_BEGIN`) — header Objective-C trở thành optional hay implicitly-unwrapped optional trong Swift ra sao
- Chiến lược migrate dần — bọc singleton Objective-C legacy sau một protocol Swift để code mới không bao giờ đụng trực tiếp vào type cũ

## Ví dụ

```objc
// Legacy.h
NS_ASSUME_NONNULL_BEGIN
@interface LegacySessionManager : NSObject
+ (instancetype)shared;
- (void)fetchTokenWithCompletion:(void (^)(NSString * _Nullable token, NSError * _Nullable error))completion;
@end
NS_ASSUME_NONNULL_END
```

```swift
// Gọi từ Swift — completion trở thành (String?, Error?) -> Void
LegacySessionManager.shared().fetchToken { token, error in
    guard let token else { return }
    self.session = token
}
```

## Câu hỏi luyện tập

- Tại sao một method `@objc` đánh dấu `private` lại fail lúc runtime khi gọi qua `perform(_:)`?
- Chuyện gì xảy ra nếu quên `NS_ASSUME_NONNULL_BEGIN` trong một header legacy mà module Swift import?
- Tại sao một `enum` Swift có associated value không thể expose cho Objective-C?

## Góc nhìn Senior

Câu hỏi interop kiểm tra xem bạn có hiểu Swift và Objective-C là hai mô hình dispatch và type khác nhau được ghép lại, chứ không phải một ngôn ngữ với hai cú pháp. Câu trả lời tốt gọi tên đúng ranh giới (cái gì qua được, cái gì không, vì sao) thay vì chỉ nói "thêm `@objc` là chạy". Nửa còn lại của câu trả lời senior là một kế hoạch migrate: cô lập Objective-C legacy sau một protocol Swift nhỏ để phần còn lại của codebase không bao giờ phải suy nghĩ về cái cầu nối đó nữa.

## Bài tập

Một singleton `AnalyticsManager` Objective-C legacy đang được 40 view controller gọi trực tiếp qua static call. Thiết kế một protocol Swift `AnalyticsTracking` bọc nó, giải thích method Objective-C nào có thể và không thể map gọn sang chữ ký Swift idiomatic (ví dụ method có payload `NSDictionary *` chứa kiểu hỗn hợp), và mô tả kế hoạch rollout để cả call site cũ lẫn mới đều chạy được trong lúc migrate.
