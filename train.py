from transformers import WhisperProcessor, WhisperForConditionalGeneration, WhisperFeatureExtractor, WhisperTokenizer
import os
import soundfile as sf
import librosa
import numpy as np
import torch

from dataclasses import dataclass
from typing import Any, Dict, List, Union
import evaluate
from transformers import Seq2SeqTrainingArguments
from transformers import Seq2SeqTrainer



training_args = Seq2SeqTrainingArguments(
    output_dir="./whisper-small-hi-quick2",
    per_device_train_batch_size=1,  # Reduced to 1 since we only have one sample
    gradient_accumulation_steps=1,
    learning_rate=5e-5,  # Slightly increased for faster convergence
    warmup_steps=0,  # Removed warmup since we have very few steps
    max_steps=10,  # Drastically reduced number of steps
    gradient_checkpointing=False,  # Disabled to speed up training
    fp16=False,
    evaluation_strategy="steps",
    per_device_eval_batch_size=1,
    predict_with_generate=True,
    generation_max_length=225,
    save_steps=5,  # Save more frequently
    eval_steps=5,  # Evaluate more frequently
    logging_steps=1,  # Log every step
    report_to=["tensorboard"],
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    push_to_hub=False,
)


metric = evaluate.load("wer")

def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids

    # replace -100 with the pad_token_id
    label_ids[label_ids == -100] = tokenizer.pad_token_id

    # we do not want to group tokens when computing the metrics
    pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    wer = 100 * metric.compute(predictions=pred_str, references=label_str)

    return {"wer": wer}


@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any
    decoder_start_token_id: int

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lengths and need different padding methods
        # first treat the audio inputs by simply returning torch tensors
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        # get the tokenized label sequences
        label_features = [{"input_ids": feature["labels"]} for feature in features]
        # pad the labels to max length
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        # if bos token is appended in previous tokenization step,
        # cut bos token here as it's append later anyways
        if (labels[:, 0] == self.decoder_start_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels

        return batch


feature_extractor = WhisperFeatureExtractor.from_pretrained("openai/whisper-small")
tokenizer = WhisperTokenizer.from_pretrained("openai/whisper-medium", language="english", task="transcribe")
# Initialize the Whisper model and processor
processor = WhisperProcessor.from_pretrained("openai/whisper-medium.en")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-medium.en")


chunk_path = "/Users/seagull/home/git/adalat/output_chunks/input/chunk_2.wav"

audio_sample, sample_rate = sf.read(chunk_path)
print("before sampling len: values:", len(audio_sample), audio_sample)

# print("sample rate", sample_rate)
# Resample to 16000 Hz if necessary
if sample_rate != 16000:
    audio_sample, sample_rate = librosa.load(chunk_path, sr=16000)

# Process the audio sample
input_features = processor(audio_sample, sampling_rate=16000, return_tensors="pt").input_features

# Generate token ids
predicted_ids = model.generate(input_features)

# Decode token ids to text
transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

print(f"Transcription:")
print(transcription[0])

# data_sample = {
#     'sentence': transcription[0],
#     'audio': {
#         'path': chunk_path,
#         'array':audio_sample,
#         'sampling_rate': 16000,
#         'input_features': input_features,
#         'labels': tokenizer(transcription[0]).input_ids
#     }
# }

data_sample = {
    'input_features': input_features.squeeze(0),  # Remove batch dimension
    'labels': tokenizer(transcription[0]).input_ids
}

# Create a custom dataset class
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

# Create the dataset
dataset = CustomDataset([data_sample])
print(data_sample)

model.generation_config.language = "english"
model.generation_config.task = "transcribe"

model.generation_config.forced_decoder_ids = None

data_collator = DataCollatorSpeechSeq2SeqWithPadding(
    processor=processor,
    decoder_start_token_id=model.config.decoder_start_token_id,
)

trainer = Seq2SeqTrainer(
    args=training_args,
    model=model,
    train_dataset=dataset,
    eval_dataset=dataset,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    tokenizer=processor.feature_extractor,
)

trainer.train()