year_min = 2012
wcvp_name_url=https://www.dropbox.com/s/pkpv3tc5v9k0thh/wcvp_names.txt?dl=0
wcvp_dist_url=https://www.dropbox.com/s/9vefyzzp978m2f1/wcvp_distribution.txt?dl=0

python_launch_cmd=python
python_launch_cmd=winpty python

date_formatted=$(shell date +%Y%m%d-%H%M%S)

# limit_args can be used in any step that reads a data file (ie explode and link) 
# It will reduce the number of records processed, to ensure a quick sanity check of the process
#limit_args= --limit=1000
limit_args=

# filter_args can be used in the link step to filter processing to a set of known records for debugging purposes.
filter_args=--filter_ids=77103635-1
filter_args=

downloads/wcvp_names.txt:
	mkdir -p downloads
	wget -O $@ $(wcvp_name_url)

downloads/wcvp_distributions.txt:
	mkdir -p downloads
	wget -O $@ $(wcvp_dist_url)

downloads/ipninames.csv: getipninames.py
	mkdir -p downloads
	$(python_launch_cmd) getipninames.py --year_min $(year_min) $@

getnames: downloads/ipninames.csv

###############################################################################
# Lookup literature in unpaywall
data/ipniname-oastatus.csv: ipninames2oastatus.py downloads/ipninames.csv
	mkdir -p data
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
getoastatus: data/ipniname-oastatus.csv
###############################################################################

data/ipninames-w-wcvp.txt: addwcvp.py downloads/ipninames.csv downloads/wcvp_names.txt downloads/wcvp_distributions.txt
	mkdir -p data
	$(python_launch_cmd) $^ $(limit_args) $@

addwcvp: data/ipninames-w-wcvp.txt


###############################################################################
# Report on OA status over time
data/ipniname-oastatus-report.csv: reportoastatus.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
reportoa: data/ipniname-oastatus-report.csv
###############################################################################

###############################################################################
#  Plot OA takeup over time
data/oatrend.png: plotoa.py data/ipniname-oastatus-report.csv
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
plotoa: data/oatrend.png
###############################################################################

###############################################################################
#  Plot OA status over time
data/oastatustrend.png: plotoastatus.py data/ipniname-oastatus-report.csv
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
plotoastatus: data/oastatustrend.png
###############################################################################

all: data/oatrend.png data/oastatustrend.png

archive:
	mkdir -p archive
	zip archive/data-$(date_formatted).zip data/* -r
	zip archive/downloads-$(date_formatted).zip downloads/* -r

clean:
	rm -f data/*

sterilise:
	rm -f data/*
	rm -f downloads/*