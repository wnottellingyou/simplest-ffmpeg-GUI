# FFmpeg GUI - Complete Edition

A comprehensive, user-friendly GUI application for FFmpeg built with Python and Tkinter. This application provides an intuitive interface for common video and audio processing tasks without requiring command-line knowledge.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

### 🎬 Format Conversion
- Convert between all major video/audio formats
- Codec selection (H.264, H.265, VP9, AV1, etc.)
- Quality control (CRF, preset, bitrate)
- Resolution adjustment with presets (4K, 1080p, 720p, etc.)
- FPS control
- Hardware acceleration support (NVENC, QSV, AMF)
- Custom FFmpeg arguments

### ✂️ Video Editing
- **Trim/Cut**: Extract video segments by start time and duration
- **Merge**: Concatenate multiple videos with drag-and-drop reordering
- **Filters**:
  - Rotation (90°, 180°, 270°)
  - Flip (horizontal/vertical)
  - Speed adjustment (0.25x to 4x)
  - Brightness/Contrast/Saturation
  - Blur effect

### 🎵 Audio Extraction
- Extract audio from video files
- Multiple format support (MP3, AAC, WAV, FLAC, OGG, Opus)
- Codec and quality settings
- Volume adjustment
- Audio trimming
- Fade in/out effects
- Channel selection (mono/stereo)

### 📦 Batch Processing
- Process multiple files or entire folders
- Four operation types:
  - Format conversion
  - Audio extraction
  - Resize
  - Apply filters
- Custom output patterns
- Progress tracking for each file

### 🔧 Advanced Features
- **Subtitles**:
  - Soft subtitles (embedded as separate stream)
  - Hard subtitles (burned into video)
  - Font customization for hard subs
- **Watermark**:
  - Add image overlays
  - Position control (5 presets)
  - Opacity and margin adjustment
- **Video Info**:
  - View detailed metadata
  - Format, codec, resolution, bitrate information

### 📊 User Experience
- Real-time progress bars with percentage
- Video preview integration (FFplay)
- Stop button on all processing tabs
- Persistent configuration (saves last used settings)
- Show command before execution
- Comprehensive error handling

## Prerequisites

### Required Software
1. **Python 3.7 or higher**
   - Download from [python.org](https://www.python.org/downloads/)

2. **FFmpeg**
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **Important**: Add FFmpeg to your system PATH

   **Windows Installation:**
   - Download FFmpeg build (recommended: gyan.dev or BtbN builds)
   - Extract to a folder (e.g., `C:\ffmpeg`)
   - Add `C:\ffmpeg\bin` to system PATH:
     1. Search "Environment Variables" in Windows
     2. Edit "Path" variable
     3. Add new entry with FFmpeg bin folder path
     4. Restart terminal/IDE

### Verify Installation
```bash
# Check Python
python --version

# Check FFmpeg
ffmpeg -version

# Check FFprobe
ffprobe -version

# Check FFplay
ffplay -version
```

## Installation

1. **Clone or download this repository**
```bash
git clone <repository-url>
cd simpliest_ffmpeg_GUI
```

2. **No additional Python packages required**
   - Uses only Python standard library (tkinter, threading, subprocess, json, pathlib)

3. **Run the application**
```bash
python main.py
```

## Usage

### Basic Workflow

1. **Select a tab** based on your task (Format Conversion, Video Editing, etc.)
2. **Choose input file(s)** using the Browse button
3. **Configure settings** (format, quality, effects, etc.)
4. **Set output location** and filename
5. **Preview command** (optional) - Click "Show Command" to see the FFmpeg command
6. **Start processing** - Click "Start" button
7. **Monitor progress** - Watch the progress bar and status messages
8. **Stop if needed** - Use Stop button to cancel operation

### Examples

#### Convert MP4 to MKV with H.265
1. Go to **Format Conversion** tab
2. Select input MP4 file
3. Choose output format: **MKV**
4. Select video codec: **H.265 (HEVC)**
5. Adjust quality (CRF: 23 is good default)
6. Click **Start**

#### Extract Audio as MP3
1. Go to **Audio Extraction** tab
2. Select input video file
3. Choose format: **MP3**
4. Set bitrate: **192k** or **320k**
5. Adjust volume if needed
6. Click **Start**

#### Trim Video
1. Go to **Video Editing** → **Trim/Cut** tab
2. Select input file
3. Set start time (e.g., 00:01:30)
4. Set duration or end time
5. Click **Start**

#### Batch Convert Videos
1. Go to **Batch Processing** tab
2. Click **Add Files** or **Add Folder**
3. Select operation: **Format Conversion**
4. Choose output format and settings
5. Set output folder
6. Click **Start Batch**

#### Add Subtitles
1. Go to **Advanced** → **Subtitles** tab
2. Select input video file
3. Select subtitle file (.srt, .ass, .vtt)
4. Choose soft (embedded) or hard (burned-in)
5. Customize font settings for hard subs
6. Click **Start**

## Configuration

Settings are automatically saved to `config.json` in the application directory, including:
- Last used directories
- Format preferences
- Quality settings
- Window geometry

## Troubleshooting

### "FFmpeg not found" error
- Ensure FFmpeg is installed and added to system PATH
- Restart your terminal/command prompt after adding to PATH
- Test with `ffmpeg -version` in terminal

### Progress bar stuck at 0%
- Some operations (like codec probing) take time before progress starts
- Check if FFmpeg is actually running (Task Manager on Windows)
- If truly stuck, use Stop button and check input file validity

### Batch processing fails
- Ensure all input files are valid video/audio files
- Check that output folder has write permissions
- Verify sufficient disk space

### Video preview doesn't work
- Ensure FFplay is installed (comes with FFmpeg)
- Check that FFplay is in system PATH
- Some video formats may not be supported by FFplay

### Application won't start
- Verify Python 3.7+ is installed
- Check that tkinter is available: `python -m tkinter`
- On some Linux systems: `sudo apt-get install python3-tk`

## Limitations

- **Platform**: Optimized for Windows (uses `CREATE_NO_WINDOW` flag)
- **Hardware Acceleration**: Requires compatible GPU and drivers
- **Subtitle Styling**: Advanced ASS styling only available with hard subs
- **Preview**: FFplay opens in separate window

## Technical Details

- **Language**: Python 3.7+
- **GUI Framework**: Tkinter (standard library)
- **FFmpeg Integration**: Subprocess with real-time output parsing
- **Threading**: Background processing to prevent UI freezing
- **Progress Tracking**: Regex parsing of FFmpeg progress output
- **Config**: JSON-based persistent storage

## Project Structure

```
simpliest_ffmpeg_GUI/
│
├── main.py           # Main application (single file)
├── config.json       # Auto-generated configuration
└── README.md         # This file
```

## Contributing

Contributions are welcome! Areas for improvement:
- GIF creation functionality
- Screenshot/thumbnail extraction
- Target file size compression
- Additional filters and effects
- Improved error messages
- Localization support

## License

MIT License - Feel free to use and modify for your needs.

## Acknowledgments

- FFmpeg project for the powerful media processing framework
- Python Tkinter for the cross-platform GUI toolkit

## Support

For issues, questions, or feature requests, please open an issue on the repository.

---

**Note**: This application is a GUI wrapper for FFmpeg. All processing is performed by FFmpeg itself. The quality and capabilities depend on your FFmpeg installation.
