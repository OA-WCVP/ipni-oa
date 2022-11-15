import argparse

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile')
    parser.add_argument('-g','--groupby', type=str, default='publicationYear')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--plot-percentage', action='store_true')
    parser.add_argument('--logy', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('--yearmin', default='2012')
    parser.add_argument('--yearmax', default='2021')
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
    na_label = 'non-discoverable'
    df.is_oa.fillna(na_label,inplace=True)
    df.oa_status.fillna(na_label,inplace=True)
    df.is_oa = df.is_oa.astype(str)
    #
    # 2.2 Rename columns
    column_renames = {'is_oa':'Open access'}
    df.rename(columns=column_renames,inplace=True)
    #
    # 2.3 Reshape data
    # 2.3.1 Group and sum to get a total
    dfg = df.groupby([args.groupby,'Open access']).n.sum().reset_index()
    # 2.3.2 Pivot table to get a column per Open access (T, F or n/a), values are totals
    dfg = dfg[[args.groupby,'Open access','n']].pivot_table(index=args.groupby,columns='Open access',values='n')
    dfg.columns = dfg.columns.get_level_values('Open access')
    oas=['True','False',na_label]
    dfg = dfg[oas]

    #
    # 2.4 If we are grouping by publication, select the top n most numerous publications to plot
    if args.groupby == 'publication':
        dfg['total']=dfg.sum(axis=1)
        dfg = dfg.sort_values(by='total',ascending=False).head(n=30)
    #
    # 2.5 Convert to a percentage data structure
    if (args.plot_percentage):
        dfg['total']=dfg.sum(axis=1)
        dfg.columns=['False','True',na_label,'total']
        for col in ['False','True',na_label]:
            dfg[col] = dfg[col]/dfg['total']
        dfg.drop(columns='total',inplace=True)
        dfg = dfg*100

    ###########################################################################
    # 3. Plot and save figure to outputfile
    ###########################################################################
    colour_mapper = {'True':'#79be78','False':'#c5c5c5', na_label:'#ffffff'}
    colours = [colour_mapper[oa] for oa in oas]
    dfg[['True','False',na_label]].plot(kind='bar', stacked=True, linewidth=1, logy=args.logy, edgecolor='k', color=colours)
    plt.legend(title='Open access', loc='upper right')
    if args.plot_percentage:
        plt.ylim((0,100))
        plt.ylabel("Percentage of nomenclatural acts")
        plt.legend(bbox_to_anchor=(1.0, 1.0))
    else:
        if args.logy:
            plt.ylim((1,100000))
        else:
            plt.ylim((0,12000))
        plt.ylabel("Number of nomenclatural acts")
    plt.title("OA status of IPNI nomenclatural acts {}-{}".format(args.yearmin,args.yearmax))
    plt.xlabel(args.groupby)
    plt.tight_layout()
    plt.savefig(args.outputfile)

if __name__ == "__main__":
    main()
