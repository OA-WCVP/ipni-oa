import argparse

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile')
    parser.add_argument('inputfile_doaj')
    parser.add_argument('inputfile_publ')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
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

    #
    # 1.1 Main data file
    df = pd.read_csv(args.inputfile, sep=args.delimiter, nrows=args.limit)
    df = df.replace({np.nan:None})
    print('Read {} of {} grouped IPNI name rows'.format(args.inputfile, len(df)))
    print(df)

    #
    # 1.2 Read publication datafile to add abbrev and title
    publ_cols = ['linkedPublication.abbreviation','linkedPublication.title','linkedPublication.issn','linkedPublication.remarks','journal_issns']
    df_publ = pd.read_csv(args.inputfile_publ, sep=args.delimiter, nrows=args.limit, usecols=['linkedPublication.id']+publ_cols)
    df = pd.merge(left=df,right=df_publ,left_on='linkedPublication.id',right_on='linkedPublication.id',how='left')

    #
    # 1.3 Read DOAJ report to flag and APC details
    doaj_cols=['bibjson.title','bibjson.oa_start','bibjson.ref.journal','bibjson.apc.has_apc','bibjson.apc.max']
    df_doaj = pd.read_csv(args.inputfile_doaj, sep=args.delimiter, nrows=args.limit, usecols=['linkedPublication.id']+doaj_cols)
    df = pd.merge(left=df,right=df_doaj,left_on='linkedPublication.id',right_on='linkedPublication.id',how='left')

    # 1.4 Add in DOAJ flag
    mask = (df['bibjson.title'].notnull())
    df.loc[mask,'in_doaj'] = True
    df['in_doaj'].fillna(False,inplace=True)

    # 1.5 Add DOAJ indicator on publication label
    df['publication_label'] = df['linkedPublication.abbreviation']
    mask = (df.in_doaj)
    df.loc[mask,'publication_label'] = df.publication_label.apply(lambda x: x + ' (*)')

    # 1.6 Establish label for chart
    groupcol = 'publication_label'

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
    dfg = df.groupby([groupcol,'Open access']).n.sum().reset_index()
    # 2.3.2 Pivot table to get a column per Open access (T, F or n/a), values are totals
    dfg = dfg[[groupcol,'Open access','n']].pivot_table(index=groupcol,columns='Open access',values='n')
    dfg.columns = dfg.columns.get_level_values('Open access')
    dfg = dfg[['True','False',na_label]]
    oas = ['Open', 'Closed', na_label]
    dfg.columns = oas
    # Add total
    dfg['total']=dfg.sum(axis=1)

    #
    # 2.4 Group by publication    
    grand_total = dfg['total'].sum()
    dfg.sort_values(by='total',ascending=False, inplace=True)
    # Add cumulative total
    dfg['contribution'] = dfg['total']/grand_total
    dfg['contribution_cs'] = dfg['contribution'].cumsum()
    dfg['include'] = dfg['contribution_cs']<args.percentage_coverage
    n = len(dfg[dfg['include']]) + 1
    print('Using top {} publication'.format(n))
    dfg = dfg.head(n=n)

    ###########################################################################
    # 3. Plot and save figure to outputfile
    ###########################################################################
    
    colour_mapper = {'Open':'#ffffff','Closed':'#c5c5c5', na_label:'#000000'}
    colours = [colour_mapper[oa] for oa in oas]
    
    figsize=(8,10) # default is mpl.rcParams["figure.figsize"]
    fig, axes = plt.subplots(1,1)
    dfg.sort_values(by='total',ascending=True)[['Open','Closed',na_label]].plot(kind='barh', stacked=True, linewidth=1, edgecolor='k', color=colours, figsize=figsize,ax=axes)
    plt.legend(title='Open access', loc='lower right')
    plt.xlabel("Number of nomenclatural acts")
    
    title = "OA status by publication ({}-{})".format(args.yearmin,args.yearmax)
    if args.yearmin == args.yearmax:
        # simplify title if its a single year:
        title = "OA status by publication ({})".format(args.yearmin)
    plt.suptitle(title)
    plt.ylabel('Publication', rotation=0)
    plt.tight_layout()
    plt.savefig(args.outputfile_chart)

    dfg = pd.merge(left=dfg,right=df[['linkedPublication.id','publication_label']+publ_cols+doaj_cols].drop_duplicates(),left_on='publication_label',right_on='publication_label',how='inner')
    output_cols = ['linkedPublication.id','linkedPublication.abbreviation',	'linkedPublication.title',	'linkedPublication.issn',	'linkedPublication.remarks',	'journal_issns', 'bibjson.title',	'bibjson.oa_start',	'bibjson.ref.journal',	'bibjson.apc.has_apc',	'bibjson.apc.max']
    dfg[output_cols].to_csv(args.outputfile_table,sep='\t',index=False)

if __name__ == "__main__":
    main()
