# :speech_balloon: RPNSD for single file 
This repository modifies [RPNSD](https://github.com/HuangZiliAndy/RPNSD) repository by [Zili Huang](https://github.com/HuangZiliAndy) and [Yusuke Fujita](https://github.com/yubouf) to work for a single audio file. In this repo, we will take the example of a callhome file iaaa.

## :computer: Install 

1. Environment Preparation: Install PyTorch (0.4.0) and torchvision according to your CUDA version
```bash
conda install pytorch==0.4.0 cuda91 torchvision pillow"<7" -c pytorch
```
2. Install the packages in requirements.txt
```bash
pip install -r requirements.txt
```

## :open_file_folder: Data Preparation 
 Kaldi style data prep will be required for the audio file you want to diarize. Data files of iaaa are stored in iaaa_test.

## :checkered_flag: Adapted Models 	
The adapted models are present in [../RPNSD/experiment](https://github.com/sehgal-simran/Speaker-Diarization/tree/main/RPNSD/experiment) and also available to download from [here](https://drive.google.com/file/d/1_qGZ42zSgcrgBCm12gJz6IJyt5O0EUQq/view?usp=sharing)

## :runner: Diarization
1. Forward the network to get speech region proposals, speaker embedding and background probability.
2. Post-processing with clustering and NMS.
3. Result is rttm file!

```bash
./diarization.sh
```



