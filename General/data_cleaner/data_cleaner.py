#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 10:25:17 2018

@author: sgolara
"""

import pandas as pd
import os


def archive_old_grade_reports(download_dir):

    print "\tarchiving grade reports in {download_dir}".format(download_dir=download_dir)

    files = []
    for (dirpath, dirnames, filenames) in os.walk(download_dir):
        files.extend(filenames)
        break
    grade_reports=[f for f in files if ".csv" in f and "grade_report" in f ]
    grade_reports.sort()

    for f in grade_reports[:-1]:
        os.rename(download_dir+f, download_dir+"Old Grade Reports/"+f)
        print '\t{f} moved to Old Grade Reports folder'.format(f=f)


def generate_latest_grades(download_dir):

    print "\tcleaning grade reports in {download_dir}".format(download_dir=download_dir)

    files = []
    for (dirpath, dirnames, filenames) in os.walk(download_dir):
        files.extend(filenames)
        break
    grade_reports=[f for f in files if ".csv" in f and "grade_report" in f ]
    grade_reports.sort()
    latest_report=grade_reports[-1]

    latest_df=pd.read_csv(download_dir+latest_report)
    latest_df.head()

    special_path=download_dir+'Special Learner Groups.csv'
    if os.path.exists(special_path):
        special= pd.read_csv(special_path)[['Student ID', 'Special Group']]
        special.head()

        latest_df=pd.merge(latest_df, special, how='left', on='Student ID',suffixes=('', '_2'))


    latest_df.to_csv(download_dir+'Latest_Grades.csv', index=False)
    print '\tLatest_Grades.csv generated based on {latest_report} and '.format(latest_report=latest_report)
