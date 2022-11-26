import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
import pandas as pd
pd.set_option('display.max_rows',100)
import argparse
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", default=None, type=int)
    parser.add_argument("--email_address", default='n.nicolson@kew.org', type=str)
    parser.add_argument("inputfile", type=str)
    parser.add_argument("outputfile", type=str)
    args = parser.parse_args()

    ###########################################################################
    # 1. Read data file
    ###########################################################################
    df = pd.read_csv(args.inputfile, nrows=args.limit, sep='\t')
    df = df.replace({np.nan:None})
    print('Read {} of {} IPNI name rows'.format(args.inputfile, len(df)))

    ###########################################################################
    # 2. Do unpaywall lookup using DOI
    ###########################################################################
    mask = df.doi.notnull()
    df.loc[mask,'doi'] = df[mask].doi.apply(lambda x: x.lower())
    UnpywallCredentials(args.email_address)
    df_doi = Unpywall.doi(dois=df[mask].doi.unique().tolist(), errors='warn', progress=True)
    df_doi.doi = df_doi.doi.apply(lambda x: x.lower())
    df = pd.merge(left=df, right=df_doi, left_on='doi', right_on='doi', how='left', suffixes=['','_unpaywall'])
    print(df[df.doi.notnull()].sample(n=1).T)

    ###########################################################################
    # 3. Write output file
    ###########################################################################
    print('Writing {} IPNI name OA status rows to {} '.format(len(df), args.inputfile))
    df.to_csv(args.outputfile, sep='\t', index=False)
    
if __name__ == '__main__':
    main()