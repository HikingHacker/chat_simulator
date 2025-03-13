# Content Automation Toolkit

A Python toolkit for automatically generating chat bubble images that mimic messaging apps. This project makes it easy to convert text conversations into realistic chat screenshots.

## Features

- Convert text-based conversations to realistic chat bubble images
- Customizable bubble styles, fonts, and margins
- Supports multi-line messages with automatic text wrapping
- Adds realistic details like timestamps and "Seen" indicators

## Project Structure

- `chat_parser.py`: Parses text conversations and generates images
- `chat_simulator.py`: Creates chat bubble images with customizable styling
- `conversations/`: Contains text files with conversation data
- `fonts/`: Stores font files for text rendering
- `content/`: Output directory for generated images

## Usage

### Parsing a Conversation File

```bash
python chat_parser.py conversations/all_conversations.txt
```

Conversation files should use the format:
```
A: This is a message from person A
B: This is a reply from person B
```

### Direct Image Generation

```bash
python chat_simulator.py "Hello, how are you?" sender
```

## Requirements

- Python 3.6+
- Pillow (PIL Fork) library