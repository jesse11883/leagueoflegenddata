#!/bin/sh
export DEVHOME=/home/myao/dev/git-jesse/leagueoflegenddata
export USERHOME=/home/seluser

export PYTHONPATH=$DEVHOME/x8lollib

echo $PYTHONPATH



cd $DEVHOME/data_scraper

cd ./dnld_data
rm -rf ./job-1
cd ..
mkdir -p logs
mkdir -p data

scrapy crawl data_scraper -s JOBDIR=dnld_data/job-1  -a cmd=get-users -s cmd=get-users
