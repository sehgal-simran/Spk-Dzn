
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
 
 ## Implemented Approaches
 To find a good baseline, we reviewed many recent works and found 2 common types Spk-Dzn of systems:
 1. Kaldi-based: These are systems built on top of the robust kaldi speaker diarization recipe involving x-vectors, by modifying one or more components in the pipeline. 
 
 2. End-to-End/ Neural-based: These are systems which combine many modules of the pipeline within a single (often neural network based) model. They have potential to be/already are end-to-end i.e input is audio and output is speaker labels.
 
 Thus, we decided to implement and review 3 approaches: Kaldi's original x-vector recipe, Kaldi's x-vector with an LSTM similarity scoring module and the Region Proposal Network for Speaker Diarization.

## Install
1. Clone this project
```bash
git clone https://github.com/sehgal-simran/Speaker-Diarization.git
cd Speaker-Diarization
```

