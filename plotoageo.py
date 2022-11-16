import argparse
from cProfile import label

import pandas as pd
pd.set_option('display.max_rows',200)
import numpy as np
import matplotlib.pyplot as plt
import geopandas

dist_level_mapper=dict()
dist_level_mapper[1]='continent'
dist_level_mapper[2]='region'
dist_level_mapper[3]='area'

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('inputfile')
    parser.add_argument('-l','--limit', type=int, default=None)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument("--tdwg_wgsrpd_level", default=2, type=int)
    parser.add_argument("--tax_novs_only", action='store_true')
    parser.add_argument('--plot-maps', action='store_true')
    parser.add_argument('-d','--delimiter', type=str, default='\t')
    parser.add_argument('outputfile_oa')
    parser.add_argument('outputfile_unknown')

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
    # 2.5 Calculate fractions of OA and unfindables
    if (args.plot_maps):
        df['total']=df.sum(axis=1)
        df['OA_ratio']  = df['OA_true']/df['OA_false']
        df['OA_unfind'] = df['OA_n/a']/df['total']
        df['OA_unfind'] = df['OA_unfind']*100
        df.drop(columns='total',inplace=True)
    print(df)

    # 2.6 Import the map of the world
    world = geopandas.read_file("./data/level{}.geojson".format(args.tdwg_wgsrpd_level))

    column_renames = {area_name_column.capitalize():'LEVEL{}_NAM'.format(args.tdwg_wgsrpd_level)}
    df.rename(columns=column_renames,inplace=True)

    world = pd.merge(world, df, on='LEVEL{}_NAM'.format(args.tdwg_wgsrpd_level))

    ###########################################################################
    # 3. Plot and save figure to outputfile
    ###########################################################################
    
    # 3.1 plotting the ratio between open and closed access
    fig, ax = plt.subplots(1, 1)
    world.plot(column='OA_ratio',ax=ax, legend=True, cmap='OrRd', scheme='quantiles')
    if args.tax_novs_only:
        plt.title("Ratio Open/Closed access of all tax. nov. IPNI nomenclatural acts")
    else:
        plt.title("Ratio Open/Closedaccess of all IPNI nomenclatural acts")
    plt.tight_layout()
    plt.savefig(args.outputfile_oa)

    # 3.2 plotting the percentage of unfindable publications
    fig, ax = plt.subplots(1, 1)
    world.plot(column='OA_unfind',ax=ax, legend=True, cmap='OrRd', scheme='quantiles')
    if args.tax_novs_only:
        plt.title("Proportion of unfindable publications of tax. nov. IPNI nomenclatural acts")
    else:
        plt.title("Proportion of unfindable publications of all IPNI nomenclatural acts")
    plt.tight_layout()
    plt.savefig(args.outputfile_unknown)

if __name__ == "__main__":
    main()
