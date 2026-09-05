[English](./ARC.md) | [Tiếng Việt](./ARC.vi.md)

[← Swift Core](./README.vi.md)

# ARC và Quản lý bộ nhớ

## 1. ARC

### Ý chính

ARC tự động theo dõi các strong reference và giải phóng object khi reference count của chúng về zero.

### Những điều quan trọng trong thực tế

- Strong reference giữ object tồn tại
- Weak reference không giữ object tồn tại
- Unowned reference giả định object vẫn còn tồn tại
- ARC không phải là garbage collector

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

- Closures capture `self`
- Mối quan hệ delegate không có `weak`
- Các callback tồn tại lâu dài
- Các pattern Timer / notification / observer
- Async work giữ strong reference đến object lâu hơn mong đợi

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

## Bài tập

Viết một class `DataLoader` fetch dữ liệu và gọi một completion closure. Cố tình tạo ra một retain cycle bằng cách để closure capture `self` mạnh và lưu closure đó như một property. Xác minh cycle tồn tại bằng cách dùng `deinit { print("deinit") }`. Sau đó fix nó bằng `[weak self]`. Giải thích trong comment tại sao weak là lựa chọn đúng ở đây (không phải unowned).
