#!/bin/bash

. ./scripts/setup_dvc.sh

dvc pull data/01_raw/all_contents.dvc --remote all_contents
dvc pull data/01_raw/missing_contents.dvc --remote missing_contents
dvc pull data/01_raw/google_analytics.xlsx.dvc --remote google_analytics
