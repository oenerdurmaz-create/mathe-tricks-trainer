import SwiftUI

@main
struct MatheTricksTrainerApp: App {
    var body: some Scene {
        WindowGroup {
            GameContainerView()
                .preferredColorScheme(.dark)
        }
    }
}
