import SwiftUI
import UIKit
import WebKit

/// Lokaler WKWebView-Host. Laedt ausschliesslich die mitgelieferte HTML-Datei,
/// blockiert jede externe Navigation und meldet dem Spiel, wenn die App in den
/// Hintergrund geht, damit der Zeitbalken pausiert (window.appPause).
struct LocalGameWebView: UIViewRepresentable {
    let resourceName: String
    let resourceExtension: String

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .default()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true
        configuration.allowsInlineMediaPlayback = true
        configuration.mediaTypesRequiringUserActionForPlayback = []

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.uiDelegate = context.coordinator
        webView.isOpaque = false
        webView.backgroundColor = .clear
        webView.scrollView.backgroundColor = .clear
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.scrollView.bounces = false
        webView.allowsBackForwardNavigationGestures = false
        webView.allowsLinkPreview = false

        context.coordinator.attach(webView)
        context.coordinator.loadGame(in: webView, resourceName: resourceName, resourceExtension: resourceExtension)
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        if webView.url == nil {
            context.coordinator.loadGame(in: webView, resourceName: resourceName, resourceExtension: resourceExtension)
        }
    }

    static func dismantleUIView(_ webView: WKWebView, coordinator: Coordinator) {
        coordinator.detach()
    }

    final class Coordinator: NSObject, WKNavigationDelegate, WKUIDelegate {
        private weak var webView: WKWebView?
        private var observers: [NSObjectProtocol] = []

        func attach(_ webView: WKWebView) {
            self.webView = webView
            let center = NotificationCenter.default
            observers.append(center.addObserver(forName: UIApplication.willResignActiveNotification, object: nil, queue: .main) { [weak self] _ in
                self?.webView?.evaluateJavaScript("window.appPause && window.appPause()", completionHandler: nil)
            })
            observers.append(center.addObserver(forName: UIApplication.didEnterBackgroundNotification, object: nil, queue: .main) { [weak self] _ in
                self?.webView?.evaluateJavaScript("window.appPause && window.appPause()", completionHandler: nil)
            })
        }

        func detach() {
            observers.forEach { NotificationCenter.default.removeObserver($0) }
            observers.removeAll()
        }

        func loadGame(in webView: WKWebView, resourceName: String, resourceExtension: String) {
            guard let url = Bundle.main.url(forResource: resourceName, withExtension: resourceExtension) else {
                let message = "<html><body style='font-family:-apple-system;padding:30px'><h2>Mathe Tricks Trainer</h2><p>Die Spieldatei konnte nicht geladen werden.</p></body></html>"
                webView.loadHTMLString(message, baseURL: nil)
                return
            }

            webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }

        func webView(
            _ webView: WKWebView,
            decidePolicyFor navigationAction: WKNavigationAction,
            decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
        ) {
            guard let url = navigationAction.request.url else {
                decisionHandler(.cancel)
                return
            }

            if url.isFileURL || url.scheme == "about" {
                decisionHandler(.allow)
            } else {
                decisionHandler(.cancel)
            }
        }
    }
}
