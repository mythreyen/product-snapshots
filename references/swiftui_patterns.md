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

## 2. Multi-Layer Studio Shadows & Zero-Cutoff Padding

macOS window shadows rendered by AppKit/WindowServer are often messy, asymmetric, or cut off when capturing windows. In `ImageRenderer`, SwiftUI creates clean alpha-channel transparent shadows that look like high-end marketing studio renders:

```swift
content
    // Tier 1: Soft ambient floor bounce
    .shadow(color: .black.opacity(0.48), radius: 26, x: 0, y: 14)
    // Tier 2: Crisp contact shadow near the edges
    .shadow(color: .black.opacity(0.20), radius: 8, x: 0, y: 2)
    // Critical: provide outer padding to guarantee zero shadow clipping
    .padding(95)
```

### The Zero-Cutoff Padding Formula
To prevent visible hard rectangular edge cutoffs where the shadow hits the PNG canvas boundary, calculate canvas padding using:
$$\text{Padding} \ge (\text{Max Shadow Radius} \times 2.5) + |\text{Y Offset}| + 15$$

For example:
- **Standalone Cards / Windows** (`radius: 26, y: 14`): Use `.padding(95)` (or `.padding(140)` for large settings panels).
- **Docked Multi-Window Arrangements** (`radius: 30, y: 16`): Use `.padding(110)`.

This ensures the shadow opacity decays exponentially to 0% (`alpha == 0`) well before reaching the edge of the rasterized PNG.

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
