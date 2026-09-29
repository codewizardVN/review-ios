[English](./ObjCInterop.md) | [Tiếng Việt](./ObjCInterop.vi.md)

[← Swift Core](./README.vi.md)

# Objective-C Interop

## Ý chính

Phần lớn vị trí senior sẽ đụng vào một codebase không phải pure Swift. Interop là việc biết chính xác feature nào của Swift còn sống sót khi bắc cầu sang Objective-C, và tại sao một cơ chế runtime bạn đang dựa vào (dynamic dispatch, KVO, selector) đôi khi âm thầm ngừng hoạt động.

## Những điều cần nắm

- `@objc` và `@objcMembers` — expose một khai báo Swift cho Objective-C runtime; bắt buộc cho selector, KVO, và action trong Interface Builder
- Bridging header — cách một project mixed-target expose header Objective-C cho Swift (`-Bridging-Header.h`) và khai báo Swift cho Objective-C (file `-Swift.h` tự sinh)
- Cái gì không bridge được — generic thuần Swift, enum có associated value, struct tự định nghĩa (khác với các type được bridge sẵn như `String`, `Array`, `Dictionary`, `Date`, `URL`), và protocol extension không có đại diện tương ứng trong Objective-C
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
// Gọi từ Swift — completion trở thành (String?, Error?) -> Void.
// Vì completion theo đúng quy ước, compiler còn tự sinh thêm bản
// `func fetchToken() async throws -> String` để gọi bằng `try await`.
LegacySessionManager.shared().fetchToken { token, error in
    guard let token else { return }
    self.session = token
}
```

## Câu hỏi luyện tập

- Một method `@objc private` gọi qua `perform(_:)` có chạy được không, và khi nào lời gọi `perform` mới thật sự crash với "unrecognized selector"?
- Chuyện gì xảy ra nếu quên `NS_ASSUME_NONNULL_BEGIN` trong một header legacy mà module Swift import?
- Tại sao một `enum` Swift có associated value không thể expose cho Objective-C?

## Góc nhìn Senior

Câu hỏi interop kiểm tra xem bạn có hiểu Swift và Objective-C là hai mô hình dispatch và type khác nhau được ghép lại, chứ không phải một ngôn ngữ với hai cú pháp. Câu trả lời tốt gọi tên đúng ranh giới (cái gì qua được, cái gì không, vì sao) thay vì chỉ nói "thêm `@objc` là chạy". Nửa còn lại của câu trả lời senior là một kế hoạch migrate: cô lập Objective-C legacy sau một protocol Swift nhỏ để phần còn lại của codebase không bao giờ phải suy nghĩ về cái cầu nối đó nữa.

## Đáp án câu hỏi luyện tập

### Một method `@objc private` gọi qua `perform(_:)` có chạy được không, và khi nào lời gọi `perform` mới thật sự crash với "unrecognized selector"?

Câu trả lời thẳng: có, nó chạy bình thường. Bản thân `private` không làm nó fail, vì access control chỉ tồn tại lúc compile của Swift, còn Objective-C runtime không biết gì về nó. Một `@objc private func` vẫn được đăng ký selector; pattern target-action `@objc private func didTap()` chạy bình thường hằng ngày.

Khi thật sự gặp crash "unrecognized selector sent to instance", nguyên nhân thường là một trong các trường hợp sau, và `private` chỉ là chi tiết gây nhiễu:
- Method thiếu `@objc` (ví dụ ai đó xóa `@objc` vì nghĩ `private` thì không cần). Từ Swift 4, subclass `NSObject` không còn tự suy ra `@objc`, nên method không có trong runtime.
- Selector dựng từ string sai tên. `@objc private func load(id: String)` có selector là `loadWithId:`, không phải `"load"` hay `"load:"`.
- Gọi `perform` trên sai object (ví dụ target của action bị gán nhầm sang một object không có method đó).

```swift
perform(Selector("load"))              // crash: selector không tồn tại
perform(#selector(load(id:)), with: id) // compiler kiểm tra tên
```

Cách phòng tránh là luôn dùng `#selector(...)`, vì compiler kiểm tra method có tồn tại và có `@objc` không. Nói thêm về trade-off: `perform(_:)` chỉ truyền được object, không truyền được `Int` hay struct một cách an toàn, và bỏ qua type checking. Trong code Swift mới, closure hoặc protocol gần như luôn tốt hơn.

### Chuyện gì xảy ra nếu quên `NS_ASSUME_NONNULL_BEGIN` trong một header legacy mà module Swift import?

Mọi pointer không có annotation sẽ được import thành implicitly unwrapped optional (`String!`, `LegacySessionManager!`), nghĩa là Swift không biết giá trị có thể `nil` hay không.

Cơ chế: Objective-C cho phép mọi pointer là `nil`. Khi header không nói gì, Swift không thể đoán, nên nó chọn IUO làm thỏa hiệp: code compile được như non-optional, nhưng nếu giá trị thật sự là `nil` thì app crash ngay tại chỗ dùng. Với header trong ví dụ, `+ (instancetype)shared` sẽ thành `LegacySessionManager!` thay vì `LegacySessionManager`.

Hệ quả thực tế:
- API Swift trông an toàn nhưng không an toàn; lỗi `nil` xuất hiện lúc runtime thay vì lúc compile.
- IUO lan ra code Swift gọi nó, dễ bị truyền tiếp vào chỗ khác.
- Nếu header chỉ annotate một phần, clang cảnh báo "pointer is missing a nullability type specifier".

Cách sửa: bọc header bằng `NS_ASSUME_NONNULL_BEGIN/END`, rồi chỉ đánh dấu `_Nullable` ở những chỗ thật sự có thể `nil`, như `token` và `error` trong completion. Trade-off: annotation phải đúng sự thật. Đánh dấu `nonnull` cho một giá trị thật ra có thể `nil` còn nguy hiểm hơn để IUO.

### Tại sao một `enum` Swift có associated value không thể expose cho Objective-C?

Vì enum của Objective-C chỉ là enum của C, tức là một số nguyên có tên, không có chỗ nào để chứa dữ liệu đi kèm.

Cơ chế: `@objc enum` chỉ được phép khi có raw type là kiểu số nguyên (`Int`, `UInt8`...), và nó được import thành `NS_ENUM`, về bản chất là một hằng số. Enum có associated value trong Swift là một kiểu dữ liệu khác hẳn: mỗi case mang payload riêng với type riêng (`case success(User)`, `case failure(Error)`), và layout bộ nhớ do Swift quyết định. Objective-C không có khái niệm tương đương, nên compiler từ chối `@objc` cho enum đó.

Các cách vượt ranh giới:
- Tách thành một `@objc enum` chỉ chứa "loại" (kind) cộng với các property optional mang dữ liệu.
- Bọc bằng một class `NSObject` có factory method cho từng case.
- Dùng hai callback hoặc tham số `(value, error)` như completion trong ví dụ.

```swift
@objc enum LoadStateKind: Int { case idle, loading, loaded, failed }
```

Trade-off: mỗi cách đều làm mất tính "exhaustive" và type safety của enum Swift. Chỉ nên tạo lớp vỏ này ở ranh giới interop, còn bên trong Swift vẫn giữ enum gốc.

## Bẫy phỏng vấn

### "Thêm `@objc` là đủ để swizzle method hoặc observe property bằng KVO?"

**Dễ trả lời sai:** "Đủ, `@objc` nghĩa là method dùng Objective-C message dispatch." `@objc` chỉ expose method cho runtime, không đổi cách Swift gọi nó.

**Nên trả lời:** Với `@objc` không có `dynamic`, code Swift gọi method đó vẫn có thể dùng vtable hoặc static dispatch, thậm chí bị inline, nên swizzle chỉ có tác dụng với caller Objective-C. KVO cũng vậy: property phải là `@objc dynamic var` thì setter mới đi qua `objc_msgSend` để KVO chèn notification vào. Thiếu `dynamic`, `observe(\.x)` có thể âm thầm không bao giờ được gọi.

### "Class kế thừa `NSObject` thì mọi method đều gọi được từ Objective-C?"

**Dễ trả lời sai:** "Đúng, subclass `NSObject` tự động expose hết." Điều này chỉ đúng trước Swift 4.

**Nên trả lời:** Từ Swift 4 (SE-0160), compiler không còn tự suy ra `@objc` cho member của subclass `NSObject`, trừ các trường hợp như override method Objective-C hoặc implement `@objc` protocol. Muốn expose cả class thì dùng `@objcMembers`, nhưng việc này làm binary lớn hơn và tăng thời gian load, nên tốt hơn là đánh dấu `@objc` từng member cần thiết.

### "Header đã annotate `_Nonnull` rồi thì Swift không bao giờ nhận `nil`?"

**Dễ trả lời sai:** "Không bao giờ, annotation được compiler đảm bảo." Annotation chỉ là lời hứa, không được kiểm tra lúc runtime.

**Nên trả lời:** Clang không chặn được implementation Objective-C trả về `nil` cho một giá trị đã khai báo `nonnull`. Swift tin annotation nên coi giá trị là non-optional, và khi `nil` thật sự đi qua thì kết quả tùy type: có thể crash, có thể hành vi không xác định, hoặc âm thầm sai (ví dụ `NSString` nil được bridge thành `String` rỗng), thường ở một chỗ khó liên hệ với nguyên nhân. Với code legacy không chắc chắn, an toàn hơn là khai báo `_Nullable` rồi xử lý optional ở lớp wrapper Swift.

## Bài tập

Một singleton `AnalyticsManager` Objective-C legacy đang được 40 view controller gọi trực tiếp qua static call. Thiết kế một protocol Swift `AnalyticsTracking` bọc nó, giải thích method Objective-C nào có thể và không thể map gọn sang chữ ký Swift idiomatic (ví dụ method có payload `NSDictionary *` chứa kiểu hỗn hợp), và mô tả kế hoạch rollout để cả call site cũ lẫn mới đều chạy được trong lúc migrate.
