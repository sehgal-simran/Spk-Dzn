import csv
import requests
import os
from urllib.parse import urlparse, parse_qs

from pytube import YouTube
import os
import yt_dlp

def download_youtube_audio(youtube_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            filename = ydl.prepare_filename(info)
            mp3_filename = filename.rsplit('.', 1)[0] + '.mp3'
        
        print(f"Audio downloaded successfully: {mp3_filename}")
        return mp3_filename
    except Exception as e:
        print(f"An error occurred while downloading {youtube_url}: {str(e)}")
        return None


def download_file(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded transcript: {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading transcript: {e}")
    
base_path="/Users/seagull/home/git/adalat/test_data"
def process_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            number=row.get('Sr. No.')
            dropbox_link = row.get('Oral Hearing Link')       
            transcript = row.get('Transcript Link')
            identifier= "case_"+number
            if dropbox_link:
                filename =  os.path.join(base_path, identifier,"audio.mp3")
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                download_youtube_audio(dropbox_link, filename)
                print(f"Downloaded: {filename}")
            
            if transcript:
                pdf_filename = os.path.join(base_path, identifier, "transcript.pdf")
                os.makedirs(os.path.dirname(pdf_filename), exist_ok=True)
                download_file(transcript, pdf_filename)
                print(f"Downloaded transcript: {pdf_filename}")
                # Process the PDF transcript here
                # For example, you could save it to a file or analyze its content
                print(f"Transcript: {transcript}")

if __name__ == "__main__":
    csv_file = "raw_data.csv"  # Replace with your CSV file name
    process_csv(csv_file)