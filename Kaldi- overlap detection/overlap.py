#!/usr/bin/env python3
import heapq
import numpy as np
import argparse

def main():
    parser = argparse.ArgumentParser(description='Overlap Wrapper')
    parser.add_argument('calc_rttm', type=str, help='The rttm output file after VB resegmentation')
    parser.add_argument('overlap_rttm', type=str, 
                        help='File that has segments of overlap')
    parser.add_argument('output_dir', type=str, help='Output directory of rttm')
    

    args = parser.parse_args()
    ref=open(args.calc_rttm, 'r')
    f=ref.readlines()

    ov=open(args.overlap_rttm, 'r')
    l=ov.readlines()

    new_segs=[]
    for line in l:
        key=line.split()[0]
        st=float(line.split()[1])
        en=float(line.split()[2])
        count=0
        scores=np.zeros(len(f))
        i=0
        for spks in f:
            speaker=spks.split()[7]
            if(speaker!=key):
                continue
            first=float(spks.split()[3])
            sec=float(spks.split()[4])+first
            scores[i]+= (first-st)+ (sec-en)
            i+=1
        x=heapq.nsmallest(2, range(len(scores)), scores.take)
        try:
            new_segs.append('SPEAKER '+ line.split()[0]+' 0 '+ str(st)+' '+ "{:.2f}".format(en-st)+ ' <NA> <NA> '+ f[x[0]].split()[7]+' <NA> <NA> \n' )
            new_segs.append('SPEAKER '+ line.split()[0]+' 0 '+ str(st)+' '+ "{:.2f}".format(en-st)+ ' <NA> <NA> '+ f[x[1]].split()[7]+' <NA> <NA> \n' )
        except:
            continue
    newrttm= f+new_segs
    filee=args.output_dir+'/overlap_processing.rttm'
    x=open(filee,'w')
    x.writelines(newrttm)

    return 0

if __name__ == "__main__":
    main()
