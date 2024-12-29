# YT Downloader

⚠️ **For Educational Purposes Only**

A simple YT video downloader built with Python and CustomTkinter. This application demonstrates how to create a modern GUI application that interacts with web APIs.

> **macOS Users**: A fully packaged application is available in the [Releases](https://github.com/jviars/ytdownloader/releases) section.

## Prerequisites

### FFmpeg Installation
FFmpeg is required for this application to work. Install it using one of these commands based on your operating system:

**Windows:**
```bash
winget install Gyan.FFmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

## Features
- Clean, modern dark-mode interface
- Video quality selection
- Download progress tracking
- Thumbnail preview
- Audio-only download option
- Support for various video resolutions (up to 8K)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jviars/ytdownloader.git
cd ytdownloader
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Launch the application:
```bash
python YTDownloader.py
```

2. Paste a YouTube URL
3. Click "Fetch Info" to load video details
4. Select your desired quality
5. Click "Download" and choose your save location

## Dependencies
### These are included in requirements.txt

- customtkinter
- yt-dlp
- Pillow
- requests
### This is not

- FFmpeg (external dependency)

## Legal Notice

This application is intended for educational purposes only. It demonstrates:
- GUI development with Python
- API integration
- Asynchronous programming
- Error handling
- Modern UI design

Please respect YouTube's terms of service and content creators' rights. Only download videos that you have permission to download.

## Contributing

Feel free to fork this project and submit pull requests. Please ensure you maintain appropriate error handling and user feedback in any modifications.

## License

This project is available under the MIT License. Please note that this doesn't grant any rights to download copyrighted content.

## Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Video processing handled by [yt-dlp](https://github.com/yt-dlp/yt-dlp)
