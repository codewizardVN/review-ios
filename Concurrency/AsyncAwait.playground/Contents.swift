import Combine
import UIKit
import Foundation

//struct User: Codable {
//    let id: String
//    let name: String
//}
//
//func fetchUser(id: String) async throws -> User {
////    let url = URL(string: "https://api.example.com/users/\(id)")!
////    let (data, response) = try await URLSession.shared.data(from: url)
////
////    guard let httpResponse = response as? HTTPURLResponse,
////        httpResponse.statusCode == 200
////    else {
////        throw URLError(.badServerResponse)
////    }
////    return try JSONDecoder().decode(User.self, from: data)
//    try await Task.sleep(nanoseconds: 1_000_000_000) // Simulate network delay
//    return User(id: id, name: "John Doe")
//}
//
//@MainActor
//func fetchUserWithCompletion(id: String, completion: @escaping (Result<User, Error>) -> Void) {
//    Task {
//        do {
//            // withCheckedThrowingContinuation tạo ra một "bridge point":
//            // nó suspend coroutine hiện tại, cho phép ta gọi code
//            // callback-based bên trong, rồi resume lại khi có kết quả.
//            //
//            // "Checked" = runtime sẽ crash nếu continuation bị gọi
//            // 0 lần hoặc > 1 lần → giúp phát hiện bug sớm.
//            let user = try await withCheckedThrowingContinuation { continuation in
//                // Ở đây ta giả sử fetchUser(id:) async đã tồn tại,
//                // nhưng ta đang wrap chính nó để demo pattern.
//                // Trong thực tế, chỗ này là nơi gọi legacy async API:
//                //
//                // legacySDK.fetchUser(id: id) { result in
//                //     continuation.resume(with: result)
//                // }
//                Task {
//                    do {
//                        let result = try await fetchUser(id: id)
//                        continuation.resume(returning: result)
//                    } catch {
//                        continuation.resume(throwing: error)
//                    }
//                }
//            }
//            completion(.success(user))
//        } catch {
//            completion(.failure(error))
//        }
//    }
//}
//
//
//// MARK: - Example Usage
//fetchUserWithCompletion(id: "123") { result in
//    switch result {
//    case .success(let user):
//        print("Fetched user: \(user)")
//    case .failure(let error):
//        print("Error fetching user: \(error)")
//    }
//}
