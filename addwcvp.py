import argparse
import pandas as pd
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile_ipni')
    parser.add_argument('inputfile_wcvp_name')
    parser.add_argument('inputfile_wcvp_dist')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--delimiter_ipni', type=str, default='\t')
    parser.add_argument('--delimiter_wcvp', type=str, default='|')
    parser.add_argument('outputfile')

    args = parser.parse_args()

    # 1. Read input files
    # 1.1 IPNI name
    df = pd.read_csv(args.inputfile_ipni, sep=args.delimiter_ipni, usecols=['id','citationType','is_oa','oa_status'])
    print('Read {} IPNI name rows from {}'.format(len(df), args.inputfile_ipni))
    df = df.replace({np.nan:None})
    # 1.2 WCVP name 
    df_wn = pd.read_csv(args.inputfile_wcvp_name, sep=args.delimiter_wcvp, usecols=['plant_name_id','ipni_id','taxon_rank','taxon_status','accepted_plant_name_id'])
    print('Read {} WCVP name rows from {}'.format(len(df_wn), args.inputfile_wcvp_name))
    df_wn = df_wn.replace({np.nan:None})
    # 1.3 WCVP dist 
    df_wd = pd.read_csv(args.inputfile_wcvp_dist, sep=args.delimiter_wcvp)
    print('Read {} WCVP dist rows from {}'.format(len(df_wd), args.inputfile_wcvp_dist))
    df_wd = df_wd.replace({np.nan:None})

    # 2. Link data
    # 2.1 IPNI names to WCVP names
    df = pd.merge(left=df,right=df_wn, left_on='id', right_on='ipni_id',how='left',suffixes=['','_wcvp'])
    print('Merged IPNI names with WCVP names to make data structure of {} rows'.format(len(df)))
    # 2.2 IPNI names to WCVP dists
    mask = (df_wd.introduced == 0) & (df_wd.extinct == 0) & (df_wd.location_doubtful == 0)
    df = pd.merge(left=df,right=df_wd[mask], left_on='accepted_plant_name_id', right_on='plant_name_id',how='left',suffixes=['','_wcvpd'])
    print('Merged IPNI names with WCVP dists to make data structure of {} rows'.format(len(df)))

    # 3. Write output file
    print('Writing {} IPNI name rows to {}'.format(len(df), args.outputfile))
    df.to_csv(args.outputfile, sep=args.delimiter_ipni, encoding='utf8', index=False)


if __name__ == "__main__":
    main()
