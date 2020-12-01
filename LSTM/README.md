## LSTM
This repository is based on the paper [LSTM based Similarity Measurement with Spectral Clustering for Speaker Diarization](https://arxiv.org/abs/1907.10393) and is adapted from [this repo](https://github.com/cvqluu/nn-similarity-diarization)

## Requirements
Kaldi, python, kaldi_io, scipy, sklearn, torch (tested on torch ver. 1.3.0), CALLHOME dataset


## Usage
In `run.sh`, please change `xvector_dir`, `KALDI_PATH`, `folds_path`, `nnet_dir`, `callhome_path` to corresponding paths.

## Results
For CALLHOME dataset
| Similarity Scoring Method                   | DER  | DER (overlap)
| ------------------------------------------- |--------------:| --------|
| x-vector + PLDA + AHC                 | 9.46%         | 20.14%
| x-vector + PLDA + AHC + VB             | 7.33%        |18.61%|
| x-vector + LSTM + SC [paper]                    | 7.73% | NA|
| x-vector + LSTM + SC [this repo]            | 9.04%        |18.55%|
| x-vector + LSTM + SC + VB [this repo]       | 6.52%        | 16.52%|
