import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
import pandas as pd
pd.set_option('display.max_rows',100)
import argparse
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", default=None, type=int)
    parser.add_argument("inputfile", type=str)
    parser.add_argument("outputfile", type=str)
    args = parser.parse_args()

    ###########################################################################
    # 1. Read data file
    ###########################################################################
    #
    # 1.1 Read file
    df = pd.read_csv(args.inputfile, usecols=['doi','oa_status','best_oa_location.repository_institution'], nrows=args.limit, sep='\t')
    df = df.replace({np.nan:None})
    #
    # 1.2 Select only those records with green OA status
    mask = df.oa_status.isin(['green'])
    df.drop(df[~mask].index,inplace=True)
    print('Retained {} OA status=green records'.format(len(df)))
    # 
    # 1.3 Drop duplicates
    df.drop_duplicates(inplace=True)
    print('Retained {} unique DOI / repository records'.format(len(df)))
        
    ###########################################################################
    # 2. Reshape to calculate number of DOIs per repository
    ###########################################################################
    
    dfg = df.groupby('best_oa_location.repository_institution').agg({'doi':'nunique'}).sort_values(by='doi',ascending=False)

    ###########################################################################
    # 3. Output
    ###########################################################################
    print('Writing {} repository usage records to {} '.format(len(dfg), args.outputfile))
    dfg.reset_index().to_csv(args.outputfile, sep='\t', index=False)
    
if __name__ == '__main__':
    main()