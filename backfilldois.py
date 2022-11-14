import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", default=None, type=int)
    parser.add_argument("inputfile_names", type=str)
    parser.add_argument("inputfile_refs", type=str)
    parser.add_argument("outputfile", type=str)
    args = parser.parse_args()

    dfn = pd.read_csv(args.inputfile_names, sep='\t', usecols=['ID','referenceID'])
    dfp = pd.read_csv(args.inputfile_refs, sep='\t', usecols=['ID','doi'])

    df = pd.merge(left=dfn,
                right=dfp.rename(columns={'ID':'referenceID'}),
                left_on='referenceID',
                right_on='referenceID',
                how='left')

    mask = (df.doi.notnull())
    df[mask][['ID','doi']].to_csv(args.outputfile, sep='\t', index=False)

if __name__ == '__main__':
    main()