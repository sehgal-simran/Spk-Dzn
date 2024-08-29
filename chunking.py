import os
from pydub import AudioSegment

base_path='/Users/seagull/home/git/adalat/test_data'

for subdir in os.listdir(base_path):
    case_dir = os.path.join(base_path, subdir)
    if os.path.isdir(case_dir):
        print(f"Processing case directory: {subdir}")
        audio = AudioSegment.from_mp3(case_dir + "/audio.mp3")
        
        # Create chunks directory
        chunks_dir = os.path.join(case_dir, "chunks")
        os.makedirs(chunks_dir, exist_ok=True)
        
        # Split audio into 30-second chunks
        chunk_length_ms = 30 * 1000  # 30 seconds in milliseconds
        j=0
        for i, chunk in enumerate(audio[::chunk_length_ms]):
            # Check if the chunk is silent
            if chunk.dBFS > -60:  # Adjust this threshold as needed
                chunk_dir = os.path.join(chunks_dir, f"chunk_{j}")
                j+=1
                os.makedirs(chunk_dir, exist_ok=True)
                chunk_file = os.path.join(chunk_dir, "audio.mp3")
                chunk.export(chunk_file, format="mp3")
                print(f"Saved chunk {i} to {chunk_file}")
            else:
                print(f"Skipped silent chunk {i}")


