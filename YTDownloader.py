import yt_dlp
import os
import io
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Configuration
#url = input("Paste the video URL here:").strip()
pasta_projeto = os.path.dirname(os.path.abspath(__file__))
pasta_downloads = os.path.join(pasta_projeto, "downloads")

# Variables

video_data = None
thubnail_tk = None

def analyze_video():
    global video_data, thubnail_tk

    url = urlGet.get().strip()

    if not url:
        messagebox.showwarning("Attention!", "Paste a YouTube url.")
        return

    status_var.set("Analyzing video...")
    window.update_idletasks()
    opcoes = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            video_data = ydl.extract_info(url, download=False)

        # Title
        title_var.set(video_data.get("title", "Unknown"))

        # Duration
        duration = video_data.get("duration")

        if duration:
            minutos = duration // 60
            segundos = duration % 60
            duration_var.set(f"{minutos}:{segundos:02d}")
        else:
            duration_var.set("Unknown")

        # Thumbnail
        thumbnail_url = video_data.get("thumbnail")

        if thumbnail_url:
            download_thumbnail(thumbnail_url)

        # Formatos
        load_format()

        status_var.set("Vídeo analisado!")

    except Exception as erro:
        status_var.set("Erro ao analisar.")
        messagebox.showerror("Erro", str(erro))

# Thumbnail

def download_thumbnail(url):
    global thubnail_tk

    try:
        import urllib.request

        with urllib.request.urlopen(url) as response:
            image_bytes = response.read()

        images = Image.open(io.BytesIO(image_bytes))

        images.thumbnail((400,225))

        thubnail_tk = ImageTk.PhotoImage(images)

        label_thumbnail.config(image = thubnail_tk, text="")

        label_thumbnail.image = thubnail_tk

    except Exception:
        label_thumbnail.config(text="Thumbnail indisponível")

# Formats

def load_format():
    formats = video_data.get("formats", [])
    options_video = []
    options_audio = []

    seen_heights = set()

    for format in formats:
        height = format.get("height")
        extention = format.get("ext")
        vcodec = format.get("vcodec")
        

        if not height or vcodec == "none":
            continue

        if height in seen_heights:
            continue

        seen_heights.add(height)


        text = f"{height}p - {extention} - video + audio"

        options_video.append(
            (height, format.get("format_id"), text)
        )

    options_video.sort(reverse=True)

    # Formats audio

    seenAudio = set()

    for format in formats:
        acodec = format.get("acodec")
        vcodec = format.get("vcodec")

        if acodec == "none" or vcodec != "none":
            continue

        bitrate = format.get("abr")
        ext = format.get("ext")

        if not bitrate:
            continue

        bitrate = round(bitrate)

        keys = (bitrate, ext)

        seenAudio.add(keys)

        text = f"Audio • {ext.upper()} • {bitrate} kbps"

        options_audio.append(
            (bitrate, format.get("format_id"), text)
        )

     # Sort by higher bitrate
    options_audio.sort(reverse=True)

    # List

    list_formats = []

    for height, format_id, text in options_video:
        list_formats.append(("video", format_id, text))

    for bitrate, format_id, text in options_audio:
        list_formats.append(("audio", format_id, text))


    combo_formats["values"] = [
        text for _, _, text in list_formats
    ]

    # Store IDs internaly
    combo_formats.formats = list_formats

    if list_formats:
        combo_formats.current(0)

# Download

def download_video():

    if not video_data:
        messagebox.showwarning(
            "Attention",
            "Analyze a video first "
        )
        return

    index = combo_formats.current()

    if index < 0:
        messagebox.showwarning(
            "Attention",
            "Choose a format."
        )
        return

    type, format_id, text = combo_formats.formats[index]

    url = video_data["webpage_url"]

    os.makedirs(pasta_downloads, exist_ok=True)

    if type == "audio":
        options = {
            "format": f"{format_id}",
            "outtmpl": os.path.join(pasta_downloads, "%(title)s.%(ext)s"),
            "ffmpeg_location": os.path.join(pasta_projeto, r"ffmpeg\bin"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320"
                }
            ]
        }
    else:
        options = {
                    "format": f"{format_id}+bestaudio/b",
                    "marge_output_format": "mp4",
                    "outtmpl": os.path.join(pasta_downloads, "%(title)s.%(ext)s"),
                    "ffmpeg_location": os.path.join(pasta_projeto, r"ffmpeg\bin")
                }

    try:

        status_var.set("Downloading...")
        window.update_idletasks()

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        status_var.set("Download Finished!")

        messagebox.showinfo(
            "Finished",
            "Download finished sussefuly"
        )
    except Exception as error:
        status_var.set("Download Error")

        messagebox.showerror(
            "Error",
            str(error)
        )
# Interface

window = tk.Tk()

window.title("Youtube Downloader")
window.geometry("800x650")
window.resizable(False, False)

# Title

tk.Label(
    window,
    text="YouTube Downloader",
    font=("Arial", 22, "bold")
).pack(pady=15)

# URL

frame_url = tk.Frame(window)
frame_url.pack(pady=10)

tk.Label(frame_url, text="URL:").pack(side="left")

urlGet = tk.Entry(frame_url, width=70)

urlGet.pack(side="left", padx=10)

tk.Button(frame_url, text="ANALYZE", command=analyze_video).pack(side="left")

# Info Area

frame_info = tk.Frame(window)

frame_info.pack(pady=20)

# Thumbnail

label_thumbnail = tk.Label(frame_info, text="Thumbnail", relief="solid")

label_thumbnail.pack(side="left", padx=20)

# Info

frame_data = tk.Frame(frame_info)
frame_data.pack(side="left", anchor="n")

tk.Label(frame_data, text="Title:",
    font=("Arial", 10, "bold")
).pack(anchor="w")

title_var = tk.StringVar()

tk.Label(
    frame_data,
    textvariable=title_var,
    wraplength=350,
    justify="left"
).pack(anchor="w", pady=(0, 15))

tk.Label(
    frame_data,
    text="Duration:",
    font=("Arial", 10, "bold")
).pack(anchor="w")

duration_var = tk.StringVar()

tk.Label(
    frame_data, 
    textvariable=duration_var
).pack(anchor="w")

# Formats

tk.Label(
    window,
    text="Choose Format:",
    font=("Arial", 11, "bold")
).pack(pady=(10, 5))

combo_formats = ttk.Combobox(
    window,
    width=65,
    state="readonly"
)

combo_formats.pack()

combo_formats.formats = []

# Button download

tk.Button(
    window,
    text="DOWNLOAD",
    command=download_video,
    width=20,
    height=2
).pack(pady=25)

# Status

status_var = tk.StringVar()
status_var.set("Ready.")

tk.Label(
    window,
    textvariable=status_var
).pack()

window.mainloop()

# print("\nDownload Concluído")
