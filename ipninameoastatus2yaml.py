import pandas as pd
pd.set_option('display.max_rows',100)
import argparse
import numpy as np
import yaml
from statistics import mean 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", default=None, type=int)
    parser.add_argument("--email_address", default='n.nicolson@kew.org', type=str)
    parser.add_argument("inputfile", type=str)
    parser.add_argument("--delimiter", type=str, default='\t')
    parser.add_argument('--year_min',type=int,default=2012)
    parser.add_argument('--year_max',type=int,default=2021)
    parser.add_argument("outputfile", type=str)
    args = parser.parse_args()

    df = pd.read_csv(args.inputfile,sep=args.delimiter)

    # Drop data out of range
    dropmask = df.publicationYear.between(args.year_min,args.year_max)==False
    df.drop(df[dropmask].index,inplace=True)

    # Set up output data structure
    output_variables = dict()

    output_variables['year_min']=args.year_min
    output_variables['year_max']=args.year_max

    # Calculate number of years in study
    output_variables['number_of_years'] = len(df.publicationYear.unique())

    # Calculate total number of records
    output_variables['nomenclatural_act_count'] = len(df)
    
    # Calculate number of DOIs found in IPNI data
    output_variables['dois_from_ipni'] = len(df[df.doi_ipni.notnull()])
    output_variables['dois_from_col'] = len(df[df.doi_ipni.isnull()&df.doi_col.notnull()])

    # Calculate number of unresolvable DOIs
    output_variables['dois_unresolvable'] = len(df[df.doi.notnull()&df.is_oa.isnull()])

    # Which publications have DOIs none of which are resolvable
    dfg = pd.merge(left=df[df.doi.notnull()].groupby('publication').size().to_frame('doi_count'),
                    right=df[df.doi.notnull()&df.is_oa.isnull()].groupby('publication').size().to_frame('doi_unresolved_count'),
                    left_index=True,
                    right_index=True,
                    how='left')
    dfg.fillna(0,inplace=True)
    #print(dfg[dfg.doi_unresolved_count==dfg.doi_count].sort_values(by='doi_count',ascending=False))

    output_variables['publications_w_unresolvable_dois'] = len(dfg[dfg.doi_unresolved_count==dfg.doi_count])
    #print(dfg[dfg.doi_resolved_count==0])

    # Calculate total number of nomenclatural acts
    output_variables['nomenclatural_act_total'] = len(df)

    # Calculate total number of nomenclatural acts that are undiscoverable
    mask = (df.is_oa.isnull())
    output_variables['nomenclatural_act_undiscoverable_total'] = len(df[mask])
    output_variables['nomenclatural_act_undiscoverable_pc'] = round(len(df[mask])/len(df)*100)

    # Calculate total number of nomenclatural acts that are open
    mask = (df.is_oa.notnull()&df.is_oa)
    output_variables['nomenclatural_act_open_total'] = len(df[mask])
    output_variables['nomenclatural_act_open_pc'] = round(len(df[mask])/len(df)*100)

    # Calculate total number of nomenclatural acts that are undiscoverable
    mask = (df.is_oa.notnull()&(df.is_oa==False))
    output_variables['nomenclatural_act_closed_total'] = len(df[mask])
    output_variables['nomenclatural_act_closed_pc'] = round(len(df[mask])/len(df)*100)

    # Calculate total number of publications examined
    output_variables['publications_total'] = len(df.publicationId.unique())

    # Calculate mean number of publications examined each year
    output_variables['publications_annual_mean'] = round(mean(df.groupby('publicationYear').agg({'publicationId':'nunique'})['publicationId'].values))
    
    # Calculate fraction of names published in serials
    output_variables['nomenclatural_act_proportion_in_serial'] = round((len(df[df.publ_type=='serial'])/len(df))*100)

    # Calculate GLOVAP count
    publ_abbrev_glovap='Global Fl.'
    mask=(df.publication==publ_abbrev_glovap)
    output_variables['nomenclatural_act_glovap_count'] = len(df[mask])

    #print(output_variables)
    with open(args.outputfile, 'w') as f:
        yaml.dump(output_variables, f)

if __name__ == '__main__':
    main()