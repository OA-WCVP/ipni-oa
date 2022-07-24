import pandas as pd
pd.set_option('display.max_rows',100)
import argparse
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", default=None, type=int)
    parser.add_argument("--tdwg_wgsrpd_level", default=3, type=int)
    parser.add_argument("--tax_novs_only", action='store_true')
    parser.add_argument("inputfile", type=str)
    parser.add_argument("outputfile", type=str)
    args = parser.parse_args()

    ###########################################################################
    # 1. Read data file
    ###########################################################################
    df = pd.read_csv(args.inputfile, nrows=args.limit, sep='\t')
    print('Read {} of {} IPNI name dist rows'.format(args.inputfile, len(df)))
    print(df.sample(n=1).T)
    # 1.1 Replace nan w None
    df = df.replace({np.nan:None})
    # 1.2 Add placeholder for NULL values in is_oa and oa_status fields
    df.is_oa.fillna('n/a',inplace=True)
    df.oa_status.fillna('n/a',inplace=True)
    # 1.3 Drop records that are not tax. novs
    if args.tax_novs_only:
        dropmask = (df.citationType.isin(['tax. nov.'])==False)
        df.drop(df[dropmask].index, inplace=True)
        print('Retained {} IPNI name dist rows'.format(len(df)))

    ###########################################################################
    # 2. Determine at which TDWG WGSRPD level we are operating, drop un-needed
    # columns and duplicated rows
    ###########################################################################
    # 2.1 Create a variable to hold the column name
    tdwg_wgsrpd_col={1:'continent',2:'region',3:'area'}[args.tdwg_wgsrpd_level]
    # 2.2 Drop un-needed columns
    retain_cols = ['ipni_id', 'is_oa', tdwg_wgsrpd_col]
    drop_cols = [col for col in df.columns if col not in retain_cols]
    df.drop(columns=drop_cols, inplace=True)
    # 2.3 Drop duplicated rows
    df.drop_duplicates(inplace=True)

    ###########################################################################
    # 3. Normalise the contribution of each name to the overall total
    # This step is requires as a taxon can be distributed across multiple 
    # distribution units
    # To normalise the contribution of a name, we do the following:
    # 3.1. Count how many distribution units are attached to the name
    # 3.2. Allocate a value to each name dist record which is the reciprocal 
    # of the distribution unit count
    # 3.3 Copy this value to the name dist data structure
    # This ensures that the total contribution for each name to the overall count is 1 
    ###########################################################################
    
    # 3.1. Count how many distribution units are attached to the name
    dfc = df[df[tdwg_wgsrpd_col].notnull()].groupby('ipni_id').agg({tdwg_wgsrpd_col:'nunique'}).reset_index()
    # 3.2. Allocate a value to each name record which is the reciprocal of the 
    # distribution unit count
    dfc['contribution'] = 1/dfc[tdwg_wgsrpd_col]
    # 3.3 Copy this value to the name dist data structure
    df = pd.merge(left=df[df[tdwg_wgsrpd_col].notnull()],right=dfc[['ipni_id','contribution']],left_on='ipni_id',right_on='ipni_id',how='left')

    ###########################################################################
    # 4. Group by TDWG WGSRPD level and oa_status, calculating the total 
    # contribution for each group
    ###########################################################################
    dfg = df.groupby([tdwg_wgsrpd_col, 'is_oa']).agg({'contribution':'sum'})
    print(dfg)
    # 4.1 Sanity check that the summed contribution is the same as the number 
    # of names that can contribute to the analysis
    print('Number of records with distributions: {}, summed contribution: {}'.format(df[df[tdwg_wgsrpd_col].notnull()].ipni_id.nunique(), dfg.contribution.sum()))

    ###########################################################################
    # 5. Write output file
    ###########################################################################
    print('Writing {} WCVP distribution OA status rows to {} '.format(len(dfg), args.outputfile))
    dfg.reset_index().to_csv(args.outputfile, sep='\t', index=False)
    
if __name__ == '__main__':
    main()