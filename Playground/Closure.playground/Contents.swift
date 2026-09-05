import PlaygroundSupport
import SwiftUI
import UIKit
//
//// 1. Child dont need to know about the parent, so we pass in the callbacks as closures
//struct ConfirmmationSheet: View {
//    let message: String
//    var onConfirm: () -> Void
//    var onCancel: () -> Void
//
//    var body: some View {
//        VStack(spacing: 20) {
//            Text(message)
//                .font(.headline)
//                .multilineTextAlignment(.center)
//                .padding()
//            HStack {
//                Button("Cancel") {
//                    onCancel()
//                }
//                .padding()
//                .background(Color.gray.opacity(0.2))
//                .cornerRadius(8)
//                Button("Confirm") {
//                    onConfirm()
//                }
//                .padding()
//                .background(Color.blue)
//                .foregroundColor(.white)
//                .cornerRadius(8)
//            }
//        }
//    }
//}
//
//// 2. Parent can define the logic for confirm and cancel, and pass it down to the child
//struct ContentView: View {
//    @State private var showSheet = false
//
//    var body: some View {
//        VStack {
//            Button("Place Order") {
//                showSheet = true
//            }
//            .padding()
//            .background(Color.blue)
//            .foregroundColor(.white)
//            .cornerRadius(8)
//        }
//        .frame(width: 390, height: 844)
//        .sheet(isPresented: $showSheet) {
//            ConfirmmationSheet(
//                message: "Are you sure you want to place the order?",
//                onConfirm: {
//                    print("Order confirmed!")
//                    showSheet = false
//                },
//                onCancel: {
//                    print("Order cancelled.")
//                    showSheet = false
//                }
//            )
//        }
//    }
//}
//
//
//let viewController = UIHostingController(rootView: ContentView())
//viewController.preferredContentSize = CGSize(width: 390, height: 844)
//
//PlaygroundPage.current.liveView = viewController
//PlaygroundPage.current.needsIndefiniteExecution = true

// Session user - need 1 object shared across the app, but we dont want to make it a global variable.
actor AuthSession {
    static let shared = AuthSession()
    private(set) var currentUser: User?
    private(set) var accessToken: String?
    
    func update(user: User, token: String) {
        self.currentUser = user
        self.accessToken = token
    }
}

// Use in NavigationStack, Tabbar, ViewModel,..
let session = AuthSession.shared
