import argparse

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np
import matplotlib.pyplot as plt

na_label = 'non-discoverable'
value_column = dict()
value_column['takeup'] = 'Open access takeup'
value_column['status'] = 'Open access status'

value_list = dict()
value_list['takeup'] = ['open','closed',na_label]
value_list['status'] = ['green','gold','hybrid','bronze','closed']

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile')
    parser.add_argument('-g','--groupby', type=str, default='publicationYear')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--plot-percentage', action='store_true')
    parser.add_argument('--plot_percentage_subplot_1', action='store_true')
    parser.add_argument('--plot_percentage_subplot_2', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('--plottype', type=str, default='composite')
    parser.add_argument('--year_min',type=int,default=2012)
    parser.add_argument('--year_max',type=int,default=2021)
    parser.add_argument('outputfile')

    args = parser.parse_args()

    ###########################################################################
    # 0. Check plot type
    ###########################################################################
    if args.plottype not in ['composite', 'status', 'takeup']:
        print('Unknown plot type: {}, exiting'.format(args.plottype))
        import sys
        sys.exit()
        
    ###########################################################################
    # 1. Read data files
    ###########################################################################
    df = pd.read_csv(args.inputfile, sep=args.delimiter, nrows=args.limit)
    df = df.replace({np.nan:None})
    df.rename(columns={'publicationYear':'year'},inplace=True)
    print(df.columns)
    # Drop data outside of specified range
    dropmask = (df.year.between(args.year_min,args.year_max)==False)
    df.drop(df[dropmask].index,inplace=True)
    print('Read {} of {} grouped IPNI name rows'.format(args.inputfile, len(df)))
    print(df)

    ###########################################################################
    # 2. Preparation
    ###########################################################################
    # 2.0
    # if args.removena:
    #     df.drop(df[df.is_oa.isnull()].index,inplace=True)

    # 2.1 Add placeholder for NULL values in is_oa and oa_status fields
    df['is_oa'] = df['is_oa'].map({True: 'open', False: 'closed'})  
    df.is_oa.fillna(na_label,inplace=True)
    df.oa_status.fillna(na_label,inplace=True)

    # mask = (df.is_oa)
    # df.loc[mask,'is_oa']='open'
    # mask = (df.is_oa==False)
    # df.loc[mask,'is_oa']='closed'

    print(df)

    #
    # 2.2 Rename columns
    column_renames = {'is_oa':'Open access takeup','oa_status':'Open access status'}
    df.rename(columns=column_renames,inplace=True)

    # 2.3 Determine what plot types required
    plottypes = [args.plottype]
    if args.plottype == 'composite':
        plottypes = ['takeup','status']

    fig, axes = plt.subplots(1,len(plottypes))
    
    if args.plottype != 'composite':
        axes = [axes]
    for plottype, ax, plot_percentage in zip(plottypes, axes, [args.plot_percentage_subplot_1,args.plot_percentage_subplot_2]):
        print(plot_percentage)

        reshape_and_plot(df, ax, plottype, plot_percentage)

        ax.legend(title=None, loc='best')
        #ax.get_legend().set_title(None)
        if plot_percentage:
            ax.set_ylim((0,100))
            ax.set_ylabel("Percentage of nomenclatural acts")
            ax.legend(bbox_to_anchor=(1.0, 1.0))
        else:
            ax.set_ylim((0,12000))
            ax.set_ylabel("Number of nomenclatural acts")
        ax.set_title("Open access {}".format(plottype))
        ax.set_xlabel("Year")
    
    handles, labels = axes[0].get_legend_handles_labels()
    axes[0].legend(handles[::-1], labels[::-1], title=None, loc='best',framealpha=0)

    if args.plottype == 'composite':
        plt.suptitle("Open access in IPNI monitored nomenclatural acts ({}-{})".format(args.year_min,args.year_max))
    plt.tight_layout()
    
    ###########################################################################
    # 3. Save figure to outputfile
    ###########################################################################
    plt.savefig(args.outputfile)

def reshape_and_plot(df, ax, plottype, plot_percentage):
    # 2.3 Reshape data - pivot
    df_plot = df[['year',value_column[plottype],'n']].pivot_table(index='year',columns=value_column[plottype],values='n',aggfunc=sum)
    values_as_columns = value_list[plottype]
    df_plot = df_plot[values_as_columns]
    print(df_plot)
    #
    #
    # 2.4 Convert to a percentage data structure
    if (plot_percentage):
        df_plot['total']=df_plot.sum(axis=1)
        print(df_plot.columns)
        df_plot.columns= values_as_columns + ['total']
        for col in values_as_columns:
            df_plot[col] = df_plot[col]/df_plot['total']
        df_plot.drop(columns='total',inplace=True)
        df_plot = df_plot*100

    colour_mapper = {'open':'#ffffff','green':'#79be78','gold':'#fde769','hybrid':'#feb352','bronze':'#d29766','closed':'#c5c5c5', na_label:'#000000'}
    colours = [colour_mapper[value] for value in values_as_columns]
    df_plot.plot(kind='bar', stacked=True, linewidth=1, edgecolor='k', color=colours, ax=ax,label=None)

if __name__ == "__main__":
    main()
