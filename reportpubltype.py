import argparse

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('outputfile')

    args = parser.parse_args()

    ###########################################################################
    # 1. Read data files
    ###########################################################################
    df = pd.read_csv(args.inputfile, sep=args.delimiter, nrows=args.limit, usecols=['id','publicationYear','publ_type'])
    df = df.replace({np.nan:None})
    print('Read {} of {} IPNI name rows'.format(args.inputfile, len(df)))

    ###########################################################################
    # 2. Preparation
    ###########################################################################
    # 2.1 Convert year to int
    df.publicationYear = df.publicationYear.astype(int)

    # 2.2 Column renames - more generic name for year
    column_renames = {'publicationYear':'year'}
    df.rename(columns=column_renames, inplace=True)

    # 2.3 Group
    dfg = df.groupby(['year','publ_type']).size().to_frame('n')
    print('Summarised {} IPNI name rows'.format(dfg.n.sum()))

    ###########################################################################
    # 3. Save data to outputfile
    ###########################################################################
    print('Writing {} rows grouped data to {}'.format(len(dfg), args.outputfile))
    dfg.to_csv(args.outputfile, sep='\t')#, index=False)

if __name__ == "__main__":
    main()
