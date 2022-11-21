import argparse

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile')
    parser.add_argument('-g','--groupby', type=str, default='publicationYear')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--plot-percentage', action='store_true')
    parser.add_argument('--log_axis', action='store_true')
    parser.add_argument('--horizontal', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('--yearmin', default='2012')
    parser.add_argument('--yearmax', default='2021')
    parser.add_argument('--percentage_coverage', default=0.80)
    parser.add_argument('outputfile_chart')
    parser.add_argument('outputfile_table')
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
    # Add total
    dfg['total']=dfg.sum(axis=1)

    #
    # 2.4 If we are grouping by publication, select the top n most numerous publications to plot
    if args.groupby == 'publication':
        
        grand_total = dfg['total'].sum()
        print(dfg.sort_values(by='total',ascending=False).head(n=50)['total'].sum())
        dfg = dfg.sort_values(by='total',ascending=False)
        # Add cumulative total
        dfg['contribution'] = dfg['total']/grand_total
        dfg['contribution_cs'] = dfg['contribution'].cumsum()
        dfg['include'] = dfg['contribution_cs']<args.percentage_coverage
        n = len(dfg[dfg['include']]) + 1
        print('Using top {} publication'.format(n))
        print(dfg.head(n=n*2))
        dfg = dfg.head(n=n)
        print(dfg)
    #
    # 2.5 Convert to a percentage data structure
    if (args.plot_percentage):
        dfg['total']=dfg.sum(axis=1)
        dfg.columns=['False','True',na_label,'total']
        for col in ['False','True',na_label]:
            dfg[col] = dfg[col]/dfg['total']
        #dfg.drop(columns='total',inplace=True)
        dfg = dfg*100

    ###########################################################################
    # 3. Plot and save figure to outputfile
    ###########################################################################
    colour_mapper = {'True':'#79be78','False':'#c5c5c5', na_label:'#ffffff'}
    colours = [colour_mapper[oa] for oa in oas]
    kind = 'bar'
    
    cat_axis_label_method = plt.xlabel
    cat_axis_label_method = plt.ylabel
    num_axis_lim_method = plt.ylim
    num_axis_label_method = plt.ylabel
    logx=False
    logy=False
    ascending=False
    figsize=mpl.rcParams["figure.figsize"]
    loc='upper right'
    if args.horizontal:
        kind = 'barh'
        logy=False
        logx=args.log_axis
        cat_axis_label_method = plt.ylabel
        num_axis_label_method = plt.xlabel
        num_axis_lim_method = plt.xlim
        ascending=True
        figsize=(8,12)
        loc='lower right'
        
    dfg.sort_values(by='total',ascending=ascending)[['True','False',na_label]].plot(kind=kind, stacked=True, linewidth=1, logx=logx, logy=logy, edgecolor='k', color=colours, figsize=figsize)
    plt.legend(title='Open access', loc=loc)
    if args.plot_percentage:
        num_axis_lim_method((0,100))
        num_axis_label_method("Percentage of nomenclatural acts")
        plt.legend(bbox_to_anchor=(1.0, 1.0))
    else:
        if args.log_axis:
            num_axis_lim_method((1,100000))
        # else:
        #     num_axis_lim_method((0,12000))
        num_axis_label_method("Number of nomenclatural acts")
    plt.title("OA status of IPNI nomenclatural acts {}-{}".format(args.yearmin,args.yearmax))
    cat_axis_label_method(args.groupby)
    plt.tight_layout()
    plt.savefig(args.outputfile_chart)
    dfg.to_csv(args.outputfile_table,sep='\t')

if __name__ == "__main__":
    main()
