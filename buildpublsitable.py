import argparse

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile_publ_report')
    parser.add_argument('inputfile_publ_data')
    parser.add_argument('inputfile_doaj')
    parser.add_argument('--yearmin', type=int, default=2012)
    parser.add_argument('--yearmax', type=int, default=2021)
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('outputfile')

    args = parser.parse_args()

    ###########################################################################
    # 1. Read data files
    ###########################################################################
    
    # 1.1 Publications report
    df_publ = pd.read_csv(args.inputfile_publ_report, sep=args.delimiter, nrows=args.limit)
    df_publ = df_publ.replace({np.nan:None})

    # 1.2 IPNI publications
    df_ipni_publ = pd.read_csv(args.inputfile_publ_data, sep=args.delimiter, nrows=args.limit)
    df_ipni_publ = df_ipni_publ.replace({np.nan:None})

    # 1.3 Publications with DOAJ data
    df_doaj = pd.read_csv(args.inputfile_doaj, sep=args.delimiter, nrows=args.limit)
    df_doaj = df_doaj.replace({np.nan:None})

    ###########################################################################
    # 2. Merge data
    ###########################################################################

    df = pd.merge(left=df_publ.set_index('publication'), right=df_ipni_publ.set_index('linkedPublication.abbreviation'), left_index=True,right_index=True,how='left')

    # Add doaj data
    df = pd.merge(left=df.set_index('linkedPublication.id'), right=df_doaj.set_index('linkedPublication.id'), left_index=True,right_index=True,how='left')

    ###########################################################################
    # 3. Save data to outputfile
    ###########################################################################
    print('Writing {} rows publication SI data to {}'.format(len(df), args.outputfile))
    df.to_csv(args.outputfile, sep='\t')#, index=False)

if __name__ == "__main__":
    main()
