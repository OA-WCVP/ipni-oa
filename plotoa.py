import argparse

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--plot-percentage', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('outputfile')

    args = parser.parse_args()

    ###########################################################################
    # 1. Read data files
    ###########################################################################
    df = pd.read_csv(args.inputfile, sep=args.delimiter, nrows=args.limit)
    df = df.replace({np.nan:None})
    print('Read {} of {} grouped IPNI name rows'.format(args.inputfile, len(df)))

    ###########################################################################
    # 2. Preparation
    ###########################################################################
    # 2.1 Add placeholder for NULL values in is_oa and oa_status fields
    df.is_oa.fillna('n/a',inplace=True)
    df.oa_status.fillna('n/a',inplace=True)
    #
    # 2.2 Rename columns
    column_renames = {'is_oa':'Open access'}
    df.rename(columns=column_renames,inplace=True)
    #
    # 2.3 Reshape data
    # 2.3.1 Group and sum to get a total
    dfg = df.groupby(['year','Open access']).n.sum().reset_index()
    # 2.3.2 Pivot table to get a column per Open access (T, F or n/a), values are totals
    dfg = dfg[['year','Open access','n']].pivot_table(index='year',columns='Open access',values='n')
    print(dfg)
    #
    # 2.4 Convert to a percentage data structure
    if (args.plot_percentage):
        dfg['total']=dfg.sum(axis=1)
        dfg.columns=['False','True','n/a','total']
        for col in ['False','True','n/a']:
            dfg[col] = dfg[col]/dfg['total']
        dfg.drop(columns='total',inplace=True)
        dfg = dfg*100

    ###########################################################################
    # 3. Plot and save figure to outputfile
    ###########################################################################
    dfg.plot(kind='bar', stacked=True)
    plt.legend(title='Open access', loc='upper right')
    if args.plot_percentage:
        plt.ylim((0,100))
        plt.ylabel("Percentage of nomenclatural acts")
        plt.legend(bbox_to_anchor=(1.0, 1.0))
    else:
        plt.ylim((0,12000))
        plt.ylabel("Number of nomenclatural acts")
    plt.title("Open access status of IPNI monitored nomenclatural acts")
    plt.xlabel("Year")
    plt.tight_layout()
    plt.savefig(args.outputfile)

if __name__ == "__main__":
    main()
