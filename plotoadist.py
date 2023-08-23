import argparse
from cProfile import label

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np
import matplotlib.pyplot as plt

dist_level_mapper=dict()
dist_level_mapper[1]='continent'
dist_level_mapper[2]='region'
dist_level_mapper[3]='area'

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument("--tdwg_wgsrpd_level", default=3, type=int)
    parser.add_argument("--tax_novs_only", action='store_true')
    parser.add_argument('--plot-percentage', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('outputfile')

    args = parser.parse_args()

    ###########################################################################
    # 1. Read data files
    ###########################################################################
    df = pd.read_csv(args.inputfile, sep=args.delimiter, nrows=args.limit)
    df = df.replace({np.nan:None})
    print('Read {} of {} grouped WCVP dist rows'.format(args.inputfile, len(df)))

    ###########################################################################
    # 2. Preparation
    ###########################################################################
    # 2.1 Add placeholder for NULL values in is_oa and oa_status fields
    df.is_oa.fillna('n/a',inplace=True)
    #df.oa_status.fillna('n/a',inplace=True)
    #
    # 2.2 Rename columns
    column_renames = {'is_oa':'Open access'}
    df.rename(columns=column_renames,inplace=True)
    #
    # 2.3 Use TDWG WGSRPD level to determine area name column (continent, region, area etc)
    area_name_column = dist_level_mapper[args.tdwg_wgsrpd_level] 
    print(args.tdwg_wgsrpd_level, area_name_column)
    #
    # 2.4 Pivot table to get a column per Open access (T, F or n/a), values are totals
    df = df.pivot_table(index=area_name_column,columns='Open access',values='contribution').reset_index()
    df.columns=[area_name_column.capitalize(),'OA_false','OA_true','OA_n/a']
    print(df)

    #
    # 2.4 Convert to a percentage data structure
    if (args.plot_percentage):
        df['total']=df.sum(axis=1)
        for col in ['OA_false','OA_true','OA_n/a']:
            df[col] = df[col]/df['total']
            df[col] = df[col]*100
        df.drop(columns='total',inplace=True)
    print(df)

    ###########################################################################
    # 3. Plot and save figure to outputfile
    ###########################################################################
    df[[area_name_column.capitalize(),'OA_false','OA_true','OA_n/a']].set_index(area_name_column.capitalize()).plot(kind='bar', stacked=True,figsize=(10, 8))
    plt.legend(title='Open access', loc='upper left')
    #plt.ylim((0,12000))
    if args.tax_novs_only:
        plt.title("Open access status of tax. nov. IPNI nomenclatural acts by WCVP distribution")
    else:
        plt.title("Open access status of all IPNI nomenclatural acts by WCVP distribution")
    if args.plot_percentage:
        plt.ylabel("Percentage of nomenclatural acts")
        plt.legend(bbox_to_anchor=(1.0, 1.0))
    else:
        plt.ylabel("Number of nomenclatural acts")
    plt.xlabel(area_name_column.capitalize())
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(args.outputfile, dpi=300)


if __name__ == "__main__":
    main()
