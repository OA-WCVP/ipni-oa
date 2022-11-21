import argparse

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile')
    parser.add_argument('-g','--groupby', type=str, default='publicationYear')
    parser.add_argument('--yearmin', type=int, default=2012)
    parser.add_argument('--yearmax', type=int, default=2021)
    parser.add_argument('--filtergroupvalues', type=str)
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('outputfile')

    args = parser.parse_args()

    ###########################################################################
    # 1. Read data files
    ###########################################################################
    cols = ['id','doi',args.groupby,'is_oa','oa_status']
    if args.groupby != 'publicationYear':
        cols.append('publicationYear')
    df = pd.read_csv(args.inputfile, sep=args.delimiter, nrows=args.limit, usecols=cols)
    df = df.replace({np.nan:None})
    print('Read {} of {} IPNI name rows'.format(args.inputfile, len(df)))
    # Filter by year
    df.drop(df[df['publicationYear'].astype(int).between(args.yearmin, args.yearmax)==False].index,inplace=True)

    ###########################################################################
    # 2. Preparation
    ###########################################################################
    # 2.1  Add has_doi flag
    df['has_doi']=df.doi.notnull()
    
    # 2.2 Add placeholder for NULL values in is_oa and oa_status fields
    df.is_oa.fillna('n/a',inplace=True)
    df.oa_status.fillna('n/a',inplace=True)

    # 2.3 Convert year to int
    if args.groupby == 'publicationYear':
        df[args.groupby] = df[args.groupby].astype(int)

    # 2.4 Apply filter
    if args.filtergroupvalues is not None:
        mask = (df[args.groupby].isin(args.filtergroupvalues.split(',')))
        df = df[mask]
    # column_renames = {'publicationYear':'year'}
    # df.rename(columns=column_renames, inplace=True)

    # 2.5 Group
    dfg = df.groupby([args.groupby,'has_doi','is_oa','oa_status']).size().to_frame('n')
    print('Summarised {} IPNI name rows'.format(dfg.n.sum()))

    ###########################################################################
    # 3. Save data to outputfile
    ###########################################################################
    print('Writing {} rows grouped data to {}'.format(len(dfg), args.outputfile))
    dfg.to_csv(args.outputfile, sep='\t')#, index=False)

if __name__ == "__main__":
    main()
