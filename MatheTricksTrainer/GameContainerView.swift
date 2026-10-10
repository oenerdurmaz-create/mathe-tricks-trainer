import SwiftUI

struct GameContainerView: View {
    var body: some View {
        LocalGameWebView(resourceName: "MatheTricksTrainer", resourceExtension: "html")
            .ignoresSafeArea()
            .background(Color(red: 0.059, green: 0.106, blue: 0.239))
    }
}

#Preview {
    GameContainerView()
}
