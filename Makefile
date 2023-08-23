year_min = 2012
year_max = 2021
wcvp_zip_url=http://sftp.kew.org/pub/data-repositories/WCVP/Special_Issue_28_Feb_2022/wcvp_names_and_distribution_special_issue_28_feb_2022.zip
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

downloads/wcvp.zip:
	mkdir -p downloads
	wget -O $@ $(wcvp_zip_url)

downloads/wcvp_names.txt: downloads/wcvp.zip
	unzip -p $^  wcvp_names.txt >$@

downloads/wcvp_distribution.txt: downloads/wcvp.zip
	unzip -p $^  wcvp_distribution.txt >$@

downloads/ipninames.csv: getipninames.py data/ipni-coldp-dois.tsv
	mkdir -p downloads
	$(python_launch_cmd) $^ --year_min $(year_min) --year_max $(year_max) $@
getnames: downloads/ipninames.csv

downloads/ipni-coldp-2022-10-15.zip:
	mkdir -p downloads
	wget -O $@ $(ipni_coldp_url)

downloads/rdmpage-ipni-coldp-8fe9cb4/names.tsv: downloads/ipni-coldp-2022-10-15.zip
	mkdir -p downloads/rdmpage-ipni-coldp-8fe9cb4
	unzip -p $^  rdmpage-ipni-coldp-8fe9cb4/names.tsv >$@

downloads/rdmpage-ipni-coldp-8fe9cb4/references.tsv: downloads/ipni-coldp-2022-10-15.zip
	unzip -p $^  rdmpage-ipni-coldp-8fe9cb4/references.tsv >$@

data/ipni-coldp-dois.tsv: backfilldois.py downloads/rdmpage-ipni-coldp-8fe9cb4/names.tsv downloads/rdmpage-ipni-coldp-8fe9cb4/references.tsv
	mkdir -p data
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
# Extract publication details from IPNI name dataset
data/ipnipubls.csv: ipninames2publs.py data/ipniname-oastatus.csv
	mkdir -p data
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
getipnipubls: data/ipnipubls.csv
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

data/ipniname-oastatus-wcvp.txt: addwcvp.py data/ipniname-oastatus.csv downloads/wcvp_names.txt downloads/wcvp_distribution.txt
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
	$(python_launch_cmd) $^ $(limit_args) --group linkedPublication.id $@
# Shorthand:
reportoapubl: data/ipniname-oastatus-report-publ.csv
###############################################################################

###############################################################################
# Report on OA status by publ - selected years
# 2019-2021
data/ipniname-oastatus-report-publ-2019-2021.csv: reportoastatus.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) --yearmin=2019 --yearmax=2021 --group linkedPublication.id $@

reportoapubl201921: data/ipniname-oastatus-report-publ-2019-2021.csv

# 2019
data/ipniname-oastatus-report-publ-2019.csv: reportoastatus.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) --yearmin=2019 --yearmax=2019 --group linkedPublication.id $@

reportoapubl2019: data/ipniname-oastatus-report-publ-2019.csv
###############################################################################

data/ipni-oa-composite.png: plotoastatus.py data/ipniname-oastatus-report-year.csv
	$(python_launch_cmd) $^ $(limit_args) --plottype=composite --plot_percentage_subplot_2 $@

###############################################################################
#  Plot OA takeup by publ
data/ipni-oatrend-publ-all.png data/ipni-oatrend-publ-all.txt: plotpubl.py data/ipniname-oastatus-report-publ.csv data/oastatus2doaj.csv data/ipnipubls.csv 
	$(python_launch_cmd) $^ $(limit_args) $(basename $@).png $(basename $@).txt
# Shorthand:
plotoapubl: data/ipni-oatrend-publ-all.png
###############################################################################

###############################################################################
#  Plot OA takeup by publ - selected years

# 2019-21
data/ipni-oatrend-publ-2019-2021.png data/ipni-oatrend-publ-2019-2021.txt: plotpubl.py data/ipniname-oastatus-report-publ-2019-2021.csv  data/oastatus2doaj.csv data/ipnipubls.csv 
	$(python_launch_cmd) $^ $(limit_args) --yearmin=2019 --yearmax=2021 $(basename $@).png $(basename $@).txt
# Shorthand:
plotoapublyr201920: data/ipni-oatrend-publ-2019-2021.png

# 2019 only
data/ipni-oatrend-publ-2019.png data/ipni-oatrend-publ-2019.txt: plotpubl.py data/ipniname-oastatus-report-publ-2019.csv  data/oastatus2doaj.csv data/ipnipubls.csv 
	$(python_launch_cmd) $^ $(limit_args) --yearmin=2019 --yearmax=2019 $(basename $@).png $(basename $@).txt
# Shorthand:
plotoapublyr2019: data/ipni-oatrend-publ-2019.png

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

# Build SI table
data/si-table-publ-%.md: buildpublsitable.py data/ipni-oatrend-publ-%.txt resources/publication-urls.txt
	$(python_launch_cmd) $^ $(limit_args) --daterange=$* $@
buildpublsitable: data/si-table-publ-all.md
###############################################################################

# Build YAML
data/article-variables.yaml: ipninameoastatus2yaml.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $@
buildyaml: data/article-variables.yaml
###############################################################################

oa_charts_year:=data/ipni-oa-composite.png
oatrends_charts_publ:=data/ipni-oatrend-publ-all.png data/ipni-oatrend-publ-2019-2021.png data/ipni-oatrend-publ-2019.png

wcvp_reports:= data/ipniname-oastatus-wcvp-report-1.csv data/ipniname-oastatus-wcvp-report-2.csv data/ipniname-oastatus-wcvp-report-3.csv

si_tables:= data/si-table-publ-all.md data/si-table-publ-2019.md data/si-table-publ-2019-2021.md

yaml:= data/article-variables.yaml
all: $(oa_charts_year) $(oatrends_charts_publ) $(wcvp_reports) $(si_tables) $(yaml)

data_archive_zip:=$(shell basename $(CURDIR))-data.zip
downloads_archive_zip:=$(shell basename $(CURDIR))-downloads.zip

archive: $(oa_charts_year) $(oatrends_charts_publ) $(wcvp_reports) $(si_tables) $(yaml)
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
