import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
import pandas as pd
pd.set_option('display.max_rows',100)
import argparse
import numpy as np
import requests 

def getDoajMetadata(issn):
    data = []
    url = 'https://doaj.org/api/search/journals/issn:{issn}'.format(issn=issn)
    try:
        r = requests.get(url)    
        data.extend(r.json()['results'])
    except:
        pass
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", default=None, type=int)
    parser.add_argument("inputfile", type=str)
    parser.add_argument("outputfile", type=str)
    args = parser.parse_args()

    ###########################################################################
    # 1. Read data file
    ###########################################################################
    df = pd.read_csv(args.inputfile, usecols=['journal_name','journal_is_in_doaj','journal_issns'], nrows=args.limit, sep='\t')
    df = df.replace({np.nan:None})
    print('Read {} of {} IPNI name OA status rows'.format(args.inputfile, len(df)))
    df.drop(df[df.journal_is_in_doaj.isnull()].index,inplace=True)
    print('Retained {} unpaywall journal records'.format(len(df)))
    df.drop_duplicates(inplace=True)
    print('Retained {} unique journal records'.format(len(df)))
    
    ###########################################################################
    # 2. Convert ISSN field value to list and explode
    ###########################################################################
    #
    # 2.1 Split multivalues in journal_issns
    mask = df.journal_issns.notnull()
    df.loc[mask,'journal_issns'] = df[mask].journal_issns.apply(lambda x: x.split(','))
    #
    # 2.2 Explode
    df = df.explode('journal_issns')
    print('Exploded to {} unique journal ISSN records'.format(len(df)))

    ###########################################################################
    # 3. Look up DOAJ using ISSN
    ###########################################################################
    mask = df.journal_is_in_doaj
    doaj_metadata = []
    for issn in df[mask].journal_issns:
        doaj_metadata.extend(getDoajMetadata(issn))
    df_doaj = pd.json_normalize(doaj_metadata)

    ###########################################################################
    # 4. Write output file
    ###########################################################################
    print('Writing {} DOAJ journal metadata records to {} '.format(len(df_doaj), args.outputfile))
    df_doaj.to_csv(args.outputfile, sep='\t', index=False)
    
if __name__ == '__main__':
    main()