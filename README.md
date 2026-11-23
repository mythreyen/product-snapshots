# Product Snapshots & Showcase Generator

<p align="center">
  <b>Automated, publication-grade screenshot and marketing showcase pipeline directly from native application builds.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20iOS%20%7C%20Electron%20%7C%20Web-111827?style=flat-square" alt="Platform: macOS, iOS, Electron, Web">
  <img src="https://img.shields.io/badge/type-Antigravity%20Skill-8B5CF6?style=flat-square" alt="Type: Antigravity Skill">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License: MIT">
</p>

---

## Overview

Taking screenshots for READMEs, App Store product pages, and marketing showcases is often painful:
* **Fragile**: Manual window captures capture clutter, irregular shadows, and mouse cursors.
* **Timing Bugs (The $t=0$ Trap)**: Headless rendering engines (like SwiftUI's `ImageRenderer`) rasterize at $t=0$, causing asynchronous loaders and `.transition` animations to render empty or with placeholder/skeleton art.
* **Control Clutter**: Product shots need content to shine—hover buttons, transport controls, and window utility icons should be cleanly suppressed.
* **Clipped Shadows**: OS-level window shadows are frequently cut off or vary across OS versions.

**`product-snapshots`** is an Antigravity skill that provides a complete, automated architecture for native in-process snapshot capture, studio multi-layer drop shadows, multi-window docking, marketing banner generation, and automated pixel verification.

---

## Features

- 🎯 **Direct Binary Execution**: Trigger captures directly via CLI flags (`app --snapshot`) without screen recording tools or display window managers.
- ⚡ **Animation Phase Bypass**: Eliminates $t=0$ transition bugs to render final, pristine visual states immediately.
- 🎨 **Multi-Layer Studio Shadows**: Produces dual-tier transparent alpha drop shadows with generous safety padding to prevent edge clipping.
- 🧩 **Multi-Window Docking**: Pixel-aligned side-by-side composition for main windows paired with auxiliary panels (inspectors, sidebars, lyrics windows).
- 🖼️ **2:1 Showcase Banners**: Blueprint for composing 2560×1280 Retina marketing banners with ambient color glows and typography.
- 🔍 **Automated Pixel & Dimension Verification**: Bundled Python verification tool checks for zero placeholder pixels, retina resolutions, and non-empty files.

---

## Directory Structure

```text
product-snapshots/
├── SKILL.md                               # Main Antigravity skill definition with YAML frontmatter
├── README.md                              # Repository overview and documentation
├── LICENSE                                # MIT License
├── scripts/
│   └── validate_snapshots.py              # Pixel-level verification tool (detects placeholder discs & texture errors)
├── templates/
│   ├── SnapshotGenerator.swift.template   # Modular SwiftUI snapshot capture engine
│   └── SnapshotEnvironment.swift.template # Environment keys: isSnapshotMode & forceControlsVisible
└── references/
    ├── swiftui_patterns.md                # Technical guide on ImageRenderer, animation bypass, and shadows
    ├── banner_composition.md              # Layout blueprint for marketing & repository showcase banners
    └── troubleshooting.md                 # Diagnostics for yellow pixels, clipping, and missing assets
```

---

## Installation

### Option 1: Global Install (Available across all projects on your Mac)

Clone or copy this repository into your global Antigravity config directory:

```bash
mkdir -p ~/.gemini/config/skills
git clone https://github.com/mythreyen/product-snapshots.git ~/.gemini/config/skills/product-snapshots
```

Ensure your `~/.gemini/config/skills.json` includes:

```json
{
  "entries": [
    {
      "path": "~/.gemini/config/skills"
    }
  ]
}
```

### Option 2: Project-Specific Install (Workspace Skill)

Add the skill to your project repository so your entire team can use it:

```bash
mkdir -p .agents/skills
git clone https://github.com/mythreyen/product-snapshots.git .agents/skills/product-snapshots
```

---

## How It Works: The 7-Step Pipeline

1. **In-Memory Mock State**: Supply realistic, production-ready local mock data (no network dependencies, no skeletons).
2. **Snapshot Environment Protocol**: Inject `\.isSnapshotMode` and `\.forceControlsVisible` into view hierarchies.
3. **Bypass Transitions & Overlays**: If `isSnapshotMode` is true, render images directly without `.transition` or `.animation` delays, and hide floating controls.
4. **Studio Shadow Canvases**: Wrap views in multi-tier shadows (`radius: 26` ambient floor + `radius: 8` contact shadow) with outer `.padding(34)` to prevent clipping.
5. **Retina ImageRenderer**: Render at `scale = 2.0` to generate high-DPI `@2x` PNGs.
6. **Showcase & Banner Composition**: Compose docked views and 2560×1280 showcase banners.
7. **Automated Verification**: Run `validate_snapshots.py` to assert 0 error/placeholder pixels before publishing.

---

## Verifying Snapshots

Run the automated verification script on your output directory:

```bash
python3 scripts/validate_snapshots.py --dir docs/images
```

Output:
```text
🔍 Validating 15 product snapshots in 'docs/images'...

Image Filename                       | Dimensions   | Size       | Status
----------------------------------------------------------------------------
musi-banner.png                      | 2560x1280    | 3893 KB    | ✅ PASS
musi-player.png                      | 1452x1284    | 1686 KB    | ✅ PASS
screenshot-standard.png              | 856x1276     | 1115 KB    | ✅ PASS
screenshot-mini.png                  | 1136x416     | 438 KB     | ✅ PASS
screenshot-compact.png               | 656x656      | 495 KB     | ✅ PASS
----------------------------------------------------------------------------
✨ SUCCESS: All product snapshots are pristine and publication-ready!
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
