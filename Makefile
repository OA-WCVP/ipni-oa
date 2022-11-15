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
# Report on OA status by selected family (pro)
data/ipniname-oastatus-report-fam-pro.csv: reportoastatus.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) --group family --filtergroupvalues Poaceae,Solanaceae,Fabaceae $@
# Shorthand:
reportoafampro: data/ipniname-oastatus-report-fam-pro.csv
###############################################################################

###############################################################################
# Report on OA status by selected family (hort)
data/ipniname-oastatus-report-fam-hort.csv: reportoastatus.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) --group family --filtergroupvalues Cactaceae,Orchidaceae,Bromeliaceae $@
# Shorthand:
reportoafamhort: data/ipniname-oastatus-report-fam-hort.csv
###############################################################################

###############################################################################
#  Plot OA takeup over time
data/ipni-oatrend-year.png: plotoa.py data/ipniname-oastatus-report-year.csv
	$(python_launch_cmd) $^ $(limit_args) $@
data/ipni-oatrendpc-year.png: plotoa.py data/ipniname-oastatus-report-year.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage $@
# Shorthand:
plotoayear: data/ipni-oatrend-year.png data/ipni-oatrendpc-year.png
###############################################################################

###############################################################################
#  Plot OA takeup by publ
data/ipni-oatrend-publ.png: plotoa.py data/ipniname-oastatus-report-publ.csv
	$(python_launch_cmd) $^ $(limit_args) --group publication --logy $@
data/ipni-oatrendpc-publ.png: plotoa.py data/ipniname-oastatus-report-publ.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage --group publication $@
# Shorthand:
plotoapubl: data/ipni-oatrend-publ.png data/ipni-oatrendpc-publ.png
###############################################################################

###############################################################################
#  Plot OA takeup by family (pro)
data/ipni-oatrend-fam-pro.png: plotoa.py data/ipniname-oastatus-report-fam-pro.csv
	$(python_launch_cmd) $^ $(limit_args) --group family $@
data/ipni-oatrendpc-fam-pro.png: plotoa.py data/ipniname-oastatus-report-fam-pro.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage --group family $@
# Shorthand:
plotoafampro: data/ipni-oatrend-fam-pro.png data/ipni-oatrendpc-fam-pro.png
###############################################################################

###############################################################################
#  Plot OA takeup by family (hort)
data/ipni-oatrend-fam-hort.png: plotoa.py data/ipniname-oastatus-report-fam-hort.csv
	$(python_launch_cmd) $^ $(limit_args) --group family $@
data/ipni-oatrendpc-fam-hort.png: plotoa.py data/ipniname-oastatus-report-fam-hort.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage --group family $@
# Shorthand:
plotoafamhort: data/ipni-oatrend-fam-hort.png data/ipni-oatrendpc-fam-hort.png
###############################################################################

###############################################################################
#  Plot OA status over time
data/ipni-oastatustrend.png: plotoastatus.py data/ipniname-oastatus-report-year.csv
	$(python_launch_cmd) $^ $(limit_args) $@
data/ipni-oastatustrendpc.png: plotoastatus.py data/ipniname-oastatus-report-year.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage --removena $@
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
data/ipni-oatrend-dist-%.png: plotoadist.py data/ipniname-oastatus-wcvp-report-%.csv
	$(python_launch_cmd) $^ $(limit_args) --tdwg_wgsrpd_level=$* $@
# Shorthand:
plotoa_level1: data/ipni-oatrend-dist-1.png
plotoa_level2: data/ipni-oatrend-dist-2.png
plotoa_level3: data/ipni-oatrend-dist-3.png
###############################################################################

###############################################################################
#  Plot OA takeup by WCVP dist - all nomenclatural acts percent
data/ipni-oatrend-dist-%-pc.png: plotoadist.py data/ipniname-oastatus-wcvp-report-%.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage --tdwg_wgsrpd_level=$* $@
# Shorthand:
plotoa_level1_pc: data/ipni-oatrend-dist-1-pc.png
plotoa_level2_pc: data/ipni-oatrend-dist-2-pc.png
plotoa_level3_pc: data/ipni-oatrend-dist-3-pc.png
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
data/ipni-oatrend-dist-%-taxnov.png: plotoadist.py data/ipniname-oastatus-wcvp-report-%-taxnov.csv
	$(python_launch_cmd) $^ $(limit_args)  --tax_novs_only --tdwg_wgsrpd_level=$* $@
# Shorthand:
plotoa_level1_taxnov: data/ipni-oatrend-dist-1-taxnov.png
plotoa_level2_taxnov: data/ipni-oatrend-dist-2-taxnov.png
plotoa_level3_taxnov: data/ipni-oatrend-dist-3-taxnov.png
###############################################################################data/ipni-oatrend

###############################################################################
#  Plot OA takeup by WCVP dist - tax novs only percent
data/ipni-oatrend-dist-%-taxnov-pc.png: plotoadist.py data/ipniname-oastatus-wcvp-report-%-taxnov.csv
	$(python_launch_cmd) $^ $(limit_args)  --plot-percentage --tax_novs_only --tdwg_wgsrpd_level=$* $@
# Shorthand:
plotoa_level1_taxnov_pc: data/ipni-oatrend-dist-1-taxnov-pc.png
plotoa_level2_taxnov_pc: data/ipni-oatrend-dist-2-taxnov-pc.png
plotoa_level3_taxnov_pc: data/ipni-oatrend-dist-3-taxnov-pc.png
###############################################################################

##
###############################################################################
# Report on publication types over time
data/ipniname-publtype-report.csv: reportpubltype.py data/ipniname-oastatus.csv
	$(python_launch_cmd) $^ $(limit_args) $@
# Shorthand:
reportpubltype: data/ipniname-publtype-report.csv
###############################################################################

###############################################################################
#  Plot OA takeup over time
data/ipni-publtype.png: plotpubltype.py data/ipniname-publtype-report.csv
	$(python_launch_cmd) $^ $(limit_args) $@
data/ipni-publtypepc.png: plotpubltype.py data/ipniname-publtype-report.csv
	$(python_launch_cmd) $^ $(limit_args) --plot-percentage $@
# Shorthand:
plotpubltype: data/ipni-publtype.png data/ipni-publtypepc.png
###############################################################################
##

oatrends_charts_year:=data/ipni-oatrend-year.png data/ipni-oatrendpc-year.png 
oatrends_charts_publ:=data/ipni-oatrend-publ.png data/ipni-oatrendpc-publ.png 
oatrends_charts_fam_pro:=data/ipni-oatrend-fam-pro.png data/ipni-oatrendpc-fam-pro.png 
oatrends_charts_fam_hort:=data/ipni-oatrend-fam-hort.png data/ipni-oatrendpc-fam-hort.png 
oastatus_charts_year:= data/ipni-oastatustrend.png data/ipni-oastatustrendpc.png

publtype_charts:=data/ipni-publtype.png
publtype_pc_charts:=data/ipni-publtypepc.png
dist1_charts:=data/ipni-oatrend-dist-1.png data/ipni-oatrend-dist-1-taxnov.png
dist1_pc_charts:=data/ipni-oatrend-dist-1-pc.png data/ipni-oatrend-dist-1-taxnov-pc.png
dist2_charts:=data/ipni-oatrend-dist-2.png data/ipni-oatrend-dist-2-taxnov.png
dist2_pc_charts:=data/ipni-oatrend-dist-2-pc.png data/ipni-oatrend-dist-2-taxnov-pc.png
dist3_charts:=data/ipni-oatrend-dist-3.png data/ipni-oatrend-dist-3-taxnov.png
dist3_pc_charts:=data/ipni-oatrend-dist-3-pc.png data/ipni-oatrend-dist-3-taxnov-pc.png

all: $(oatrends_charts_year) $(oatrends_charts_publ) $(oatrends_charts_fam_pro) $(oatrends_charts_fam_hort) $(oastatus_charts_year) $(dist1_charts) $(dist1_pc_charts) $(dist2_charts) $(dist2_pc_charts) $(dist3_charts) $(dist3_pc_charts) $(publtype_charts) $(publtype_pc_charts)

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

touch:
	touch data/ipniname-oastatus.csv

cleancharts:
	rm -f data/*.png

sterilise:
	rm -f data/*
	rm -f downloads/*
