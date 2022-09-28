year_min = 2012
year_max = 2021
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
	$(python_launch_cmd) getipninames.py --year_min $(year_min) --year_max $(year_max) $@

getnames: downloads/ipninames.csv

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
# Report on OA status over time
data/ipniname-oastatus-report.csv: reportoastatus.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
reportoa: data/ipniname-oastatus-report.csv
###############################################################################

###############################################################################
#  Plot OA takeup over time
data/ipni-oatrend.png: plotoa.py data/ipniname-oastatus-report.csv
	$(python_launch_cmd) $^ $(limit_args) $@
data/ipni-oatrendpc.png: plotoa.py data/ipniname-oastatus-report.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage $@
# Shorthand:
plotoa: data/ipni-oatrend.png data/ipni-oatrendpc.png
###############################################################################

###############################################################################
#  Plot OA status over time
data/ipni-oastatustrend.png: plotoastatus.py data/ipniname-oastatus-report.csv
	$(python_launch_cmd) $^ $(limit_args) $@
data/ipni-oastatustrendpc.png: plotoastatus.py data/ipniname-oastatus-report.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage $@
# Shorthand:
plotoastatus: data/ipni-oastatustrend.png data/ipni-oastatustrendpc.png
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
#  Plot OA takeup by WCVP dist - all nomenclatural acts percent
data/oatrend-dist-%-pc.png: plotoadist.py data/ipniname-oastatus-wcvp-report-%.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage --tdwg_wgsrpd_level=$* $@
# Shorthand:
plotoa_level1_pc: data/oatrend-dist-1-pc.png
plotoa_level2_pc: data/oatrend-dist-2-pc.png
plotoa_level3_pc: data/oatrend-dist-3-pc.png
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

###############################################################################
#  Plot OA takeup by WCVP dist - tax novs only percent
data/oatrend-dist-%-taxnov-pc.png: plotoadist.py data/ipniname-oastatus-wcvp-report-%-taxnov.csv
	$(python_launch_cmd) $^ $(limit_args)  --plot-percentage --tax_novs_only --tdwg_wgsrpd_level=$* $@
# Shorthand:
plotoa_level1_taxnov_pc: data/oatrend-dist-1-taxnov-pc.png
plotoa_level2_taxnov_pc: data/oatrend-dist-2-taxnov-pc.png
plotoa_level3_taxnov_pc: data/oatrend-dist-3-taxnov-pc.png
###############################################################################

oatrends_charts:=data/ipni-oatrend.png data/ipni-oastatustrend.png
oatrends_pc_charts:=data/ipni-oatrendpc.png data/ipni-oastatustrendpc.png
dist1_charts:=data/oatrend-dist-1.png data/oatrend-dist-1-taxnov.png
dist1_pc_charts:=data/oatrend-dist-1-pc.png data/oatrend-dist-1-taxnov-pc.png
dist2_charts:=data/oatrend-dist-2.png data/oatrend-dist-2-taxnov.png
dist2_pc_charts:=data/oatrend-dist-2-pc.png data/oatrend-dist-2-taxnov-pc.png
dist3_charts:=data/oatrend-dist-3.png data/oatrend-dist-3-taxnov.png
dist3_pc_charts:=data/oatrend-dist-3-pc.png data/oatrend-dist-3-taxnov-pc.png

all: $(oatrends_charts) $(oatrends_pc_charts) $(dist1_charts) $(dist1_pc_charts) $(dist2_charts) $(dist2_pc_charts) $(dist3_charts) $(dist3_pc_charts)

data_archive_zip:=$(shell basename $(CURDIR))-data.zip
downloads_archive_zip:=$(shell basename $(CURDIR))-downloads.zip

archive: $(oatrends_charts) $(oatrends_pc_charts) $(dist1_charts) $(dist1_pc_charts) $(dist2_charts) $(dist2_pc_charts) $(dist3_charts) $(dist3_pc_charts)
	mkdir -p archive	
	echo "Archived on $(date_formatted)" >> data/archive-info.txt
	zip archive/$(data_archive_zip) data/archive-info.txt data/* -r
	echo "Archived on $(date_formatted)" >> downloads/archive-info.txt
	zip archive/$(downloads_archive_zip) data/archive-info.txt downloads/* -r
	
clean:
	rm -f data/*

cleancharts:
	rm -f data/*.png

sterilise:
	rm -f data/*
	rm -f downloads/*
