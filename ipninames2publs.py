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
    # 1. Read data file
    ###########################################################################
    df = pd.read_csv(args.inputfile, sep=args.delimiter, nrows=args.limit)
    df = df.replace({np.nan:None})
    print('Read {} of {} IPNI name rows'.format(args.inputfile, len(df)))
    
    ###########################################################################
    # 2. Filter columnwise
    ###########################################################################
    cols = [col for col in df.columns if col.startswith('linkedPublication')]
    df_publ = df[cols].drop_duplicates()

    ###########################################################################
    # 3. Add ISSNs
    ###########################################################################

    unpaywall_cols = ['linkedPublication.id','journal_issns']
    unpaywall_mask = (df.journal_issns.notnull())

    df_issn = pd.DataFrame(df[unpaywall_mask][unpaywall_cols])
    df_issn['journal_issns'] = df_issn['journal_issns'].apply(lambda x: x.split(','))
    df_issn = df_issn.explode('journal_issns')
    df_issn.drop_duplicates(inplace=True)

    df_issn = df_issn.sort_values(by=['linkedPublication.id','journal_issns']).groupby('linkedPublication.id').agg({'journal_issns':lambda x: ','.join(x)})

    df_publ = pd.merge(left=df_publ,
                right=df_issn,
                left_on='linkedPublication.id',
                right_on='linkedPublication.id',
                how='left')

    ###########################################################################
    # 3. Save data to outputfile
    ###########################################################################
    print('Writing {} rows publication data to {}'.format(len(df_publ), args.outputfile))
    df_publ.drop_duplicates().to_csv(args.outputfile, sep='\t', index=False)


if __name__ == "__main__":
    main()
