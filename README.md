# ipni-oa
How many names published in IPNI are available open access?

## Background

IPNI record DOIs against the publications in which new nomenclatural acts are found. This data element has been recorded since 2012.

## Research questions

1. What proportion of IPNI monitored nomenclatural acts are published open access, and how is this changing over time?
1. What OA statuses (green, gold, bronze, hybrid etc) are reported, and how are these changing over time?
1. Do these trends vary with the WCVP distribution of the species?

## How to use this repository

### Pre-requisites

The software is written in `Python` and execution is managed with the build tool `make`.
APIs are used to access IPNI data (via `pykew`) and unpaywall (via the `unpywall` package).
Software package dependencies are specified in `requirements.txt`

### How to set up the environment

1. Create a virtual environment: `python -m venv env`
2. Activate the virtual environment: `source env/Scripts/activate`
3. Install dependencies: `pip install -r requirements.txt`

### How to define the time period to be analysed

The `Makefile` includes a `year_min` variable which is passed to the `getipninames.py` script to select the initial set of records. By default this is set to `2012`.

### Seeing what will be done for each step

A report of the actions that will be taken to build a particular Makefile target can be seen by using the `--dry-run` flag. For example to see the actions taken to process the `reportoa` target use `make reportoa --dry-run`.

### Estimating the time taken to run the analysis

The unpaywall lookup will take some time (several hours for datasets of thousands of records). The `unpywall` utility offers a cache option which stores the results of a lookup and uses this local cache for subsequent requests. See more details here: https://unpywall.readthedocs.io/en/latest/cache.html. The cache file is named `unpaywall_cache` and is specified in `.gitignore`.

### How to run the analysis

A complete run can be initiated with `make all` or individual steps are detailed below.

1. Download names from IPNI
    - **Script** `getipninames.py`
    - **Outputfile:** `downloads/ipninames.csv`
    - **Method** Using the time period specified by the `year_min` variable, IPNI names are downloaded using the `pykew` API wrapper.
    - **How to run:** Use the Makefile target: `make downloads/ipninames.csv` or the shorthand: `make getnames`
1. Lookup DOI labelled literature in unpaywall
    - **Script** `ipninames2oastatus.py`
    - **Inputfile(s):** `downloads/ipninames.csv`
    - **Outputfile:** `data/ipniname-oastatus.csv`
    - **Method:** Using the extracted DOI, make a call to unpaywall (https://unpaywall.org/) using the `unpywall` API wrapper and store the results in CSV format.
    - **How to run:** Use the Makefile target: `make data/ipniname-oastatus.csv` or the shorthand: `make getoastatus`
1. Report on OA status over time
    - **Script** `reportoastatus.py`
    - **Inputfile(s):** `data/ipniname-oastatus.csv`
    - **Outputfile:** `data/ipniname-oastatus-report.csv`
    - **Method:** Summarise the unpaywall data, by grouping on year, whether the literature item has a doi available (`has_doi`), if the literature is available open access (`is_oa`) and the open access status (`oa_status` - green, gold, bronze, hybrid etc), and counting the size of each of the groups.
    - **How to run:** Use the Makefile target: `make data/ipniname-oastatus-report.csv` or the shorthand: `make reportoa`
1. Plot OA takeup over time
    - **Script** `plotoa.py`
    - **Inputfile(s):** `data/ipniname-oastatus-report.csv`
    - **Outputfile:** `data/oatrend.png`
    - **Method:** Organise the unpaywall data by year and plot a stacked bar graph of OA takeup.
    - **How to run:** Use the Makefile target: `make data/oatrend.png` or the shorthand: `make plotoa`    
1. Plot OA status over time
    - **Script** `plotoatype.py`
    - **Inputfile(s):** `data/ipniname-oastatus-report.csv`
    - **Outputfile:** `data/oastatustrend.png`
    - **Method:** Organise the unpaywall data by year and plot a stacked bar graph of OA status.
    - **How to run:** Use the Makefile target: `make data/oastatustrend.png` or the shorthand: `make plotoastatus`    
1. Indicate any correlations between WCVP distribution of species and OA status.
    - TBC
    - **Script**
    - **Method**
    - **How to run** 
    - **Outputfile:**

### Cleaning up downloaded and processed files

Two utility make targets are provided for this:

- `make clean` -  removes all processed files (ie the contents of the `data` directory)
- `make sterilise` - removes all processed files *and* all downloaded files (ie the contents of both the `data` and `downloads` directories)

### How to archive an analysis, suitable for reference in an article

1. Execute an complete analysis using `make all`
1. Archive the inputs and results using `make archive`
1. Tag the software version used using git tag, and push the tag to github
1. Create a release in github using the tag created in the previous step and attach the archived file to the github release


## Contributing

### Reporting bugs and feature requests

Please use the [github issue tracker](https://github.com/OA-WCVP/ipni-oa) associated with this project to report bugs and make feature requests.

### Commit messages

Please link your commit message to an issue which describes what is being implemented or fixed.


### Environment updates

Any new dependencies should be added to `requirements.txt` and committed to git. The `env` directory is specified in `.gitignore`, please do not commit this to git.

### Outputs (data files and chart images)

The `data` and `download` directories are specified in `.gitignore`, so please do not commit these, or any outputs such as data files / chart images to git. Instead you should:

1. Develop a script which automates the construction of the output (the datafile or chart image)
2. Add a target to the `Makefile` which will: 
    - Define the dependencies of the output (the script used to create the output, and any input files required)
    - Call the script and generate the output
3. Update the instructions above

Similarly, the `archive` directory is specified in `.gitignore`, please do not commit this or any of its contents to git - instead follow the process laid out in the "How to archive an analysis" section above.

## Contact information

[Nicky Nicolson](https://github.com/nickynicolson), RBG Kew (n.nicolson@kew.org)