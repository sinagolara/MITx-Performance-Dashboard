#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 17:00:33 2018

@author: sgolara

"""

import os,sys
#from selenium import webdriver
#from time import sleep,time
#from functools import partial
from bigquery.BigQueryDownloader import BQDL
from edx_crawler.crawler import crawl_edx
from qualtrics.qualtrics_api import DLQualtricsSurvey
from data_cleaner.data_cleaner import archive_old_grade_reports,generate_latest_grades
import datetime

from settings import *

sys.path.append("/Users/sgolara/Dropbox (MIT)/Reporting Automation/MM_Data/General" ) #for test


# <codecell>
# A. Folder structure
print '\n*** A- Start.', datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

ParDir="/Users/sgolara/Dropbox (MIT)/Reporting Automation/"

wd=os.path.abspath(os.path.dirname(sys.argv[0]))
if wd=='/Users/sgolara':   #for test
    wd="/Users/sgolara/Dropbox (MIT)/Reporting Automation/MM_Data/General"
print 'Working directory set',wd


root_name="MM_Data"
general_dir="General"
root_dir=wd.split(general_dir)[0]
par_dir=wd.split(root_name)[0]

#add chrome driver address to path
sys.path.append("/Users/sgolara/Dropbox (MIT)/Reporting Automation/MM_Data/General/edx_crawler" )

# do a pre-clean on grades
for course_name in courses:
    archive_old_grade_reports(root_dir+course_name+'/')
    generate_latest_grades(root_dir+course_name+'/')

# <codecell>
# B. read settings


print 'courses:',courses

for course_name in courses:
    if not os.path.exists(root_dir+course_name):
        os.makedirs(root_dir+course_name)
        print "folder {c} created.".format(c=course_name)
    if not os.path.exists(root_dir+course_name+'/Old Grade Reports'):
        os.makedirs(root_dir+course_name+'/Old Grade Reports')
        print "folder 'Old Grade Reports' created for {c}.".format(c=course_name)

print '\n*** B- Settings Read.', datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# <codecell>
# C1- Data Download: Forum -  Download forum activity data from Big Query

print 'C1- Downloading BQ Data.', datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

if 'forum' in reports:
    query_path=wd+'/bigquery/Forum Threads Query.txt'

    for course_name in courses:
        print "downloading BQ data for {name}".format(name=course_name)
        query=open(query_path,'r').read().replace("SC1x__2T2018",course_name)
        outfile_path=root_dir+course_name+'/Forum Threads.csv'
        BQDL(query,outfile_path)

print '\n*** C1- BQ Download Complete.', datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
# <codecell>
# C2- Data Download: edX Reports
edXreports=[]
if 'grades' in reports: edXreports.append('grades')
if 'enrollment' in reports: edXreports.append('enrollment')

if len(edXreports)>0:
    for course_name in courses:
        print "crawling edX platform for {name}".format(name=course_name)
        download_dir=root_dir+course_name+'/'

        if sys.platform=="Darwin": driver_path=wd+'/edx_crawler/chromedriver_mac'
        else: driver_path=wd+'/edx_crawler/chromedriver_linux'

        crawl_edx(course_name,download_dir=download_dir, driver_path=driver_path , edXreports=edXreports)

        if 'grades' in reports:
            archive_old_grade_reports(download_dir)
            generate_latest_grades(download_dir)

print '\n*** C2- EdX Crawling Complete.', datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# <codecell>
# C3- Data Download: Qualtrics Surveys
apiToken=qualtrics1['apiToken']
surveys=qualtrics1['surveys']
target_path=root_dir+'SC1x__2T2018/'

for surveyName in surveys.keys():
    surveyId=surveys[surveyName]
    print surveyName,surveyId
    print "Downloading feedback survey {surveyName}".format(surveyName=surveyName)
    DLQualtricsSurvey(target_path,apiToken,surveyId,surveyName)

print '\n*** C3- Qualtrics Download Complete.', datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# <codecell>
