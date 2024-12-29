import os
import threading
from tkinter import filedialog
import customtkinter as ctk
import yt_dlp
from PIL import Image
import requests
from io import BytesIO
import re


class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("YT Downloader")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)  # Make the last row expandable

        # URL Entry
        self.url_frame = ctk.CTkFrame(self.main_frame)
        self.url_frame.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Enter YT URL",
            height=40
        )
        self.url_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.fetch_button = ctk.CTkButton(
            self.url_frame,
            text="Fetch Info",
            command=self.fetch_video_info,
            width=100,
            height=40
        )
        self.fetch_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Video info frame
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.info_frame.grid_columnconfigure(1, weight=1)

        # Thumbnail
        self.thumbnail_label = ctk.CTkLabel(self.info_frame, text="")
        self.thumbnail_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

        # Title
        self.title_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            wraplength=400,
            justify="left"
        )
        self.title_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Duration
        self.duration_label = ctk.CTkLabel(self.info_frame, text="")
        self.duration_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Available qualities
        self.quality_info_label = ctk.CTkLabel(self.info_frame, text="")
        self.quality_info_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Download options frame
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.options_frame.grid_columnconfigure(1, weight=1)

        # Quality selection
        self.quality_label = ctk.CTkLabel(self.options_frame, text="Quality:")
        self.quality_label.grid(row=0, column=0, padx=10, pady=10)

        # Initial quality options (will be updated when video is fetched)
        self.default_qualities = ["Please Input a video URL and the available qualities will update."]
        self.quality_var = ctk.StringVar(value=self.default_qualities[0])
        self.quality_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=self.default_qualities,
            variable=self.quality_var,
            state="disabled"
        )
        self.quality_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Download button
        self.download_button = ctk.CTkButton(
            self.options_frame,
            text="Download",
            command=self.download_video,
            state="disabled",
            height=40
        )
        self.download_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.options_frame)
        self.progress_bar.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(self.options_frame, text="")
        self.status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        # Footer label
        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text="This application was created by jviars for educational purposes only. Please read the bundled licensing details.",
            text_color="gray75",
            font=("Helvetica", 10)
        )
        self.footer_label.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="sew")

        self.video_info = None
        self.available_formats = {}

    def get_available_formats(self, formats):
        available = {
            "Audio Only": "bestaudio"
        }
        
        # Look for available resolutions
        resolutions = set()
        for f in formats:
            if f.get('height'):
                resolutions.add(f['height'])
        
        # Standard resolutions we want to check
        standard_res = {
            '8K': 4320,
            '4K': 2160,
            '1440p': 1440,
            '1080p': 1080,
            '720p': 720,
            '480p': 480,
            '360p': 360
        }
        
        # Add available resolutions to the format dictionary
        for label, height in standard_res.items():
            if any(res >= height for res in resolutions):
                # Format string that properly selects specific resolutions
                available[label] = (
                    f'bestvideo[height={height}]+bestaudio/'  # Try exact resolution first
                    f'bestvideo[height<={height}][height>={height-120}]+bestaudio/'  # Then try close matches
                    f'best[height<={height}][height>={height-120}]'  # Finally try combined formats
                )
        
        return dict(sorted(available.items(), key=lambda x: (
            float('inf') if x[0] == "Audio Only" 
            else int(x[0].replace('K', '000').replace('p', ''))
        ), reverse=True))

    def fetch_video_info(self):
        url = self.url_entry.get()
        if not self.is_valid_youtube_url(url):
            self.status_label.configure(text="Please enter a valid YT URL")
            return

        def fetch():
            try:
                self.fetch_button.configure(state="disabled")
                self.status_label.configure(text="Fetching video information...")
                self.quality_menu.configure(state="disabled", values=["Loading..."])
                self.download_button.configure(state="disabled")

                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.video_info = ydl.extract_info(url, download=False)

                # Get thumbnail
                response = requests.get(self.video_info['thumbnail'])
                img = Image.open(BytesIO(response.content))
                img = img.resize((160, 90), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 90))
                self.thumbnail_label.configure(image=photo)
                self.thumbnail_label.image = photo

                # Update video information
                self.title_label.configure(text=self.video_info['title'])
                duration_mins = self.video_info['duration'] // 60
                duration_secs = self.video_info['duration'] % 60
                self.duration_label.configure(
                    text=f"Duration: {duration_mins}:{duration_secs:02d}"
                )

                # Get available formats and update quality menu
                self.available_formats = self.get_available_formats(self.video_info['formats'])
                quality_options = list(self.available_formats.keys())

                # Update quality info label
                max_res = max([f['height'] for f in self.video_info['formats'] if f.get('height')] or [0])
                self.quality_info_label.configure(
                    text=f"Available up to {max_res}p"
                )

                # Update quality menu
                self.quality_menu.configure(
                    values=quality_options,
                    state="normal"
                )
                self.quality_var.set(quality_options[1] if len(quality_options) > 1 else quality_options[0])

                # Enable download button
                self.download_button.configure(state="normal")
                self.status_label.configure(text="Ready to download")
                self.fetch_button.configure(state="normal")

            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}")
                self.fetch_button.configure(state="normal")
                self.quality_menu.configure(values=["Error"])
                self.quality_menu.configure(state="disabled")

        threading.Thread(target=fetch, daemon=True).start()

    def download_video(self):
        if not self.video_info:
            return

        save_path = filedialog.askdirectory()
        if not save_path:
            return

        def download_progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    if total:
                        percentage = downloaded / total
                        self.progress_bar.set(percentage)
                        self.status_label.configure(
                            text=f"Downloading... {percentage:.1%}"
                        )
                except Exception:
                    pass
            elif d['status'] == 'finished':
                self.status_label.configure(text="Download completed!")
                self.progress_bar.set(0)

        def download():
            try:
                self.download_button.configure(state="disabled")
                self.status_label.configure(text="Starting download...")
                quality = self.quality_var.get()

                ydl_opts = {
                    'format': self.available_formats[quality],
                    'progress_hooks': [download_progress_hook],
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4',
                    'postprocessor_args': ['-c:v', 'copy', '-c:a', 'copy'],
                    'ignoreerrors': True,
                    'format_sort': ['res', 'ext'],
                    'prefer_native_hls': True
                }

                if quality == "Audio Only":
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }]

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.video_info['webpage_url']])

                self.download_button.configure(state="normal")

            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}")
                self.download_button.configure(state="normal")
                self.progress_bar.set(0)

        threading.Thread(target=download, daemon=True).start()

    def is_valid_youtube_url(self, url):
        youtube_regex = (
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return bool(re.match(youtube_regex, url))


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()