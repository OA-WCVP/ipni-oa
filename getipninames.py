import argparse
from datetime import datetime

import pandas as pd
import pykew.ipni as ipni
from ipniutil import nameutil, publutil
from pykew.ipni_terms import Filters, Name

def getPublType(id, issn, bphNumber):
    publ = ipni.lookup_publication(id)
    publtype = None
    if publutil.isBook(publ):
        publtype = 'book'
    elif (issn is not None or bphNumber is not None):
        publtype = 'serial'
    return publtype

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile_dois')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('--year_min', type=int, default=1997)
    parser.add_argument('--year_max', type=int, default=None)
    parser.add_argument('outputfile')

    args = parser.parse_args()

    year_min = args.year_min
    year_max = args.year_max
    if year_max is None:
        year_max = datetime.now().year

    citations = []
    for year in range(year_min, year_max+1):
        query={Name.published:str(year)}
        res=ipni.search(query,filters = [Filters.infraspecific,Filters.specific])
        for r in res:
            citations.append(r)
        if not args.quiet:
            print(year,end='\r')
    df=pd.DataFrame(pd.json_normalize(citations))

    # Add DOI if available
    mask = df.remarks.notnull()
    df.loc[mask, 'doi_ipni']=df[mask]['remarks'].apply(lambda x: nameutil.extractDoi(str(x)))

    # Backfill DOIs from CoL
    df_dois = pd.read_csv(args.inputfile_dois, sep='\t')
    df_dois.rename(columns={'ID':'id','doi':'doi_col'},inplace=True)
    
    df = pd.merge(left=df,right=df_dois, left_on='id',right_on='id',how='left')

    df['doi']=[None]*len(df)
    mask=(df.doi_ipni.notnull())
    df.loc[mask,'doi']=df[mask].doi_ipni
    mask=(df.doi.isnull() & df.doi_col.notnull())
    df.loc[mask,'doi']=df[mask].doi_col

    # Drop temporary columns
    df.drop(columns=['doi_ipni','doi_col'],inplace=True)

    # Add epublished flag
    mask = df.remarks.notnull()
    df.loc[mask, 'epubl']=df[mask]['remarks'].apply(lambda x: nameutil.isEpublished(str(x)))
    df.epubl.fillna(False)

    # Add publ_type flag as publication level
    mask=(df['linkedPublication.fqId'].notnull())
    dfp = pd.DataFrame(df[mask][['linkedPublication.fqId','linkedPublication.issn','linkedPublication.bphNumber']].drop_duplicates())
    dfp.columns=['id','issn','bphNumber']
    dfp['publ_type'] = dfp.apply(lambda row: getPublType(row['id'],row['issn'],row['bphNumber']),axis=1)

    # Apply publ_type to name level data
    df = pd.merge(left=df,
                right=dfp.rename(columns={'id':'linkedPublication.fqId'}),
                left_on='linkedPublication.fqId',
                right_on='linkedPublication.fqId',
                how='left')
    # Add publ_type = serial status for those records with a doi and serial format collations
    mask = (df.doi.notnull() & df.referenceCollation.str.contains(':') & df.publ_type.isnull())
    df.loc[mask,'publ_type'] = 'serial'

    df.to_csv(args.outputfile, sep=args.delimiter, encoding='utf8', index=False)

if __name__ == "__main__":
    main()
