import os
import random
from PIL import Image, ImageDraw, ImageFont

def load_ios_fonts(font_size=36, time_size=28):
    """
    Tries to load iOS-like fonts (SF) first, then Helvetica,
    and falls back to the default PIL font if none are found.
    Returns two PIL ImageFont objects: (bubble_font, time_font).
    """
    possible_sf_fonts = [
        "fonts/sf-pro-text-regular.ttf",
        "fonts/SFUIText-Regular.ttf",
        "fonts/SanFrancisco.ttf"
    ]

    font_bubble_path = None
    font_time_path = None

    # Check for any SF font file in the fonts directory
    for sf_font in possible_sf_fonts:
        if os.path.isfile(sf_font):
            font_bubble_path = sf_font
            font_time_path = sf_font
            break

    # Attempt to load the SF font if found
    if font_bubble_path:
        try:
            font_bubble = ImageFont.truetype(font_bubble_path, font_size)
            font_time = ImageFont.truetype(font_time_path, time_size)
            return font_bubble, font_time
        except IOError:
            pass

    # Otherwise, try Helvetica
    helvetica_names = ["fonts/Helvetica.ttf", "fonts/HelveticaNeue.ttf"]
    for helv_font in helvetica_names:
        if os.path.isfile(helv_font):
            try:
                font_bubble = ImageFont.truetype(helv_font, font_size)
                font_time = ImageFont.truetype(helv_font, time_size)
                return font_bubble, font_time
            except IOError:
                pass

    # Fallback to the PIL default font
    print("Warning: SF/Helvetica not found. Using default font.")
    default_font = ImageFont.load_default()
    return default_font, default_font


def create_blank_image(width, height, background_color=(255, 255, 255)):
    """
    Creates and returns a blank RGB image of the specified size
    with a given background color.
    """
    return Image.new("RGB", (width, height), color=background_color)


def measure_text(draw_obj, text, font):
    """
    Measures the width and height of the given text using textbbox()
    and returns them as (width, height).
    """
    bbox = draw_obj.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_chat_bubble(draw_obj, bubble_coords, corner_radius, bubble_color, outline_color):
    """
    Draws a rounded rectangle (chat bubble) with a specified corner radius,
    fill color, and outline color on the provided draw object.
    """
    draw_obj.rounded_rectangle(
        bubble_coords,
        radius=corner_radius,
        fill=bubble_color,
        outline=outline_color,
        width=3
    )


def generate_random_timestamp():
    """
    Generates a random timestamp in HH:MM (24-hour) format.
    """
    rand_hour = random.randint(0, 23)
    rand_minute = random.randint(0, 59)
    return f"{rand_hour:02d}:{rand_minute:02d}"


def wrap_text(text, font, draw_obj, max_width):
    """
    Wraps a string into multiple lines so that each line's width
    does not exceed max_width when rendered with the given font.
    Returns a list of wrapped lines.
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        w, _ = measure_text(draw_obj, test_line, font)
        if w <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def generate_chat_image(
        messages=None,
        output_file="conversation.png",
        image_size=(1290, 1290),
        bubble_font_size=36,
        time_font_size=28,
        bottom_padding=65,
        left_margin=108,
        right_margin=108,
        bubble_margin=22,         # Gap between different people’s messages
        same_person_margin=2     # NEW: Gap between consecutive messages from the same person
):
    """
    Generates an image simulating chat bubbles with optional custom margins,
    fonts, and image size. Saves the final image to 'output_file'.

    Parameters:
      - messages: List of (role, text) tuples, e.g. [("sender", "Hi"), ("receiver", "Hello")]
      - output_file: Name of the output PNG file
      - image_size: Tuple defining the (width, height) of the image
      - bubble_font_size: Font size for chat bubble text
      - time_font_size: Font size for timestamps
      - bottom_padding: Extra space at the bottom of the image
      - left_margin: How far sender bubbles are inset from the left
      - right_margin: How far receiver bubbles are inset from the right
      - bubble_margin: Vertical gap between bubbles from different roles
      - same_person_margin: Vertical gap between consecutive bubbles from the same role
    """

    if messages is None:
        messages = [
            ("sender", "Hello!"),
            ("receiver", "Just letting you know the codes are working fine."),
            ("receiver", "This message is intentionally longer, ensuring multiple "
                         "lines for a nice demonstration of wrapping.")
        ]

    # Create a blank canvas
    img_width, img_height = image_size
    img = create_blank_image(img_width, img_height, background_color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Load fonts for bubbles and timestamps
    font_bubble, font_time = load_ios_fonts(font_size=bubble_font_size, time_size=time_font_size)

    # Generate a random time for the oldest message
    time_text = generate_random_timestamp()

    # Layout and styling constants
    bubble_padding = 32
    line_spacing = 8
    corner_radius = 50
    bubble_max_fraction = 0.65
    bubble_max_text_width = int((img_width * bubble_max_fraction) - (2 * bubble_padding))

    current_y = img_height - bottom_padding
    bottom_bubble_box = None
    top_bubble_box = None

    # Process messages in reverse (newest at the bottom)
    reversed_messages = list(reversed(messages))

    for i, (role, text) in enumerate(reversed_messages):
        # Wrap the message text
        lines = wrap_text(text, font_bubble, draw, bubble_max_text_width)

        # Measure each line for total bubble width/height
        line_widths = []
        line_heights = []
        for line in lines:
            w, h = measure_text(draw, line, font_bubble)
            line_widths.append(w)
            line_heights.append(h)

        if lines:
            text_block_width = max(line_widths)
            text_block_height = sum(line_heights) + (line_spacing * (len(lines) - 1))
            line_height = line_heights[0]
        else:
            # Minimal fallback for empty text
            text_block_width = 0
            text_block_height = 0
            line_height = measure_text(draw, "Test", font_bubble)[1]

        # Determine final bubble dimensions
        bubble_width = text_block_width + (2 * bubble_padding)
        bubble_height = text_block_height + (2 * bubble_padding)

        bubble_bottom = current_y
        bubble_top = bubble_bottom - bubble_height

        # Position bubble depending on sender or receiver
        if role == "sender":
            bubble_left = left_margin
            bubble_right = bubble_left + bubble_width
            bubble_color = (255, 255, 255)      # White
            outline_color = (230, 230, 230)     # Light gray
        else:
            bubble_right = img_width - right_margin
            bubble_left = bubble_right - bubble_width
            bubble_color = (240, 240, 240)      # Light gray bubble
            outline_color = (255, 255, 255)     # White outline

        # Draw the rounded chat bubble
        draw_chat_bubble(
            draw_obj=draw,
            bubble_coords=(bubble_left, bubble_top, bubble_right, bubble_bottom),
            corner_radius=corner_radius,
            bubble_color=bubble_color,
            outline_color=outline_color
        )

        # Render the text inside the bubble
        text_x = bubble_left + bubble_padding
        text_y = bubble_top + (bubble_padding / 2)
        for idx, line in enumerate(lines):
            draw.text((text_x, text_y), line, fill=(0, 0, 0), font=font_bubble)
            text_y += line_height
            if idx < len(lines) - 1:
                text_y += line_spacing

        # Track bubble positions for newest (bottom) and oldest (top)
        if i == 0:  # newest bubble
            bottom_bubble_box = (bubble_left, bubble_top, bubble_right, bubble_bottom)
        if i == len(reversed_messages) - 1:  # oldest bubble
            top_bubble_box = (bubble_left, bubble_top, bubble_right, bubble_bottom)

        # Decide how far up to move for the next bubble
        if i < len(reversed_messages) - 1:
            next_role, _ = reversed_messages[i + 1]
            if next_role == role:
                # Same role => use same_person_margin
                current_y = bubble_top - same_person_margin
            else:
                # Different role => use bubble_margin
                current_y = bubble_top - bubble_margin
        else:
            # This was the last bubble (oldest), just use bubble_margin
            current_y = bubble_top - bubble_margin

    # If the newest bubble is from receiver, show "Seen just now" below it
    if bottom_bubble_box is not None:
        newest_role, _ = messages[-1]
        if newest_role == "receiver":
            seen_text = "Seen just now"
            seen_width, _ = measure_text(draw, seen_text, font_time)
            l, t, r, b = bottom_bubble_box
            seen_x = r - seen_width
            seen_y = b + 10
            draw.text((seen_x, seen_y), seen_text, fill=(128, 128, 128), font=font_time)

    # Add a random timestamp above the oldest bubble
    if top_bubble_box is not None:
        l, t, r, b = top_bubble_box
        time_width, time_height = measure_text(draw, time_text, font_time)
        time_x = (img_width // 2) - (time_width // 2)
        time_y = t - time_height - 50
        draw.text((time_x, time_y), time_text, fill=(128, 128, 128), font=font_time)

    # Save the final image
    img.save(output_file)
    print(f"Chat image saved as {output_file}")


if __name__ == "__main__":
    # Example usage with custom margins
    sample_messages = [
        ("sender", "How do I slow down?"),
        ("receiver", "Breathe. Notice the small things. Let go of the rest."),
        ("receiver", "Another message from the same person to test spacing.")
    ]
    generate_chat_image(
        messages=sample_messages,
        output_file="conversation.png",
        image_size=(1290, 1290),
        bubble_font_size=40,
        time_font_size=34,
        bottom_padding=280,
        left_margin=190,
        right_margin=40,
        bubble_margin=30,        # Gap between different people's messages
        same_person_margin=10    # Gap between the same person's consecutive messages
    )
