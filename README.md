
# Speaker Diarization
## Team
An international research group from Nanyang Technical University Singapore, Hunan University China, BITS Pilani India headed by [Dr Eng-Siong Chng](https://scholar.google.com/citations?user=FJodrCcAAAAJ&hl=en), [Dr Xionghu Zhong](https://scholar.google.com/citations?user=V-ISRXwAAAAJ&hl=en) and [Dr Van Tung Pham](https://scholar.google.com/citations?user=8o42XvkAAAAJ&hl=en)

<p >
  <img src="logos/NTU.png" height=100 />
   <img src="logos/hunan.png" height=100 />
   <img src="logos/BITS.png" height=100 />
</p>

##  Problem Statement
Speaker Diarization is a process to answer the question of 'who spoke when?' in an audio file. It annotates timeframes in an audio according to the speaker of the frame.

<p>
  <img src='logos/spk-dzn.png'/>
 </p>
 
 A typical Speaker Diarization pipeline involves solving various subproblems, broadly: Identification of speech regions, Extracting features from speech frames, clustering them, and an optional resegmentation step to refine predictions. 
 
 <p>
  <img src='logos/pipeline.png'/>
 </p> 
 
 ## Install
1. Clone this project
```bash
git clone https://github.com/sehgal-simran/Speaker-Diarization.git
cd Speaker-Diarization
```

 ## Implemented Approaches
 To find a good baseline, we reviewed many recent works and found 2 common types Spk-Dzn of systems:
 1. <b><i>Kaldi-based</b></i>: These are systems built on top of the robust kaldi speaker diarization recipe involving x-vectors, by modifying one or more components in the pipeline. 
 
 2. <b><i>End-to-End/ Neural-based</b></i>: These are systems which combine many modules of the pipeline within a single (often neural network based) model. They have potential to be/already are end-to-end i.e input is audio and output is speaker labels.
 
 Thus, we decided to implement and review 3 approaches:
 1. a) Kaldi's original x-vector [recipe](https://github.com/kaldi-asr/kaldi/blob/master/egs/callhome_diarization/v2/run.sh)
 
 1. b) Kaldi's x-vector with an [LSTM similarity](https://github.com/sehgal-simran/Spk-Dzn/tree/main/LSTM) scoring module
 
 2. a) [Region Proposal Network](https://github.com/sehgal-simran/Spk-Dzn/tree/main/RPNSD) for Speaker Diarization.

## Results

The 3 systems are evaluated on the CALLHOME dataset with a collar of 0.25 secs using the standard md-eval.pl script for scoring. Kaldi's orginal recipe is tested after adapting PLDA model to CALLHOME using a 2-fold cross validation. The LSTM is trained entirely on CALLHOME and the system is tested using a 5-fold cross validation. The RPNSD model is trained on Mixer6, SRE and SWBD and adapted on CALLHOME using 5-fold cross validation.

| Pipeline | DER with overlap Speech | DER without overlap speech | Inference time (as % of total time to be diarized i.e audio length) | Testing Method
|---|---|---|---|---|
| Original Kaldi x-vector | 16.78% | 7.09% | 19%| PLDA is adapted and tested on Callhome using 2-fold cross validation|
| Kaldi x-vector with LSTM | 16.52% | 6.52%| 18%| LSTM model is trained entirely on Callhome and tested using 5-fold cross validation|
| RPNSD | 18.22% | 12.93% | 4%| RPNSD model is adapted and tested on Callhome using 5-fold cross validation|

