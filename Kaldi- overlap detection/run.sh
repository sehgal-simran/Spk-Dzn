#!/usr/bin/env bash

. ./cmd.sh
. ./path.sh
. ./variables.sh
set -e

stage=6

num_components=1024 # the number of UBM components (used for VB resegmentation)
ivector_dim=400 # the dimension of i-vector (used for VB resegmentation)

# Prepare datasets
if [ $stage -le 0 ]; then
  # Prepare the Callhome portion of NIST SRE 2000. Divides it into 2 folds.
  local/make_callhome.sh $data_root data/

  #If not callhome, need to prepare data files: fullrefrttm, reco2numspk, spk2utt, utt2spk,wav.scp
  #essentially, list of files and rttm, and will do.

fi

# Prepare features
if [ $stage -le 1 ]; then
  # The script local/make_callhome.sh splits callhome into two parts, called
  # callhome1 and callhome2.  Each partition is treated like a held-out
  # dataset, and used to estimate various quantities needed to perform
  # diarization on the other part (and vice versa).
  for name in callhome1 callhome2 callhome; do
    steps/make_mfcc.sh --mfcc-config conf/mfcc.conf --nj 40 \
      --cmd "$train_cmd" --write-utt2num-frames true \
      data/$name exp/make_mfcc $mfccdir
    utils/fix_data_dir.sh data/$name
  done

  for name in callhome1 callhome2; do
    sid/compute_vad_decision.sh --nj 40 --cmd "$train_cmd" \
      data/$name exp/make_vad $vaddir
    utils/fix_data_dir.sh data/$name
  done
fi


  # This writes features to disk after applying the sliding window CMN.
  # Although this is somewhat wasteful in terms of disk space, for diarization
  # it ends up being preferable to performing the CMN in memory.  If the CMN
  # were performed in memory (e.g., we used --apply-cmn true in
  # diarization/nnet3/xvector/extract_xvectors.sh) it would need to be
  # performed after the subsegmentation, which leads to poorer results.
if [ $stage -le 2 ]; then

  for name in callhome1 callhome2; do
    local/nnet3/xvector/prepare_feats.sh --nj 40 --cmd "$train_cmd" \
      data/$name data/${name}_cmn exp/${name}_cmn
    cp data/$name/vad.scp data/${name}_cmn/
    if [ -f data/$name/segments ]; then
      cp data/$name/segments data/${name}_cmn/
    fi
    utils/fix_data_dir.sh data/${name}_cmn
  done

fi


# Extract x-vectors
if [ $stage -le 3 ]; then
  # Extract x-vectors for the two partitions of callhome.
  diarization/nnet3/xvector/extract_xvectors.sh --cmd "$train_cmd --mem 5G" \
    --nj 40 --window 1.5 --period 0.75 --apply-cmn false \
    --min-segment 0.5 $nnet_dir \
    data/callhome1_cmn $nnet_dir/xvectors_callhome1

  diarization/nnet3/xvector/extract_xvectors.sh --cmd "$train_cmd --mem 5G" \
    --nj 40 --window 1.5 --period 0.75 --apply-cmn false \
    --min-segment 0.5 $nnet_dir \
    data/callhome2_cmn $nnet_dir/xvectors_callhome2

  
fi


# Perform PLDA scoring
if [ $stage -le 4 ]; then
  # Perform PLDA scoring on all pairs of segments for each recording.
  # The first directory contains the PLDA model that used callhome2
  # to perform whitening (recall that we're treating callhome2 as a
  # held-out dataset).  The second directory contains the x-vectors
  # for callhome1.
  diarization/nnet3/xvector/score_plda.sh --cmd "$train_cmd --mem 4G" \
    --nj 20 $nnet_dir/xvectors_callhome2 $nnet_dir/xvectors_callhome1 \
    $nnet_dir/xvectors_callhome1/plda_scores

  # Do the same thing for callhome2.
  diarization/nnet3/xvector/score_plda.sh --cmd "$train_cmd --mem 4G" \
    --nj 20 $nnet_dir/xvectors_callhome1 $nnet_dir/xvectors_callhome2 \
    $nnet_dir/xvectors_callhome2/plda_scores
fi

# Cluster the PLDA scores using a stopping threshold.


# Cluster the PLDA scores using the oracle number of speakers
if [ $stage -le 5 ]; then
  # In this section, we show how to do the clustering if the number of speakers
  # (and therefore, the number of clusters) per recording is known in advance.
  diarization/cluster.sh --cmd "$train_cmd --mem 4G" \
    --reco2num-spk data/callhome1/reco2num_spk \
    $nnet_dir/xvectors_callhome1/plda_scores $nnet_dir/xvectors_callhome1/plda_scores_num_spk

  diarization/cluster.sh --cmd "$train_cmd --mem 4G" \
    --reco2num-spk data/callhome2/reco2num_spk \
    $nnet_dir/xvectors_callhome2/plda_scores $nnet_dir/xvectors_callhome2/plda_scores_num_spk

  mkdir -p ./results
  # Now combine the results for callhome1 and callhome2 and evaluate it together.
  cat $nnet_dir/xvectors_callhome1/plda_scores_num_spk/rttm \
  $nnet_dir/xvectors_callhome2/plda_scores_num_spk/rttm \
    | md-eval.pl -1 -c 0.25 -r data/callhome/fullref.rttm -s - 2> ./results/num_spk.log \
    > ./results/DER_num_spk.txt
  
  cat $nnet_dir/xvectors_callhome1/plda_scores_num_spk/rttm \
  $nnet_dir/xvectors_callhome2/plda_scores_num_spk/rttm \
    > ./results/x_vector.rttm

  cat $nnet_dir/xvectors_callhome1/plda_scores_num_spk/rttm \
  $nnet_dir/xvectors_callhome2/plda_scores_num_spk/rttm \
    | md-eval.pl -c 0.25 -r data/callhome/fullref.rttm -s - 2> ./results/num_spk.log \
    > ./results/DER_num_spk_withoverlap.txt

  

  #der=$(grep -oP 'DIARIZATION\ ERROR\ =\ \K[0-9]+([.][0-9]+)?' \
  #  $nnet_dir/results/DER_num_spk.txt)

  # Using the oracle number of speakers, DER: 7.12%
  # Compare to 8.69% in ../v1/run.sh
  
  #echo "Using the oracle number of speakers, DER: $der%"
fi

# Variational Bayes resegmentation using the code from Brno University of Technology
# Please see https://speech.fit.vutbr.cz/software/vb-diarization-eigenvoice-and-hmm-priors 
# for details

if [ $stage -le 6 ]; then
  output_rttm_dir=exp/VB/rttm
  mkdir -p $output_rttm_dir || exit 1;
  cat $nnet_dir/xvectors_callhome1/plda_scores_num_spk/rttm \
    $nnet_dir/xvectors_callhome2/plda_scores_num_spk/rttm > $output_rttm_dir/x_vector_rttm
  init_rttm_file=$output_rttm_dir/x_vector_rttm

  # VB resegmentation. In this script, I use the x-vector result to 
  # initialize the VB system. You can also use i-vector result or random 
  # initize the VB system. The following script uses kaldi_io. 
  # You could use `sh ../../../tools/extras/install_kaldi_io.sh` to install it
  diarization/VB_resegmentation.sh --nj 20 --cmd "$train_cmd --mem 10G" \
    --initialize 1 data/callhome $init_rttm_file exp/VB \
    exp/diag_ubm_$num_components/final.dubm exp/extractor_diag_c${num_components}_i${ivector_dim}/final.ie || exit 1; 

  # Compute the DER after VB resegmentation
  md-eval.pl -1 -c 0.25 -r data/callhome/fullref.rttm -s $output_rttm_dir/VB_rttm 2> exp/VB/log/VB_DER.log \
    > ./results/VB_DER.txt

  der=$(grep -oP 'DIARIZATION\ ERROR\ =\ \K[0-9]+([.][0-9]+)?' \
    exp/VB/results/VB_DER.txt)
  # After VB resegmentation, DER: 6.48%
  echo "After VB resegmentation, DER: $der%"
fi

if [ $stage -le 7 ]; then
calc_rttm=exp/VB/rttm/VB_rttm
overlap_file=./oracle_overlap.rttm
output_dir=./results
python3 overlap.py $calc_rttm $overlap_file $output_dir

md-eval.pl -1 -c 0.25 -r data/callhome/fullref.rttm -s results/overlap_processing.rttm - 2> ./results/DER_with_overlap_processing.txt

der=$(grep -oP 'DIARIZATION\ ERROR\ =\ \K[0-9]+([.][0-9]+)?' \
    exp/VB/results/VB_DER.txt)
  # After VB resegmentation, DER: 6.48%
echo "After VB resegmentation, DER: $der%"

fi

