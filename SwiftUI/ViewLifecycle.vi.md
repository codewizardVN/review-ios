[English](./ViewLifecycle.md) | [Tiếng Việt](./ViewLifecycle.vi.md)

[← SwiftUI](./README.vi.md)

# Vòng đời View

## Ý chính

SwiftUI views là value type (struct) được tái tạo thường xuyên. Framework so sánh view description và chỉ áp dụng thay đổi thực sự lên render tree — không phải struct instance.

## Nội dung ôn tập

- `onAppear` / `onDisappear` — hook side effect được gọi khi view được thêm vào / gỡ khỏi hierarchy đang hiển thị. Chúng có thể chạy nhiều lần trong đời view (pop về, đổi tab, cuộn trong lazy container), không phải chỉ một lần như `viewDidLoad`.
- `task` modifier — cách ưu tiên để chạy async work gắn với view: task bắt đầu khi view sắp xuất hiện và tự bị cancel khi view biến mất. `.task(id:)` còn cancel và chạy lại task mỗi khi giá trị `id` thay đổi.
- View identity — SwiftUI nhận diện "đây có phải cùng một view không" bằng hai cách: structural identity (type + vị trí trong cây view, ví dụ nhánh `if` hay `else`) và explicit identity (giá trị bạn gán qua `.id(value)` hoặc ID trong `ForEach`). State (`@State`, `@StateObject`) sống theo identity, không theo struct instance.
- Khi nào SwiftUI tái tạo vs tái sử dụng view — struct view bị tạo lại rất thường xuyên và điều đó rẻ; nhưng chỉ khi identity thay đổi thì SwiftUI mới hủy view cũ (mất state, gọi `onDisappear`, cancel `.task`) và dựng view mới.

## Ví dụ

```swift
struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .task {
            await viewModel.load()
        }
    }
}
```

## Câu hỏi luyện tập

- Tại sao .task được ưu tiên hơn onAppear kết hợp quản lý task thủ công cho một CountdownView cần cancel đếm ngược dựa trên Task.sleep khi user navigate away?

## Góc nhìn Senior

Hiểu về identity là chìa khóa. Giữa hai lần update, một view có cùng type ở cùng vị trí trong hierarchy (và cùng explicit ID nếu có) được SwiftUI coi là cùng một view, nên state của nó được giữ nguyên dù struct được tạo mới. Thay đổi `.id()` sẽ phá hủy và tái tạo state. Điều này quan trọng khi animate list hoặc reset form field.

## Đáp án câu hỏi luyện tập

### Tại sao .task được ưu tiên hơn onAppear kết hợp quản lý task thủ công cho một CountdownView cần cancel đếm ngược dựa trên Task.sleep khi user navigate away?

`.task` được ưu tiên vì SwiftUI gắn vòng đời của Task vào vòng đời của view: task được khởi chạy khi view sắp xuất hiện và tự động bị cancel khi view biến mất, nên bạn không phải tự lưu và tự cancel nó.

Nếu dùng `onAppear`, bạn phải tạo `Task { ... }`, lưu vào một `@State var countdownTask: Task<Void, Never>?`, rồi nhớ gọi `cancel()` trong `onDisappear`. Chỉ cần quên một bước, hoặc `onAppear` bị gọi nhiều lần (pop về từ màn khác, đổi tab), là bạn có hai vòng đếm chạy song song hoặc một task "mồ côi" vẫn chạy sau khi user đã rời màn hình.

Với `.task`, khi user navigate away SwiftUI cancel task; `Task.sleep` là một điểm kiểm tra cancellation nên nó ném `CancellationError` ngay lập tức, vòng lặp kết thúc. Nếu bọc trong `withTaskCancellationHandler`, closure `onCancel` được gọi ngay lúc task bị cancel và in ra "cancelled".

```swift
.task {
    await withTaskCancellationHandler {
        for value in stride(from: 10, through: 0, by: -1) {
            remaining = value
            do { try await Task.sleep(for: .seconds(1)) }
            catch { return } // bị cancel khi view biến mất
        }
    } onCancel: {
        print("cancelled") // chạy ngay khi task bị cancel, có thể trên thread khác
    }
}
```

Trade-off: cancellation là cooperative — đoạn code không có điểm `await` hay `Task.checkCancellation()` vẫn chạy tiếp. Nếu cần restart khi input thay đổi, dùng `.task(id:)`. Nếu công việc phải sống lâu hơn view (upload, sync), đừng đặt trong `.task`; hãy để một service hoặc actor bên ngoài view sở hữu nó.

## Bẫy phỏng vấn

### "onAppear có giống viewDidLoad không — chỉ chạy một lần?"

**Dễ trả lời sai:** Coi `onAppear` (và `.task`) như `viewDidLoad`, chạy đúng một lần trong đời view, nên đặt việc load dữ liệu ban đầu vào đó là an toàn.

**Nên trả lời:** `onAppear` được gọi mỗi lần view xuất hiện lại: pop về từ màn detail, đổi tab, cuộn ra rồi cuộn vào trong lazy container. `.task` cũng chạy lại theo cùng nhịp đó (và bị cancel mỗi lần view biến mất). Vì vậy `FeedView` trong ví dụ có thể gọi `load()` nhiều lần. Nếu chỉ muốn load một lần, hãy guard bằng state trong view model (`if items.isEmpty`) hoặc dùng `.task(id:)` với một giá trị chỉ đổi khi thực sự cần reload.

### "Task đã bị cancel thì code bên trong dừng ngay, đúng không?"

**Dễ trả lời sai:** Cho rằng khi `.task` bị cancel, Swift sẽ "giết" task và mọi dòng code sau đó không chạy nữa.

**Nên trả lời:** Cancellation trong Swift Concurrency là cooperative: nó chỉ bật cờ `isCancelled`. Các API như `Task.sleep` hay `URLSession` kiểm tra cờ này và ném `CancellationError`, nhưng một vòng lặp tính toán đồng bộ sẽ chạy đến hết. Code dài phải tự gọi `try Task.checkCancellation()` hoặc kiểm tra `Task.isCancelled`. Ngoài ra, closure của `.task` chạy trên main actor (từ Xcode 16 / SDK iOS 18, cả protocol `View` được đánh dấu `@MainActor`), nên việc nặng đồng bộ trong đó vẫn block UI dù có bị cancel hay không.

### "Thêm .id(...) vào view chỉ để buộc nó refresh UI thôi?"

**Dễ trả lời sai:** Nghĩ rằng `.id()` chỉ là cách "force redraw", không ảnh hưởng gì đến state hay side effect.

**Nên trả lời:** Đổi `.id()` là đổi identity: SwiftUI coi đó là một view hoàn toàn mới, hủy view cũ — `@State`/`@StateObject` bị reset, `.task` cũ bị cancel, `onDisappear`/`onAppear` được gọi và `.task` mới khởi chạy. Đây là công cụ hữu ích để reset form, nhưng nếu viết `.id(UUID())` trong `body`, view bị tạo lại ở mỗi lần render, mất state và chạy lại side effect liên tục.

## Bài tập

Xây dựng `CountdownView` bắt đầu đếm ngược từ 10 dùng `.task` và `try await Task.sleep`. Xác nhận timer cancel khi navigate away bằng cách wrap sleep trong `withTaskCancellationHandler` in ra "cancelled". Navigate away giữa chừng và xác nhận message xuất hiện. Giải thích trong comment tại sao `.task` được ưu tiên hơn `onAppear` + quản lý task thủ công.
