#!/bin/bash

# Single File Diarization

nj=1
stage=0
thres=0.5      #Threshold to make decisions
nms_thres=0.3  #NMS Threshold
cluster_type=kmeans   #
modelname=modelbest
cluster_threshold=0.7   #Threshold for clustering
cfg_file=cfgs/res101.yml
batch_size=1
num_workers=4
seed=7
arch=res101
nclass=1284
gpu=0

. ../parse_options.sh || exit 1;

test_dir=$1   #location of rttm, spk2utt,utt2spk,wavscp files
model_dir=$2  #path+name of pretrained model
output_dir=$3
hdf5=$4

nj_pres=$nj

echo "Cluster type chosen is: $cluster_type"
if [ $nj -le 1 ];then
  if [ $stage -le 0 ]; then
      python3 ../scripts/evaluate.py $test_dir $model_dir $hdf5 \
	    --cfg_file $cfg_file --output_dir $output_dir --batch_size $batch_size --num_workers $num_workers \
	    --seed $seed --arch $arch \
	    --nclass $nclass --use_gpu $gpu || exit 1;
  fi


  if [ $stage -le 1 ]; then
    python3 ../scripts/cluster_nms.py $output_dir/detections.pkl $output_dir/rttm_num_spk \
            --num_cluster $test_dir/reco2num_spk --nms_thres $nms_thres --thres $thres --cluster_type $cluster_type  || exit 1;
  fi

  if [ $stage -le 2 ]; then
  result_dir_all=$output_dir/results
  mkdir -p $result_dir_all || exit 1;
  
  for overlap in "true" "false"; do

    for collar in 0 0.1 0.25; do
      if $overlap; then
        scoreopt="-c $collar"
      else
        scoreopt="-1 -c $collar"
      fi
      ../md-eval.pl $scoreopt -r $test_dir/rttm \
              -s $output_dir/rttm_num_spk 2> $result_dir_all/collar${collar}_overlap${overlap}.log \
              > $result_dir_all/collar${collar}_overlap${overlap}_DER.txt
      der=$(grep -oP 'DIARIZATION\ ERROR\ =\ \K[0-9]+([.][0-9]+)?' \
        $result_dir_all/collar${collar}_overlap${overlap}_DER.txt)
      echo "Oracle Collar $collar Overlap $overlap $test_dir DER: $der%"
    done
  done
  fi
fi
