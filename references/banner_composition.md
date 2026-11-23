# Marketing Banner Composition Guide

A dedicated hero banner (`musi-banner.png` or `banner.png`) at the top of a repository or landing page significantly boosts conversion and visual appeal.

## Optimal Dimensions
- **Aspect Ratio**: 2:1 (1280 × 640 @ 1x → 2560 × 1280 @ 2x Retina PNG).

## Canvas Anatomy

```text
┌────────────────────────────────────────────────────────────────────────┐
│  Ambient Glow 1 (Purple)                     Ambient Glow 2 (Pink)     │
│                                                                        │
│   [Icon] App Name                                  [ Mini Form Factor ]│
│                                                                        │
│   Bold Tagline Line 1                                                  │
│   Bold Tagline Line 2                              [ Standard Hero ]   │
│                                                                        │
│   Concise explanatory paragraph                                        │
│                                                                        │
│   [Pill 1] [Pill 2]                                [ Compact Card ]    │
│   [Pill 3] [Pill 4]                                                    │
│                                               Ambient Glow 3 (Blue)    │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Dark Futuristic Backdrop
```swift
LinearGradient(
    colors: [
        Color(red: 0.04, green: 0.04, blue: 0.07),
        Color(red: 0.07, green: 0.06, blue: 0.14),
        Color(red: 0.10, green: 0.08, blue: 0.18),
        Color(red: 0.04, green: 0.04, blue: 0.08)
    ],
    startPoint: .topLeading,
    endPoint: .bottomTrailing
)
```

### 2. Ambient Color Spheres
Use blurred circles placed at offsets:
```swift
Circle()
    .fill(Color.purple.opacity(0.30))
    .frame(width: 550, height: 550)
    .blur(radius: 90)
    .offset(x: -250, y: -80)
```

### 3. Feature Pills
```swift
HStack(spacing: 8) {
    Image(systemName: icon)
    Text(title)
}
.padding(.horizontal, 12)
.padding(.vertical, 6)
.background(
    RoundedRectangle(cornerRadius: 12, style: .continuous)
        .fill(Color.white.opacity(0.08))
        .overlay(RoundedRectangle(cornerRadius: 12).strokeBorder(Color.white.opacity(0.14), lineWidth: 1))
)
```
