import argparse
from datetime import datetime

import pandas as pd
import pykew.ipni as ipni
from ipniutil import nameutil
from pykew.ipni_terms import Filters, Name


def main():
    parser = argparse.ArgumentParser()
    
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
    df.loc[mask, 'doi']=df[mask]['remarks'].apply(lambda x: nameutil.extractDoi(str(x)))

    # Add epublished flag
    mask = df.remarks.notnull()
    df.loc[mask, 'epubl']=df[mask]['remarks'].apply(lambda x: nameutil.isEpublished(str(x)))
    df.epubl.fillna(False)
    
    df.to_csv(args.outputfile, sep=args.delimiter, encoding='utf8', index=False)

if __name__ == "__main__":
    main()
