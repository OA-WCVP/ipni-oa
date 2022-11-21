year_min = 2012
year_max = 2021
wcvp_name_url=https://www.dropbox.com/s/pkpv3tc5v9k0thh/wcvp_names.txt?dl=0
wcvp_dist_url=https://www.dropbox.com/s/9vefyzzp978m2f1/wcvp_distribution.txt?dl=0
ipni_coldp_url=https://zenodo.org/record/7208700/files/rdmpage/ipni-coldp-2022-10-15.zip?download=1

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

downloads/ipninames.csv: getipninames.py data/ipni-coldp-dois.tsv
	mkdir -p downloads
	$(python_launch_cmd) $^ --year_min $(year_min) --year_max $(year_max) $@
getnames: downloads/ipninames.csv

downloads/ipni-coldp-2022-10-15.zip:
	mkdir -p downloads
	wget -O $@ $(ipni_coldp_url)

downloads/rdmpage-ipni-coldp-8fe9cb4/names.tsv: downloads/ipni-coldp-2022-10-15.zip
	unzip -p $^  rdmpage-ipni-coldp-8fe9cb4/names.tsv >$@

downloads/rdmpage-ipni-coldp-8fe9cb4/references.tsv: downloads/ipni-coldp-2022-10-15.zip
	unzip -p $^  rdmpage-ipni-coldp-8fe9cb4/references.tsv >$@

data/ipni-coldp-dois.tsv: backfilldois.py downloads/rdmpage-ipni-coldp-8fe9cb4/names.tsv downloads/rdmpage-ipni-coldp-8fe9cb4/references.tsv
	$(python_launch_cmd) $^ $(limit_args) $@


###############################################################################
# Lookup literature in unpaywall
data/ipniname-oastatus.csv: ipninames2oastatus.py downloads/ipninames.csv
	mkdir -p data
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
getoastatus: data/ipniname-oastatus.csv
###############################################################################

###############################################################################
# Lookup journal metadata in DOAJ
data/oastatus2doaj.csv: oastatus2doaj.py data/ipniname-oastatus.csv
	mkdir -p data
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
getdoajmeta: data/oastatus2doaj.csv
###############################################################################

###############################################################################
# Calculate which repositories used for green status OA articles
data/oastatus2repositories.csv: oastatus2repositories.py data/ipniname-oastatus.csv
	mkdir -p data
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
getrepositories: data/oastatus2repositories.csv
###############################################################################

data/ipniname-oastatus-wcvp.txt: addwcvp.py data/ipniname-oastatus.csv downloads/wcvp_names.txt downloads/wcvp_distributions.txt
	mkdir -p data
	$(python_launch_cmd) $^ $(limit_args) $@

addwcvp: data/ipniname-oastatus-wcvp.txt

###############################################################################
# Status: green, gold, hybrid, bronze etc
# Takeup: T/F
###############################################################################
# Report on OA status over time
data/ipniname-oastatus-report-year.csv: reportoastatus.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
reportoayear: data/ipniname-oastatus-report-year.csv
###############################################################################

###############################################################################
# Report on OA status by publ
data/ipniname-oastatus-report-publ.csv: reportoastatus.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) --group publication $@
# Shorthand:
reportoapubl: data/ipniname-oastatus-report-publ.csv
###############################################################################

###############################################################################
# Report on OA status by publ - 2019-2021
data/ipniname-oastatus-report-publ-2019-2021.csv: reportoastatus.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) --yearmin=2019 --yearmax=2021 --group publication $@
# Shorthand:
reportoapubl: data/ipniname-oastatus-report-publ-2019-2021.csv
###############################################################################

###############################################################################
#  Plot OA takeup over time
data/ipni-oatrend-year.png: plotoa.py data/ipniname-oastatus-report-year.csv
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
plotoayear: data/ipni-oatrend-year.png
###############################################################################

###############################################################################
#  Plot OA status over time
data/ipni-oastatustrendpc.png: plotoastatus.py data/ipniname-oastatus-report-year.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage --removena $@
# Shorthand:
plotoastatus: data/ipni-oastatustrendpc.png
###############################################################################

###############################################################################
#  Plot OA takeup by publ
data/ipni-oatrend-publ.png: plotoa.py data/ipniname-oastatus-report-publ.csv
	# $(python_launch_cmd) $^ $(limit_args) --group publication --log_axis --horizontal $@
	$(python_launch_cmd) $^ $(limit_args) --group publication --horizontal $@
# Shorthand:
plotoapubl: data/ipni-oatrend-publ.png
###############################################################################

###############################################################################
#  Plot OA takeup by publ
data/ipni-oatrend-publ-2019-2021.png: plotoa.py data/ipniname-oastatus-report-publ-2019-2021.csv
	# $(python_launch_cmd) $^ $(limit_args) --group publication --log_axis --horizontal $@
	$(python_launch_cmd) $^ $(limit_args) --yearmin=2019 --yearmax=2021 --group publication --horizontal $@ 
# Shorthand:data/ipniname-oastatus-report-publ-2019-2021.csv
plotoapublyr: data/ipni-oatrend-publ-2019-2021.png
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

oatrends_charts_year:=data/ipni-oatrend-year.png
oastatus_charts_year:= data/ipni-oastatustrendpc.png
oatrends_charts_publ:=data/ipni-oatrend-publ.png data/ipni-oatrend-publ-2019-2021.png

wcvp_reports:= data/ipniname-oastatus-wcvp-report-1.csv data/ipniname-oastatus-wcvp-report-2.csv data/ipniname-oastatus-wcvp-report-3.csv

all: $(oatrends_charts_year) $(oastatus_charts_year) $(oatrends_charts_publ) $(wcvp_reports)

data_archive_zip:=$(shell basename $(CURDIR))-data.zip
downloads_archive_zip:=$(shell basename $(CURDIR))-downloads.zip

archive: $(oatrends_charts_year) $(oastatus_charts_year) $(oatrends_charts_publ) $(wcvp_reports)
	mkdir -p archive	
	echo "Archived on $(date_formatted)" >> data/archive-info.txt
	zip archive/$(data_archive_zip) data/archive-info.txt data/* -r
	echo "Archived on $(date_formatted)" >> downloads/archive-info.txt
	zip archive/$(downloads_archive_zip) data/archive-info.txt downloads/* -r -x downloads/ipni-coldp-2022-10-15.zip 
	
clean:
	rm -f data/*

touch:
	touch data/ipniname-oastatus.csv

cleancharts:
	rm -f data/*.png

sterilise:
	rm -f data/*
	rm -f downloads/*
