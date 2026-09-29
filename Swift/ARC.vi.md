[English](./ARC.md) | [Tiếng Việt](./ARC.vi.md)

[← Swift Core](./README.vi.md)

# ARC và Quản lý bộ nhớ

## 1. ARC

### Ý chính

ARC tự động theo dõi các strong reference và giải phóng object khi reference count của chúng về zero.

### Những điều quan trọng trong thực tế

- **Strong reference** (mặc định) giữ object tồn tại: mỗi strong reference làm tăng reference count, object chỉ được giải phóng khi không còn strong reference nào.
- **Weak reference** (`weak var`) không giữ object tồn tại: nó không tăng strong count, luôn là optional, và tự động thành `nil` khi object bị giải phóng.
- **Unowned reference** (`unowned`) cũng không giữ object tồn tại, nhưng không phải optional và giả định object vẫn còn sống mỗi khi bạn truy cập. Nếu object đã bị giải phóng mà vẫn truy cập, app crash (với `unowned(unsafe)` thì là undefined behavior).
- ARC không phải là garbage collector: việc tăng/giảm reference count được compiler chèn vào lúc compile, object được giải phóng ngay khi count về 0 (có thể đoán trước, không có "pause" như GC). Đổi lại, ARC không tự phát hiện và dọn retain cycle — đó là việc của lập trình viên.

### Ví dụ

```swift
final class Owner {
    var child: Child?
}

final class Child {
    weak var owner: Owner?
}
```

### Góc nhìn Senior

Điều quan trọng không phải là ghi nhớ các từ khóa. Đó là hiểu object ownership và lifecycle, đặc biệt trong delegates, closures, async tasks, và mối quan hệ view/controller.

---

## 2. Retain Cycles

### Những nơi thường xảy ra

- Closure capture `self` mạnh và closure đó lại được `self` lưu giữ (trực tiếp qua property, hoặc gián tiếp qua một object mà `self` sở hữu)
- Mối quan hệ delegate không có `weak`: A giữ B, B giữ `delegate` trỏ ngược về A
- Các callback tồn tại lâu dài (được lưu trong một singleton, service, hoặc cache) giữ object lâu hơn cần thiết
- Các pattern Timer / notification / observer: ví dụ `Timer.scheduledTimer(target:selector:...)` giữ strong reference tới `target`, và run loop lại giữ timer cho tới khi `invalidate()`; block-based `NotificationCenter.addObserver(forName:object:queue:using:)` giữ closure cho tới khi bạn remove observer token
- Async work (`Task`, callback của network) giữ strong reference đến object lâu hơn mong đợi — thường là kéo dài lifetime, và thành leak thật nếu công việc không bao giờ kết thúc

### Ví dụ

```swift
final class ProfileViewModel {
    var onUpdate: (() -> Void)?

    func bind() {
        onUpdate = { [weak self] in
            self?.reload()
        }
    }

    private func reload() {}
}
```

### Góc nhìn Senior

Đừng mù quáng viết `[weak self]` ở khắp nơi. Hãy giải thích tại sao capture tồn tại, ai sở hữu ai, và liệu `self` có thực sự cần tồn tại cho toàn bộ operation hay không.

## Câu hỏi luyện tập

- Bạn sẽ chứng minh retain cycle gây ra bởi completion closure của DataLoader capture self mạnh như thế nào, và tại sao [weak self] là cách sửa đúng thay vì unowned?

## Đáp án câu hỏi luyện tập

### Bạn sẽ chứng minh retain cycle gây ra bởi completion closure của DataLoader capture self mạnh như thế nào, và tại sao [weak self] là cách sửa đúng thay vì unowned?

Tôi chứng minh bằng cách tạo `DataLoader` trong một scope ngắn, gọi `load()`, rồi thấy `deinit` không bao giờ in ra sau khi scope kết thúc; sau khi thêm `[weak self]` thì `deinit` in ra ngay.

Cơ chế: `DataLoader` giữ strong reference tới closure qua property `onComplete`, còn closure lại capture `self` mạnh, tức là giữ strong reference ngược về `DataLoader`. Hai bên giữ nhau nên reference count không bao giờ về 0, dù bên ngoài không còn ai dùng. Ngoài `deinit`, có thể giữ một `weak var probe = loader` rồi kiểm tra `probe != nil` sau scope, hoặc mở Memory Graph Debugger của Xcode để thấy vòng tham chiếu.

```swift
weak var probe: DataLoader?
do {
    let loader = DataLoader()
    loader.load()
    probe = loader
}
print(probe == nil) // false khi có cycle, true sau khi sửa
```

`[weak self]` đúng vì closure không còn tăng strong count; khi `DataLoader` bị giải phóng, `self` trong closure tự thành `nil`. `unowned` giả định `self` chắc chắn còn sống mỗi khi closure chạy. Trong thực tế completion closure thường được truyền đi (vào URLSession, vào một callback async) và có thể chạy sau khi loader đã bị giải phóng — lúc đó truy cập `unowned` sẽ crash. Chỉ dùng `unowned` khi lifetime được đảm bảo rõ ràng, ví dụ closure chỉ do chính `self` sở hữu và gọi.

## Bẫy phỏng vấn

### "Mọi closure dùng self đều cần [weak self] đúng không?"

**Dễ trả lời sai:** Đúng, nên viết `[weak self]` ở mọi closure cho an toàn, kể cả trong `map`, `UIView.animate` hay `DispatchQueue.main.async`.

**Nên trả lời:** Retain cycle chỉ xảy ra khi closure được lưu lại (trực tiếp hoặc gián tiếp) bởi chính object mà nó capture. Closure non-escaping như `map` không thể gây cycle. `UIView.animate` hay `DispatchQueue.main.async` giữ `self` tạm thời cho tới khi closure chạy xong rồi thả ra — đó là kéo dài lifetime, không phải leak. Viết `[weak self]` tràn lan khiến code nhiều optional và có thể làm công việc cần thiết (lưu dữ liệu) bị bỏ qua âm thầm.

### "Task { } bên trong ViewModel có gây retain cycle không?"

**Dễ trả lời sai:** Không bao giờ, vì Task tự kết thúc; hoặc chỉ cần `[weak self]` rồi `guard let self` ở đầu là đủ.

**Nên trả lời:** Closure của `Task` capture `self` mạnh (Swift cho phép dùng implicit self trong đó). Với task ngắn thì chỉ là giữ `self` tới khi task xong. Nhưng nếu task chạy vô hạn, như `for await` trên một stream không kết thúc, thì task đang chạy giữ `self` sống mãi — dù bạn có lưu task trong property của `self` hay không — và `deinit`, nơi bạn định gọi `task.cancel()`, không bao giờ chạy. `[weak self]` rồi `guard let self` ngay đầu cũng không cứu được, vì strong reference đó sống suốt vòng lặp; phải unwrap `self` bên trong từng vòng lặp hoặc cancel task từ bên ngoài (ví dụ `onDisappear`, hoặc dùng modifier `.task` của SwiftUI).

### "guard let self = self trong closure [weak self] có tạo lại retain cycle không?"

**Dễ trả lời sai:** Có, vì nó tạo strong reference tới `self` nên cycle quay trở lại.

**Nên trả lời:** Không. Closure vẫn chỉ lưu một weak reference; `guard let self` tạo một strong reference cục bộ chỉ tồn tại trong một lần closure chạy, rồi được thả khi closure return. Nó còn có lợi: đảm bảo `self` không bị giải phóng giữa chừng khi đang chạy nhiều dòng code. Điểm cần nhớ chỉ là nếu phần thân closure chạy rất lâu (vòng lặp, await dài) thì `self` bị giữ suốt khoảng đó.

## Bài tập

Viết một class `DataLoader` fetch dữ liệu và gọi một completion closure. Cố tình tạo ra một retain cycle bằng cách để closure capture `self` mạnh và lưu closure đó như một property. Xác minh cycle tồn tại bằng cách dùng `deinit { print("deinit") }`. Sau đó fix nó bằng `[weak self]`. Giải thích trong comment tại sao weak là lựa chọn đúng ở đây (không phải unowned).

Bản cố tình có retain cycle (bug có chủ đích để quan sát):

```swift
final class DataLoader {
    var onComplete: (() -> Void)?

    func load() {
        // CỐ TÌNH SAI: self giữ closure qua onComplete, closure lại capture self mạnh
        // -> hai bên giữ nhau, deinit không bao giờ chạy.
        onComplete = {
            print("load, self\(self)")
        }
    }

    deinit {
        print("DataLoader deinit")
    }
}
```

fixed

```swift
//...
// weak: closure không tăng strong count, nên cycle bị phá. Nếu closure chạy sau khi
// loader đã bị giải phóng thì self chỉ là nil. unowned sẽ crash trong trường hợp đó.
onComplete = { [weak self] in
    print("load, self\(String(describing: self))")
}
//...
```
