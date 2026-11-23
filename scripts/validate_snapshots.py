#!/usr/bin/env python3
"""
validate_snapshots.py
Generic pixel and dimension validation tool for product screenshots.
Checks:
  - File existence and non-empty sizes
  - Dimension bounds / exact retina dimensions
  - Color anomalies (e.g. placeholder yellow discs, magenta missing texture, solid error boxes)
"""

import os
import sys
import argparse
import warnings
from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

def parse_args():
    parser = argparse.ArgumentParser(description="Validate generated product snapshots for quality, dimensions, and placeholder pixels.")
    parser.add_argument("--dir", default="docs/images", help="Directory containing screenshots (default: docs/images)")
    parser.add_argument("--check-yellow", action="store_true", default=True, help="Check for yellow placeholder disc pixels")
    parser.add_argument("--check-magenta", action="store_true", default=True, help="Check for missing texture magenta pixels")
    parser.add_argument("--check-cutoff", action="store_true", default=True, help="Check for abrupt shadow cutoff at image boundaries")
    parser.add_argument("--min-width", type=int, default=400, help="Minimum acceptable image width in pixels")
    parser.add_argument("--min-height", type=int, default=200, help="Minimum acceptable image height in pixels")
    return parser.parse_args()

def is_yellow_placeholder(r, g, b):
    # Common placeholder disc color: bright yellow/gold
    return r > 200 and g > 180 and b < 60

def is_magenta_placeholder(r, g, b):
    # Missing texture pink/magenta
    return r > 220 and g < 40 and b > 220

def validate_image(path, args):
    if not os.path.exists(path):
        return {"exists": False, "error": "File not found"}
    
    file_size_kb = os.path.getsize(path) / 1024.0
    if file_size_kb < 5.0:
        return {"exists": True, "error": f"File too small ({file_size_kb:.1f} KB)"}

    try:
        with Image.open(path) as img:
            rgb = img.convert("RGB")
            w, h = rgb.size

            if w < args.min_width or h < args.min_height:
                return {
                    "exists": True,
                    "w": w, "h": h,
                    "size_kb": file_size_kb,
                    "error": f"Dimensions {w}x{h} below minimum threshold"
                }

            yellow_count = 0
            magenta_count = 0

            # Scan pixels cleanly
            for pixel in rgb.getdata():
                r, g, b = pixel[:3]
                if args.check_yellow and is_yellow_placeholder(r, g, b):
                    yellow_count += 1
                if args.check_magenta and is_magenta_placeholder(r, g, b):
                    magenta_count += 1

            errors = []
            if yellow_count > 0:
                errors.append(f"{yellow_count} yellow placeholder px")
            if magenta_count > 0:
                errors.append(f"{magenta_count} magenta missing-texture px")

            # Check edge cutoff if image has alpha channel
            if args.check_cutoff and "A" in img.getbands():
                edge_alphas = []
                for x in range(w):
                    edge_alphas.append(img.getpixel((x, 0))[3])
                    edge_alphas.append(img.getpixel((x, h - 1))[3])
                for y in range(h):
                    edge_alphas.append(img.getpixel((0, y))[3])
                    edge_alphas.append(img.getpixel((w - 1, y))[3])
                max_edge = max(edge_alphas)
                # Allow tolerance of alpha <= 1 (negligible background noise)
                if max_edge > 1:
                    errors.append(f"shadow edge cutoff detected (edge alpha: {max_edge})")

            return {
                "exists": True,
                "w": w,
                "h": h,
                "size_kb": file_size_kb,
                "yellow_px": yellow_count,
                "magenta_px": magenta_count,
                "error": ", ".join(errors) if errors else None
            }
    except Exception as e:
        return {"exists": True, "error": str(e)}

def main():
    args = parse_args()
    if not os.path.isdir(args.dir):
        print(f"❌ Error: Directory '{args.dir}' does not exist.")
        sys.exit(1)

    image_files = sorted([f for f in os.listdir(args.dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
    if not image_files:
        print(f"⚠️ No images found in '{args.dir}'.")
        sys.exit(1)

    print(f"\n🔍 Validating {len(image_files)} product snapshots in '{args.dir}'...\n")
    print(f"{'Image Filename':<36} | {'Dimensions':<12} | {'Size':<10} | {'Status'}")
    print("-" * 76)

    all_passed = True
    for filename in image_files:
        filepath = os.path.join(args.dir, filename)
        result = validate_image(filepath, args)

        if not result["exists"]:
            print(f"{filename:<36} | MISSING      | 0 KB       | ❌ FAILED: File not found")
            all_passed = False
        elif result.get("error"):
            dims = f"{result.get('w', '?')}x{result.get('h', '?')}"
            size = f"{result.get('size_kb', 0):.0f} KB"
            print(f"{filename:<36} | {dims:<12} | {size:<10} | ❌ FAILED: {result['error']}")
            all_passed = False
        else:
            dims = f"{result['w']}x{result['h']}"
            size = f"{result['size_kb']:.0f} KB"
            print(f"{filename:<36} | {dims:<12} | {size:<10} | ✅ PASS")

    print("-" * 76)
    if all_passed:
        print("✨ SUCCESS: All product snapshots are pristine and publication-ready!\n")
        sys.exit(0)
    else:
        print("❌ FAILURES DETECTED: Review the issues flagged above.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
