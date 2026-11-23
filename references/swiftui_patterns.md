# SwiftUI Snapshot Patterns & ImageRenderer Deep Dive

## 1. Why `ImageRenderer` Evaluates at $t=0$

SwiftUI's `ImageRenderer` performs a synchronous rasterization pass on a view hierarchy. Because it does not run inside an interactive display runloop over time:
- Any `.transition(.opacity)` or `.transition(.move)` starts at progress $t=0$ (completely transparent or offscreen).
- Any `.animation(...)` attached to state changes has not had time to step forward.
- Any `AsyncImage` or async URL loading task has not completed.

### Solution
In snapshot mode, bypass all asynchronous paths and animation wrappers:
```swift
if isSnapshotMode {
    Image(nsImage: loadedImage)
        .resizable()
        .aspectRatio(contentMode: .fill)
} else {
    // Normal interactive code
    Image(nsImage: loadedImage)
        .transition(.opacity)
        .animation(.easeInOut, value: loadedImage)
}
```

---

## 2. Multi-Layer Studio Shadows

macOS window shadows rendered by AppKit/WindowServer are often messy, asymmetric, or cut off when capturing windows. In `ImageRenderer`, SwiftUI creates clean alpha-channel transparent shadows that look like high-end marketing studio renders:

```swift
content
    // Tier 1: Soft ambient floor bounce
    .shadow(color: .black.opacity(0.48), radius: 26, x: 0, y: 14)
    // Tier 2: Crisp contact shadow near the edges
    .shadow(color: .black.opacity(0.20), radius: 8, x: 0, y: 2)
    // Critical: provide outer padding larger than the maximum shadow radius (26 + 8 = 34)
    .padding(34)
```

Without `.padding(34)`, the bounding box of `ImageRenderer` will clip the outer glow, resulting in harsh rectangular cutoffs.

---

## 3. Docking Multi-Window Arrangements

When your app supports multi-window interactions (e.g., an auxiliary side panel, a secondary inspector, or a synced lyrics window), arrange them in SwiftUI using an `HStack`:

```swift
HStack(alignment: .top, spacing: 14) {
    MainWindowView()
    SecondaryWindowView()
        .frame(width: 280, height: 380)
}
.shadow(...)
.padding(36)
```

This guarantees pixel alignment, identical lighting/shadow angles, and zero window overlap artifacts.
