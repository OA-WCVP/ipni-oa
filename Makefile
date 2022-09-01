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

data/ipniname-oastatus-wcvp.txt: addwcvp.py data/ipniname-oastatus.csv downloads/wcvp_names.txt downloads/wcvp_distributions.txt
	mkdir -p data
	$(python_launch_cmd) $^ $(limit_args) $@

addwcvp: data/ipniname-oastatus-wcvp.txt


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

###############################################################################
# Report on OA status per WCVP dist - all nomenclatural acts
data/ipniname-oastatus-wcvp-report-%.csv: reportoastatusbydist.py data/ipniname-oastatus-wcvp.txt
	$(python_launch_cmd) $^ $(limit_args) --tdwg_wgsrpd_level=$* $@
# Shorthand:
reportoa_level_1: data/ipniname-oastatus-wcvp-report-1.csv
reportoa_level_2: data/ipniname-oastatus-wcvp-report-2.csv
reportoa_level_3: data/ipniname-oastatus-wcvp-report-3.csv
###############################################################################

###############################################################################
#  Plot OA takeup by WCVP dist - all nomenclatural acts
data/oatrend-dist-%.png: plotoadist.py data/ipniname-oastatus-wcvp-report-%.csv
	$(python_launch_cmd) $^ $(limit_args) --tdwg_wgsrpd_level=$* $@
# Shorthand:
plotoa_level1: data/oatrend-dist-1.png
plotoa_level2: data/oatrend-dist-2.png
plotoa_level3: data/oatrend-dist-3.png
###############################################################################

###############################################################################
# Report on OA status per WCVP dist - tax novs only
data/ipniname-oastatus-wcvp-report-%-taxnov.csv: reportoastatusbydist.py data/ipniname-oastatus-wcvp.txt
	$(python_launch_cmd) $^ $(limit_args) --tax_novs_only --tdwg_wgsrpd_level=$* $@
# Shorthand:
reportoa_level_1_taxnov: data/ipniname-oastatus-wcvp-report-1-taxnov.csv
reportoa_level_2_taxnov: data/ipniname-oastatus-wcvp-report-2-taxnov.csv
reportoa_level_3_taxnov: data/ipniname-oastatus-wcvp-report-3-taxnov.csv
###############################################################################

###############################################################################
#  Plot OA takeup by WCVP dist - tax novs only
data/oatrend-dist-%-taxnov.png: plotoadist.py data/ipniname-oastatus-wcvp-report-%-taxnov.csv
	$(python_launch_cmd) $^ $(limit_args)  --tax_novs_only --tdwg_wgsrpd_level=$* $@
# Shorthand:
plotoa_level1_taxnov: data/oatrend-dist-1-taxnov.png
plotoa_level2_taxnov: data/oatrend-dist-2-taxnov.png
plotoa_level3_taxnov: data/oatrend-dist-3-taxnov.png
###############################################################################

all: data/oatrend.png data/oastatustrend.png data/oatrend-dist-1.png data/oatrend-dist-2.png data/oatrend-dist-3.png data/oatrend-dist-1-taxnov.png data/oatrend-dist-2-taxnov.png data/oatrend-dist-3-taxnov.png

data_archive_zip:=$(shell basename $(CURDIR))-data.zip
downloads_archive_zip:=$(shell basename $(CURDIR))-downloads.zip

archive:
	mkdir -p archive	
	echo "Archived on $(date_formatted)" >> data/archive-info.txt
	zip archive/$(data_archive_zip) data/* -r
	echo "Archived on $(date_formatted)" >> downloads/archive-info.txt
	zip archive/$(downloads_archive_zip) downloads/* -r
	
clean:
	rm -f data/*

cleancharts:
	rm -f data/*.png

sterilise:
	rm -f data/*
	rm -f downloads/*
