from transformers import WhisperProcessor, WhisperForConditionalGeneration, WhisperFeatureExtractor, WhisperTokenizer
import os
import soundfile as sf
import librosa
import numpy as np
import torch

import Levenshtein
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from fuzzywuzzy import fuzz
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def find_fuzzy_subsequence(query, target_document, threshold=80):
    # Normalize the query and target document
    query = re.sub(r'\s+', ' ', query.lower())
    target_document = re.sub(r'\s+', ' ', target_document.lower())
    
    # Split the query into words
    query_words = query.split()
    
    # Find the best matching subsequence
    best_match = ""
    best_ratio = 0
    window_size = len(query_words)
    
    for i in range(len(target_document.split()) - window_size + 1):
        subsequence = ' '.join(target_document.split()[i:i+window_size])
        ratio = fuzz.ratio(query, subsequence)
        
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = subsequence
    
    if best_ratio >= threshold:
        return best_match, best_ratio
    else:
        return None, best_ratio


def process_chunk(chunk_subdir, chunks_dir, golden_transcript):
    output_file = os.path.join(chunks_dir, chunk_subdir, "output.txt")
    if os.path.exists(output_file):
        return

    chunk_path = os.path.join(chunks_dir, chunk_subdir, "audio.mp3")

    audio_sample, sample_rate = sf.read(chunk_path)
    print("before sampling len: values:", len(audio_sample), audio_sample)

    if sample_rate != 16000:
        audio_sample, sample_rate = librosa.load(chunk_path, sr=16000)

    input_features = processor(audio_sample, sampling_rate=16000, return_tensors="pt").input_features

    predicted_ids = model.generate(input_features)

    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    print("transcription", transcription)
    most_similar_sentence, distance = find_fuzzy_subsequence(transcription[0], golden_transcript)

    output_file = os.path.join(chunks_dir, chunk_subdir, "output.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        if most_similar_sentence:
            f.write(most_similar_sentence)
        else:
            f.write("No similar sentence found")
    print(f"Wrote most similar sentence to {output_file}")

tokenizer = WhisperTokenizer.from_pretrained("openai/whisper-medium", language="English", task="transcribe")
processor = WhisperProcessor.from_pretrained("openai/whisper-medium.en")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-medium.en")

base_path="/Users/seagull/home/git/adalat/test_data"

if __name__ == '__main__':

    # Iterate over all subdirectories in test_data
    for subdir in os.listdir(base_path):
        subdir_path = os.path.join(base_path, subdir)
        if os.path.isdir(subdir_path):
            chunks_dir = os.path.join(subdir_path, "chunks")
            golden_transcript_path = os.path.join(subdir_path, "extracted_transcript.txt")
            # if re.match(r'case_\d+$', os.path.basename(subdir_path)):
            #    
            # else:
            #     continue  # Skip this subdirectory if it doesn't match the pattern
            print("golden_transcript_path", golden_transcript_path)
            golden_transcript = read_file(golden_transcript_path)
            if os.path.exists(chunks_dir):
                # Get the number of CPU cores
                num_cores = multiprocessing.cpu_count()
                print("num_cores", num_cores)
                # Create a ProcessPoolExecutor
                with ProcessPoolExecutor(max_workers=num_cores) as executor:
                    # Submit tasks for each chunk
                    futures = [executor.submit(process_chunk, chunk_subdir, chunks_dir, golden_transcript) 
                               for chunk_subdir in os.listdir(chunks_dir)]
                    
                    # Wait for all tasks to complete
                    for future in as_completed(futures):
                        future.result()  