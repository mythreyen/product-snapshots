# Snapshot Troubleshooting Guide

## 1. Yellow Discs or Crossed-out Placeholders
- **Symptom**: Album art, profile photos, or item thumbnails appear as yellow discs, grey boxes, or crossed-out placeholders.
- **Cause**: View was rendered at $t=0$ while async asset loading or `.transition` had not yet completed, or mock controller did not supply synchronous image data.
- **Fix**:
  1. Ensure `MockAppState` loads assets directly and synchronously from bundle/disk (`Data(contentsOf: url)`).
  2. In SwiftUI, check `if isSnapshotMode { Image(nsImage: img) } else { ... with transition }`.

## 2. Hard Rectangular Edges Cutting Off Shadow
- **Symptom**: Shadow looks cut off in a sharp straight line on one or more sides.
- **Cause**: Insufficient `.padding()` surrounding the view before passing to `render()`.
- **Fix**: Calculate `max_shadow_radius + blur_spread + 10` and use that as the `.padding(...)`. Example: for radius 26 + radius 8, use `padding(34)` or `padding(36)`.

## 3. UI Controls, Headers, or Buttons Visible in Product Shots
- **Symptom**: Mouse hover buttons, close/minimize dots, or scrubber heads clutter the shot.
- **Fix**: Use `.environment(\.forceControlsVisible, false)` and ensure hover states check `forceControlsVisible || (isHovered && isProximity)`. When taking product shots, hover is `false` and force is `false`, resulting in clean content.

## 4. Permission Denied Writing to docs/images
- **Symptom**: `Error writing screenshot-standard.png: Permission denied`.
- **Cause**: Sandboxed agent attempting to write to Desktop or non-whitelisted paths.
- **Fix**: Run snapshot build and command with `BypassSandbox: true`.
