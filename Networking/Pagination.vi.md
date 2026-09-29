[English](./Pagination.md) | [Tiếng Việt](./Pagination.vi.md)

[← Data và Networking](./README.vi.md)

# Pagination

## Ý chính

Pagination là bài toán tải thêm dữ liệu theo cách ổn định, không tạo request trùng, không vỡ thứ tự dữ liệu, và không làm loading state rối rắm.

## Cần ôn

- Pagination kiểu offset vs cursor
- Ai sở hữu paging state
- Cách tránh duplicate load khi scroll nhanh
- Cách merge các page mà vẫn giữ identity

## Ví dụ

```swift
struct FeedPage {
    let items: [FeedItem]
    let nextCursor: String?
}

protocol FeedRepository: Sendable {
    // repository.fetchFeed(cursor:) là stateless: không nhớ cursor giữa các lần gọi
    func fetchFeed(cursor: String?) async throws -> FeedPage
}

// @MainActor: mọi lời gọi chạy trên main actor, nên đoạn "kiểm tra isLoading rồi đặt true"
// chạy liền mạch trước `await` đầu tiên (xem đáp án bên dưới)
@MainActor
final class FeedPager {
    private let repository: any FeedRepository
    private(set) var nextCursor: String?
    private(set) var isLoading = false
    // nextCursor == nil sau trang cuối: nếu không có cờ này, lần gọi sau sẽ tải lại trang đầu
    private(set) var hasMore = true

    init(repository: any FeedRepository) {
        self.repository = repository
    }

    func loadNextPage() async throws -> FeedPage? {
        guard !isLoading, hasMore else { return nil }  // đang load hoặc đã hết trang thì bỏ qua
        isLoading = true
        defer { isLoading = false }

        let page = try await repository.fetchFeed(cursor: nextCursor)
        nextCursor = page.nextCursor
        hasMore = page.nextCursor != nil
        return page
    }
}
```

## Câu hỏi thực hành

- Paging state nên nằm ở ViewModel hay service?
- Làm sao tránh load page 3 hai lần?

## Câu hỏi luyện tập

- State pagination nên nằm ở ViewModel hay service?
- Làm sao bạn tránh load trang 3 hai lần?

## Góc nhìn senior

Paging state thường nên nằm gần feature flow, không nên chôn quá sâu trong một generic network client. Điều quan trọng là ownership rõ ràng cho `isLoading`, `nextCursor`, và cách merge dữ liệu.

## Đáp án câu hỏi luyện tập

### State pagination nên nằm ở ViewModel hay service?

Nên để paging state ở gần feature — trong ViewModel hoặc một object chuyên trách như `FeedPager` mà ViewModel sở hữu — còn service (network client) nên stateless.

Lý do là paging state gắn với một phiên xem cụ thể: danh sách này, với filter này, bắt đầu từ lúc user mở màn hình. `nextCursor`, `isLoading`, danh sách item đã merge và việc reset khi pull-to-refresh đều có vòng đời của màn hình. Nếu nhét vào một service dùng chung (thường là singleton), hai màn hình dùng feed với filter khác nhau sẽ ghi đè cursor của nhau, và state cũ còn sót lại khi user quay lại màn hình.

Cách chia thường dùng:
- **Service/repository**: `fetchFeed(cursor: String?) async throws -> FeedPage` — không nhớ gì giữa các lần gọi.
- **Pager**: giữ `nextCursor`, `isLoading`, chống request trùng, merge và dedupe item theo `id`.
- **ViewModel**: biến state của pager thành state UI (`loading`, `loaded`, `empty`, `loadingMore`, `error`).

Tách `FeedPager` khỏi ViewModel giúp test logic paging mà không cần UI, và dùng lại được cho nhiều màn hình feed.

Trade-off: với màn hình đơn giản, để state thẳng trong ViewModel là đủ; tạo thêm pager chỉ đáng khi logic merge/dedupe bắt đầu phức tạp. Nếu feed cần cache lâu dài hoặc chạy offline, dữ liệu item nên nằm ở repository/database, nhưng cursor của phiên hiện tại vẫn thuộc về feature.

### Làm sao bạn tránh load trang 3 hai lần?

Chặn ở nhiều lớp: không cho gửi request thứ hai khi request cho cùng trang đang chạy, bỏ kết quả đã lỗi thời, và dedupe item khi merge phòng trường hợp vẫn lọt.

Lớp thứ nhất là guard `isLoading` như trong `FeedPager`, nhưng nó chỉ đúng khi mọi lời gọi chạy trên cùng một executor. Đánh dấu pager (hoặc ViewModel) là `@MainActor` để đoạn "kiểm tra rồi đánh dấu đang load" chạy liền mạch trước `await` đầu tiên; không có isolation, hai lời gọi từ hai thread có thể cùng vượt qua guard.

Lớp thứ hai là tránh kết quả cũ: khi pull-to-refresh, cancel `Task` load-more đang chạy hoặc tăng một biến `generation`, rồi bỏ response nếu generation đã đổi.

Lớp thứ ba là merge theo identity: khi append, bỏ những item có `id` đã tồn tại (dùng một `Set` các id). Việc này cũng xử lý trường hợp backend trả trùng item giữa hai trang.

```swift
@MainActor
final class FeedPager {
    private var loadTask: Task<Void, Never>?

    func loadNextPageIfNeeded() {
        guard loadTask == nil else { return }  // đã có request đang chạy
        loadTask = Task {
            defer { loadTask = nil }
            // fetch với nextCursor, merge, dedupe theo id
        }
    }
}
```

Trade-off: debounce trigger khi scroll cũng giúp giảm số request, nhưng không thay thế được guard — debounce chỉ làm thưa request, không đảm bảo mỗi trang chỉ được gọi một lần.

## Bẫy phỏng vấn

### "Dùng actor cho pager là hết race condition" — đúng không?

**Dễ trả lời sai:** "Đúng, actor serialize mọi truy cập nên không thể load trùng."

**Nên trả lời:** Actor chống data race, nhưng không chống logic race, vì actor có reentrancy: tại mỗi `await`, actor có thể xử lý một lời gọi khác. Nếu bạn `guard !isLoading` rồi `await` một thứ gì đó trước khi gán `isLoading = true`, lời gọi thứ hai vẫn vượt qua guard. Phải kiểm tra và đánh dấu state trước `await` đầu tiên, và kiểm tra lại state sau khi `await` trả về (ví dụ cursor có còn khớp không).

### Offset pagination (`?page=3&limit=20`) có vấn đề gì với một feed?

**Dễ trả lời sai:** "Không có gì, offset đơn giản và còn cho phép nhảy thẳng tới trang bất kỳ."

**Nên trả lời:** Khi có item mới được chèn lên đầu feed trong lúc user đang scroll, toàn bộ offset bị dịch: trang 3 sẽ chứa lại vài item của trang 2 (bị trùng) hoặc bỏ sót item. Cursor (thường là id hoặc timestamp của item cuối) gắn với vị trí thật trong dữ liệu nên ổn định hơn, và database cũng query nhanh hơn so với phải `OFFSET` qua hàng nghìn dòng. Offset vẫn hợp với dữ liệu ít thay đổi và cần nhảy trang, như bảng kết quả tìm kiếm có đánh số trang.

### Pull-to-refresh trong lúc load-more đang chạy thì chuyện gì xảy ra?

**Dễ trả lời sai:** "Không sao, guard `isLoading` đã lo rồi."

**Nên trả lời:** Nếu refresh reset danh sách và cursor, response của lần load-more cũ về sau sẽ được append vào danh sách mới — dữ liệu lẫn lộn và cursor sai. Cần cancel `Task` load-more khi refresh, hoặc gắn mỗi request với một generation/token và bỏ kết quả không khớp. Ngoài ra trong SwiftUI, `.onAppear` của hàng cuối có thể được gọi nhiều lần khi layout thay đổi, nên trigger load-more phải idempotent.

## Bài tập

Mô hình hóa một infinite feed dùng cursor pagination. Mô tả các state: success, empty, loading-more, error. Sau đó giải thích cách bạn ngăn duplicate request khi user chạm đáy danh sách nhiều lần.
