import argparse

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np

DEFAULT_DATE_RANGE='2012 - 2021'
def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile_publ_report')
    parser.add_argument('inputfile_publ_urls')
    parser.add_argument('--daterange', type=str, default=DEFAULT_DATE_RANGE)
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('outputfile')

    args = parser.parse_args()

    ###########################################################################
    # 1. Read data files
    ###########################################################################
    
    # 1.1 Publications report
    df = pd.read_csv(args.inputfile_publ_report, sep=args.delimiter, nrows=args.limit)
    df = df.replace({np.nan:None,'nan':None})

    # 1.2 Publication URLS
    df_url = pd.read_csv(args.inputfile_publ_urls, sep=args.delimiter, nrows=args.limit,keep_default_na=False,na_values=[''])
    df_url = df_url.replace({np.nan:None,'nan':None})

    # 1.3 Better formatting for ISSNs
    mask = df['journal_issns'].notnull()
    df.loc[mask,'journal_issns'] = df[mask]['journal_issns'].apply(lambda x: x.replace(',','\n'))

    ###########################################################################
    # 2. Assign URLs
    ###########################################################################
    df = pd.merge(left=df,right=df_url,left_on='linkedPublication.abbreviation',right_on='linkedPublication.abbreviation',how='left')

    ###########################################################################
    # 3. Set user friendly column names
    ###########################################################################
    mask = df['bibjson.oa_start'].notnull()
    df.loc[mask,'bibjson.oa_start'] = df[mask]['bibjson.oa_start'].apply(lambda x: str(int(x)))

    column_names = {'linkedPublication.abbreviation':'Abbreviation',
       'journal_issns':'ISSN',
       'bibjson.oa_start':'Open access since',
       'bibjson.apc.has_apc':'Has APC',
       'bibjson.apc.max':'APC cost', 
       'url':'Link'}
    df = df[column_names.keys()]
    df.rename(columns=column_names,inplace=True)
    # Replace nans
    df.fillna('', inplace=True)

    ###########################################################################
    # 4. Save data to outputfile
    ###########################################################################
    daterange = args.daterange
    if args.daterange == 'all':
         daterange = DEFAULT_DATE_RANGE
    
    title='## Publications covering 80% of nomenclatural act dataset ({})'.format(daterange)
    with open(args.outputfile, 'w', encoding='utf8') as f:
        f.write(title+'\n\n<font size="1">\n\n')
        df.to_markdown(f, index=False, tablefmt="grid", mode='a')
        f.write('\n\n</font>\n\n')

if __name__ == "__main__":
    main()
