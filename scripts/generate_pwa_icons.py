"""
Generate PWA icons in all required sizes
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Icon sizes required for PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Additional shortcut icons
SHORTCUT_ICONS = {
    'submit': 96,
    'grades': 96
}

# Colors
BG_COLOR = '#3b82f6'  # Blue theme color
TEXT_COLOR = '#ffffff'  # White text


def create_icon(size, output_path, text='AI'):
    """Create a simple icon with text"""
    # Create image with blue background
    img = Image.new('RGB', (size, size), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Calculate font size (roughly 40% of icon size)
    font_size = int(size * 0.4)

    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2

    # Draw text
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)

    # Add a border for visual appeal
    border_width = max(2, size // 50)
    draw.rectangle(
        [(border_width, border_width),
         (size - border_width, size - border_width)],
        outline='#1e293b',
        width=border_width
    )

    # Save the icon
    img.save(output_path, 'PNG')
    print(f"✓ Created {output_path}")


def create_shortcut_icon(name, size, output_path):
    """Create shortcut icons with specific symbols"""
    img = Image.new('RGB', (size, size), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Different symbols for different shortcuts
    symbols = {
        'submit': '✓',
        'grades': '★'
    }

    text = symbols.get(name, '?')
    font_size = int(size * 0.5)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2

    draw.text((x, y), text, fill=TEXT_COLOR, font=font)

    img.save(output_path, 'PNG')
    print(f"✓ Created {output_path}")


def main():
    """Generate all PWA icons"""
    # Create icons directory
    icons_dir = 'static/icons'
    os.makedirs(icons_dir, exist_ok=True)

    print("Generating PWA icons...")
    print("=" * 50)

    # Generate main app icons
    for size in ICON_SIZES:
        filename = f'icon-{size}x{size}.png'
        output_path = os.path.join(icons_dir, filename)
        create_icon(size, output_path)

    print("\nGenerating shortcut icons...")
    print("=" * 50)

    # Generate shortcut icons
    for name, size in SHORTCUT_ICONS.items():
        filename = f'{name}-{size}x{size}.png'
        output_path = os.path.join(icons_dir, filename)
        create_shortcut_icon(name, size, output_path)

    print("\n" + "=" * 50)
    print(f"✓ Successfully generated {len(ICON_SIZES) + len(SHORTCUT_ICONS)} icons")
    print(f"✓ Icons saved to: {icons_dir}/")


if __name__ == '__main__':
    main()
