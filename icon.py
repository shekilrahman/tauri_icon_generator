import os
import sys
import argparse
import shutil
import platform
import subprocess
from PIL import Image, ImageDraw

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def generate_icns(icon_path, output_dir):
    """Generate macOS .icns file if on macOS, otherwise create placeholder."""
    # Path for the iconset directory
    iconset_path = os.path.join(output_dir, 'icons/icons.iconset')
    create_directory(iconset_path)
    
    # Define icon sizes for macOS
    icon_sizes = [
        (16, '16x16.png'),
        (32, '16x16@2x.png'),
        (32, '32x32.png'),
        (64, '32x32@2x.png'),
        (128, '128x128.png'),
        (256, '128x128@2x.png'),
        (256, '256x256.png'),
        (512, '256x256@2x.png'),
        (512, '512x512.png'),
        (1024, '512x512@2x.png')
    ]
    
    # Open the original image
    original = Image.open(icon_path)
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    
    # Create all required icon sizes
    for size, filename in icon_sizes:
        img = original.copy()
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        img.save(os.path.join(iconset_path, filename), format='PNG')
    
    # Path for the output .icns file
    icns_path = os.path.join(output_dir, 'icons/icon.icns')
    
    # On macOS, use iconutil to generate the .icns file
    if platform.system() == 'Darwin':
        try:
            subprocess.run(['iconutil', '-c', 'icns', iconset_path, '-o', icns_path], check=True)
            print(f"Generated macOS .icns file: {icns_path}")
            # Clean up the iconset directory
            shutil.rmtree(iconset_path)
        except subprocess.CalledProcessError as e:
            print(f"Error generating .icns file: {e}")
            print("Creating placeholder .icns file instead...")
            create_icns_placeholder(original, icns_path)
    else:
        # On non-macOS systems, use the largest PNG as a substitute
        print("Not running on macOS, creating placeholder .icns file...")
        create_icns_placeholder(original, icns_path)
    
    return icns_path

def create_icns_placeholder(img, icns_path):
    """Create a placeholder for the .icns file."""
    img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    png_path = icns_path.replace('.icns', '.png')
    img.save(png_path, format='PNG')
    
    # Copy the PNG file to .icns for Tauri to find it
    shutil.copy2(png_path, icns_path)
    print(f"Created placeholder .icns file at {icns_path}")

def generate_ico(img, ico_path):
    """Generate Windows .ico file."""
    # Ensure the image is RGBA
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Save as ICO with multiple sizes
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f"Generated Windows .ico file: {ico_path}")

def make_round_image(image):
    """Generate a round version of the given image."""
    size = image.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    round_image = Image.new('RGBA', size)
    round_image.paste(image, mask=mask)
    return round_image

def generate_android_icons(original, output_dir, quality):
    """Generate Android launcher icons with the desired directory structure."""
    # Define densities and target sizes (in pixels)
    densities = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }
    
    for density, size in densities.items():
        density_dir = os.path.join(output_dir, "android", density)
        create_directory(density_dir)
        
        # Resize the original image to the target size
        img_resized = original.copy().resize((size, size), Image.Resampling.LANCZOS)
        
        # Save ic_launcher.png
        launcher_path = os.path.join(density_dir, "ic_launcher.png")
        img_resized.save(launcher_path, format="PNG", quality=quality)
        print(f"Generated Android launcher icon: {launcher_path}")
        
        # Save ic_launcher_foreground.png (for adaptive icons)
        foreground_path = os.path.join(density_dir, "ic_launcher_foreground.png")
        img_resized.save(foreground_path, format="PNG", quality=quality)
        print(f"Generated Android foreground icon: {foreground_path}")
        
        # Save ic_launcher_round.png (create round version)
        round_img = make_round_image(img_resized)
        round_path = os.path.join(density_dir, "ic_launcher_round.png")
        round_img.save(round_path, format="PNG", quality=quality)
        print(f"Generated Android round icon: {round_path}")

def generate_icons(input_file, output_dir, quality=90):
    """Generate all required Tauri app icons from an input image."""
    try:
        # Open the input image and convert to RGBA mode if needed
        original = Image.open(input_file)
        if original.mode != 'RGBA':
            print(f"Converting image from {original.mode} to RGBA mode...")
            original = original.convert('RGBA')
        
        # Define icon sizes and paths for various platforms
        icons = {
            # Windows icons
            'icons/32x32.png': (32, 32),
            
            # macOS icons
            'icons/128x128.png': (128, 128),
            'icons/128x128@2x.png': (256, 256),
            'icons/32x32@2x.png': (64, 64),
            'icons/icon.png': (1024, 1024),  # Default icon
            
            # iOS icons
            'icons/ios/16.png': (16, 16),
            'icons/ios/20.png': (20, 20),
            'icons/ios/29.png': (29, 29),
            'icons/ios/32.png': (32, 32),
            'icons/ios/40.png': (40, 40),
            'icons/ios/50.png': (50, 50),
            'icons/ios/57.png': (57, 57),
            'icons/ios/58.png': (58, 58),
            'icons/ios/60.png': (60, 60),
            'icons/ios/64.png': (64, 64),
            'icons/ios/72.png': (72, 72),
            'icons/ios/76.png': (76, 76),
            'icons/ios/80.png': (80, 80),
            'icons/ios/87.png': (87, 87),
            'icons/ios/100.png': (100, 100),
            'icons/ios/114.png': (114, 114),
            'icons/ios/120.png': (120, 120),
            'icons/ios/128.png': (128, 128),
            'icons/ios/144.png': (144, 144),
            'icons/ios/152.png': (152, 152),
            'icons/ios/167.png': (167, 167),
            'icons/ios/180.png': (180, 180),
            'icons/ios/192.png': (192, 192),
            'icons/ios/256.png': (256, 256),
            'icons/ios/512.png': (512, 512),
            'icons/ios/1024.png': (1024, 1024),
            
            # Linux icons
            'icons/128x128.png': (128, 128),
            'icons/256x256.png': (256, 256),
            'icons/512x512.png': (512, 512),
            'icons/1024x1024.png': (1024, 1024),
        }
        
        # Create the output directories for general icons and platform-specific icons
        create_directory(os.path.join(output_dir, 'icons'))
        create_directory(os.path.join(output_dir, 'icons/ios'))
        
        # Save general icons (Windows, macOS default, iOS, Linux)
        for icon_path, size in icons.items():
            img = original.copy().resize(size, Image.Resampling.LANCZOS)
            # Ensure the image is in RGBA mode
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            full_output_path = os.path.join(output_dir, icon_path)
            os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
            img.save(full_output_path, format='PNG', quality=quality)
            print(f"Generated: {full_output_path}")
        
        # Generate Windows ICO file
        ico_path = os.path.join(output_dir, 'icons/icon.ico')
        generate_ico(original, ico_path)
        
        # Generate macOS ICNS file
        icns_path = generate_icns(input_file, output_dir)
        
        # Generate Android icons with the desired directory structure
        generate_android_icons(original, output_dir, quality)
        
        print(f"\nIcon generation completed successfully to {output_dir}")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Generate Tauri app icons from a source image')
    parser.add_argument('input', help='Input image file path')
    parser.add_argument('-o', '--output', default='./tauri-icons', help='Output directory (default: ./tauri-icons)')
    parser.add_argument('-q', '--quality', type=int, default=90, help='PNG quality (0-100, default: 90)')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        sys.exit(1)
    
    generate_icons(args.input, args.output, args.quality)

if __name__ == "__main__":
    main()
