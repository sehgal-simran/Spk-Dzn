# :speech_balloon: Region Proposal Network based Speaker Diarization [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1SDpunV2TwneTUY017OFcScL6uAnHrpaA?usp=sharing)
This repository is an extended version of the [RPNSD](https://github.com/HuangZiliAndy/RPNSD) repository by [Zili Huang](https://github.com/HuangZiliAndy) and [Yusuke Fujita](https://github.com/yubouf). This version includes adapted pretrained models on the CALLHOME dataset and aims to verify the results reported in the paper [Speaker Diarization with Region Proposal Network](https://arxiv.org/pdf/2002.06220.pdf)

## :computer: Install 

```bash


1. Environment Preparation: Install PyTorch (0.4.0) and torchvision according to your CUDA version
```
conda install pytorch==0.4.0 cuda91 torchvision pillow"<7" -c pytorch
```
2. Install the packages in requirements.txt
```bash
pip install -r requirements.txt
```

## :open_file_folder: Test Data Preparation 
 Due to RAM constraints faced on processing a batch of audio files, the callhome dataset is stored as a [test_data.hdf5](https://drive.google.com/file/d/1HNVEi3mWFdpOt7y0oEuLyfBiigtR_ww_/view?usp=sharing) file which allows easier and faster reading and writing from memory and is made compatible with the original code by tweaking [scripts/diarization_dataset.py](https://github.com/sehgal-simran/Speaker-Diarization/blob/main/RPNSD/scripts/diarization_dataset.py)



## :checkered_flag: Adapted Models 	
The callhome dataset is split into 5 folds and the pretrained model provided by [Zili Huang and team](https://drive.google.com/file/d/1EYhTADveeeMlu2J3AqzkITcKXZhbNmUa/view?usp=sharing) is adapted and tested on these folds by performing 5-fold cross validation.

The adapted models are present in [experiment](https://github.com/sehgal-simran/Speaker-Diarization/tree/main/RPNSD/experiment) and also available to download from [here](https://drive.google.com/file/d/1_qGZ42zSgcrgBCm12gJz6IJyt5O0EUQq/view?usp=sharing)

## :runner: Inference 
Inference stage. 
1. Forward the network to get speech region proposals, speaker embedding and background probability.
2. Post-processing with clustering and NMS.
3. Compute Diarization Error Rate (DER).

```bash
./inference.sh
```

## :ledger: Results 
The reported results are on the CALLHOME dataset.

| Overlap Speech| Repository DER | Paper DER |
| :-:| :-:|:-:|
| 	      :x: | 12.93% | 11.81 %|
|       :white_check_mark: |18.22% | 17.06% |

*The results are reported with a collar of 0.25s. For more results, click [here](https://github.com/sehgal-simran/Speaker-Diarization/tree/main/RPNSD/experiment/results)*




## :high_brightness: Citation 

    @inproceedings{huang2020speaker,
        Title={Speaker Diarization with Region Proposal Network},
        Author={Huang, Zili and Watanabe, Shinji and Fujita, Yusuke and Garcia, Paola and Shao, Yiwen and Povey, Daniel and Khudanpur, Sanjeev},
        Booktitle={Accepted to ICASSP 2020},
        Year={2020}
    }
    
    @article{jjfaster2rcnn,
        Author = {Jianwei Yang and Jiasen Lu and Dhruv Batra and Devi Parikh},
        Title = {A Faster Pytorch Implementation of Faster R-CNN},
        Journal = {https://github.com/jwyang/faster-rcnn.pytorch},
        Year = {2017}
    } 
