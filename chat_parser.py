import sys
import os
import datetime
from chat_simulator import generate_chat_image

def parse_conversations(file_path):
    """
    Reads the file line by line, ignoring lines that don't start with A: or B:.
    Groups consecutive A:/B: lines into one conversation, until the next ignored line.
    Returns a list of conversations, where each conversation is a list of (role, text) tuples.
    """
    conversations = []
    current_conversation = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            # Check if line begins with 'A:' or 'B:'
            if stripped.startswith('A: '):
                role = 'sender'
                text = stripped[3:].strip()  # text after "A:"
                current_conversation.append((role, text))
            elif stripped.startswith('B: '):
                role = 'receiver'
                text = stripped[3:].strip()  # text after "B:"
                current_conversation.append((role, text))
            else:
                # If the line doesn't match A: or B:, finalize the current conversation (if any)
                if current_conversation:
                    conversations.append(current_conversation)
                    current_conversation = []

    # Append any conversation that may be pending at the end of the file
    if current_conversation:
        conversations.append(current_conversation)

    return conversations

def main(input_file):
    conversations = parse_conversations(input_file)

    # Create an output folder with the current timestamp formatted as MM_DD_YYYY_HHMSS
    timestamp = datetime.datetime.now().strftime("%m_%d_%Y_%H%M%S")
    content_dir = os.path.join(os.getcwd(), "content")
    os.makedirs(content_dir, exist_ok=True)  # Create content directory if it doesn't exist
    output_dir = os.path.join(content_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output images will be saved in: {output_dir}")

    # Generate a chat image for each conversation and save it in the output folder
    for i, convo in enumerate(conversations, start=1):
        output_file = os.path.join(output_dir, f"conversation_{i}.png")
        generate_chat_image(
            messages=convo,
            output_file=output_file,
            image_size=(1290, 1290),
            bubble_font_size=40,
            time_font_size=34,
            bottom_padding=280,
            left_margin=190,   # Adjust left margin
            right_margin=40    # Adjust right margin
        )
        print(f"Saved {output_file}")

if __name__ == "__main__":
    # Expect the input filename as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python chat_parser.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
