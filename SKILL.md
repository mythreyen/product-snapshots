---
name: product-snapshots
description: >-
  Architects and executes automated, high-resolution product screenshot and marketing
  showcase pipelines directly from native application builds (SwiftUI/macOS, iOS, Electron, Web).
  Use this skill whenever asked to create product shots, app store screenshots, README showcase
  banners, docked multi-window marketing images, or when automating screenshot capture from real builds.
---

# Product Snapshots & Showcase Generator Skill

This skill teaches the agent how to architect, build, and maintain an automated, pixel-perfect **product snapshot pipeline** that captures native, publication-ready screenshots directly from live application builds.

Unlike manual screen capture tools or fragile headless browser wrappers, this method renders views directly from the compiled application binary with pristine mock data, custom shadow canvases, zero UI chrome, and automated pixel verification.

---

## The Core Problem with Standard Screenshots

1. **Fragile UI State**: Manual window captures capture dirty local states, missing assets, placeholder discs/skeletons, or accidental mouse hover states.
2. **Animation Phase Bugs (The $t=0$ Trap)**: Headless renderers (like SwiftUI's `ImageRenderer`) evaluate views synchronously at $t=0$. Views relying on `.transition` or `.animation` for image loading or layout often render blank or with placeholder art.
3. **Control Clutter**: Product shots require content (artwork, lyrics, documents, graphs) to be the hero; hover buttons, transport controls, and utility icons should be cleanly hidden unless specifically showcasing them.
4. **Window Chrome Artifacts**: macOS window shadows are non-uniform, clipped by default capture tools, and vary across OS versions. Native multi-layer programmatic shadows provide consistent studio-quality depth.

---

## The 7-Step Product Snapshot Architecture

```text
┌────────────────────────┐      ┌─────────────────────────┐
│ 1. In-Memory Mock Data │ ───► │ 2. Snapshot Environment │
│ (Real assets, no skels)│      │    (\.isSnapshotMode)   │
└────────────────────────┘      └────────────┬────────────┘
                                             │
┌────────────────────────┐                   ▼
│ 4. Studio Shadow Canvas│      ┌─────────────────────────┐
│ (Multi-layer depth)    │ ◄─── │ 3. Animation & Gesture  │
└───────────┬────────────┘      │    Bypass (Clean at t=0)│
            │                   └─────────────────────────┘
            ▼
┌────────────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐
│ 5. Native ImageRenderer│ ───► │ 6. CLI Entrypoint       │ ───► │ 7. Automated Pixel &   │
│    (@2x Retina Scale)  │      │    (app --snapshot)     │      │    Dimension Check     │
└────────────────────────┘      └─────────────────────────┘      └────────────────────────┘
```

---

### Step 1: Supply In-Memory Mock State (Zero Placeholders)

Create a dedicated mock controller or state provider that supplies realistic, production-ready mock data:
- Real high-resolution assets (e.g. 1000×1000 album covers, complete user profiles, realistic graphs).
- Complete text content (e.g. active synchronized lyric lines, active playlists, rich descriptions).
- Avoid network-dependent fetching during snapshot mode; load synchronous fallback data if network access is absent.

```swift
class MockAppState: AppState {
    override init() {
        super.init()
        self.itemTitle = "Electric Dreams"
        self.itemSubtitle = "Synthetic Waves • Synth Horizon"
        self.heroImage = SnapshotGenerator.loadRealAsset()
        self.isLoaded = true
    }
}
```

---

### Step 2: The Snapshot Environment Keys

Define two custom SwiftUI environment keys in your application:
- `isSnapshotMode`: Signals views to bypass asynchronous loaders, transitions, and gesture delays.
- `forceControlsVisible`: Allows toggling whether floating controls, transport buttons, and hover utilities should be shown or hidden.

See [SnapshotEnvironment.swift.template](./templates/SnapshotEnvironment.swift.template).

```swift
private struct SnapshotModeKey: EnvironmentKey {
    static let defaultValue: Bool = false
}
private struct ForceControlsVisibleKey: EnvironmentKey {
    static let defaultValue: Bool = false
}

extension EnvironmentValues {
    var isSnapshotMode: Bool {
        get { self[SnapshotModeKey.self] }
        set { self[SnapshotModeKey.self] = newValue }
    }
    var forceControlsVisible: Bool {
        get { self[ForceControlsVisibleKey.self] }
        set { self[ForceControlsVisibleKey.self] = newValue }
    }
}
```

---

### Step 3: Bypassing Transitions and Animations ($t=0$ Trap)

In view components that render images, artwork, or animated panels, branch on `isSnapshotMode`:

```swift
// ❌ WRONG: ImageRenderer evaluates this at animation phase t=0, rendering the placeholder
ZStack {
    if let img = state.image {
        Image(nsImage: img)
    } else {
        Placeholder()
    }
}
.transition(.opacity)
.animation(.easeInOut, value: state.image)

// ✅ RIGHT: In snapshot mode, render the real image directly without animation/transition delays
if isSnapshotMode {
    if let img = state.image {
        Image(nsImage: img)
            .resizable()
            .aspectRatio(contentMode: .fill)
    } else {
        Placeholder()
    }
} else {
    ZStack { ... }
        .transition(.opacity)
        .animation(.easeInOut, value: state.image)
}
```

Likewise, hide hover overlays and proximity controls when `forceControlsVisible == false`:
```swift
let showControls = forceControlsVisible || (isHovering && isProximity)
```

---

### Step 4: Multi-Layer Floating Studio Shadows

Wrap views in a multi-tier shadow stack to achieve floating studio depth, padded with generous margins to prevent shadow clipping:

```swift
view
    .shadow(color: .black.opacity(0.48), radius: 26, x: 0, y: 14)  // Broad ambient floor shadow
    .shadow(color: .black.opacity(0.20), radius: 8, x: 0, y: 2)   // Crisp contact shadow
    .padding(34)                                                  // Essential: prevents shadow clip
```

---

### Step 5: High-DPI Rendering with `ImageRenderer`

Use `ImageRenderer` at `scale = 2.0` (Retina resolution) to produce crisp PNGs:

```swift
@MainActor
static func render<V: View>(view: V, scale: CGFloat = 2.0) -> Data? {
    let renderer = ImageRenderer(content: view)
    renderer.scale = scale
    guard let nsImage = renderer.nsImage,
          let tiff = nsImage.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let pngData = rep.representation(using: .png, properties: [:]) else {
        return nil
    }
    return pngData
}
```

---

### Step 6: Multi-Window Docking & Showcase Banners

#### 1. Docked Multi-Window Shots
Compose independent windows side-by-side using `HStack(alignment: .top, spacing: gap)`:
- Standard + Lyrics: `HStack(spacing: 14) { StandardPlayerView(); LyricsView().frame(...) }`
- Mini + Lyrics: `HStack(alignment: .top, spacing: 14) { MiniPlayerView(); LyricsView().frame(height: 380) }`

#### 2. Showcase Repository Banner (`musi-banner.png`)
Create a dedicated 1280×640 (@2x = 2560×1280) canvas featuring:
- Deep gradient glass background (`LinearGradient`).
- Ambient radial blur spheres (`Circle().fill(...).blur(radius: 90)`).
- Left column: App icon, bold title, subtitle, and feature pill badges.
- Right column: Depth-layered arrangement of each supported form factor with offset shadows.

See [banner_composition.md](./references/banner_composition.md).

---

### Step 7: Automated Pixel Verification

Always run an automated pixel-validation script to guarantee quality before committing:
1. Verify no placeholder colors (e.g. RGB `(200+, 180+, <60)` for yellow placeholders).
2. Verify exact `@2x` dimensions.
3. Verify file sizes are non-zero.

Run the bundled validation script:
```bash
python3 scripts/validate_snapshots.py --dir docs/images --no-placeholders
```

---

## Integration Checklist for New Projects

When adding this snapshot pipeline to any new project:

1. [ ] **Add Environment Keys**: Add `isSnapshotMode` and `forceControlsVisible` to the app.
2. [ ] **Add Snapshot Engine**: Copy and adapt [SnapshotGenerator.swift.template](./templates/SnapshotGenerator.swift.template).
3. [ ] **Hook CLI Entrypoint**: In `main.swift` or `AppDelegate.swift`, check for `CommandLine.arguments.contains("--snapshot")`. If present, call `SnapshotGenerator.generateAll()` and exit cleanly `exit(0)`.
4. [ ] **Build & Execute**:
   ```bash
   xcodebuild build -scheme App -derivedDataPath build/DerivedData ...
   build/DerivedData/Build/Products/Debug/App.app/Contents/MacOS/App --snapshot
   ```
5. [ ] **Validate**:
   Run `scripts/validate_snapshots.py` to confirm 0 error pixels.
6. [ ] **Update Documentation**: Update `README.md` with side-by-side `<img width="420">` comparison tables.
