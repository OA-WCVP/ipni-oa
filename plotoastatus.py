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
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('--yearmin', default='2012')
    parser.add_argument('--yearmax', default='2021')
    parser.add_argument('--removena', action='store_true')
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
    # 2.0
    if args.removena:
        df.drop(df[df.is_oa.isnull()].index,inplace=True)

    # 2.1 Add placeholder for NULL values in is_oa and oa_status fields
    na_label = 'non-discoverable'
    df.is_oa.fillna(na_label,inplace=True)
    df.oa_status.fillna(na_label,inplace=True)
    #
    # 2.2 Rename columns
    column_renames = {'oa_status':'Open access status'}
    df.rename(columns=column_renames,inplace=True)
    #
    # 2.3 Reshape data - pivot
    print(df.groupby([args.groupby,'is_oa'])['n'].sum())
    df = df[[args.groupby,'Open access status','n']].pivot_table(index=args.groupby,columns='Open access status',values='n',aggfunc=sum)
    oa_statuses = ['green','gold','hybrid','bronze','closed']
    if not args.removena:
        oa_statuses.append(na_label)
    df = df[oa_statuses]
    print(df)
    #
    #
    # 2.4 Convert to a percentage data structure
    if (args.plot_percentage):
        df['total']=df.sum(axis=1)
        print(df.columns)
        df.columns= oa_statuses + ['total']
        for col in oa_statuses:
            df[col] = df[col]/df['total']
        df.drop(columns='total',inplace=True)
        df = df*100

    ###########################################################################
    # 3. Plot and save figure to outputfile
    ###########################################################################
    colour_mapper = {'green':'#79be78','gold':'#fde769','hybrid':'#feb352','bronze':'#d29766','closed':'#c5c5c5', na_label:'#ffffff'}
    colours = [colour_mapper[oa_status] for oa_status in oa_statuses]
    df.plot(kind='bar', stacked=True, linewidth=1, edgecolor='k', color=colours)
    plt.legend(title='Open access status', loc='best')
    if args.plot_percentage:
        plt.ylim((0,100))
        plt.ylabel("Percentage of nomenclatural acts")
        plt.legend(bbox_to_anchor=(1.0, 1.0))
    else:
        plt.ylim((0,12000))
        plt.ylabel("Number of nomenclatural acts")
    plt.title("OA status of IPNI nomenclatural acts {}-{}".format(args.yearmin,args.yearmax))
    plt.xlabel(args.groupby)
    plt.tight_layout()
    plt.savefig(args.outputfile)

if __name__ == "__main__":
    main()
