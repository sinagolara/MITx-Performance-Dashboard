#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 19 13:33:37 2018

@author: sgolara
"""

# For Python 2.7.10
import requests
import zipfile
import os
try: import simplejson as json
except ImportError: import json
import pandas as pd

# Setting user Parameters



def DLQualtricsSurvey(target_path,apiToken,surveyId,surveyName):
    
    fileFormat = "csv"
    dataCenter = 'co1'
    
    # Setting static parameters
    requestCheckProgress = 0
    progressStatus = "in progress"
    baseUrl = "https://{0}.qualtrics.com/API/v3/responseexports/".format(dataCenter)
    headers = {
        "content-type": "application/json",
        "x-api-token": apiToken,
        }
    
    # Step 1: Creating Data Export
    downloadRequestUrl = baseUrl
    downloadRequestPayload = '{"format":"' + fileFormat + '","surveyId":"' + surveyId + '"}'
    downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers)
    progressId = downloadRequestResponse.json()["result"]["id"]
    #print downloadRequestResponse.text
    
    ## <codecell>
    
    # Step 2: Checking on Data Export Progress and waiting until export is ready
    while requestCheckProgress < 100 and progressStatus is not "complete":
      requestCheckUrl = baseUrl + progressId
      requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
      requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
      print "\tDownload is " + str(requestCheckProgress) + " complete"
    
    
    # Step 3: Downloading file
    requestDownloadUrl = baseUrl + progressId + '/file'
    requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)
    
    # Step 4: Unziping file and remove zip file
    with open("RequestFile.zip", "wb") as f:
        for chunk in requestDownload.iter_content(chunk_size=1024):
            f.write(chunk)
    zipfile.ZipFile("RequestFile.zip").extractall(target_path)
    
    os.remove("RequestFile.zip") 
    #print("RequestFile.zip Removed!") 
    
    
    
    # Step 5: Clean survey data: combine first 2 rows and remove the extra rows.
    survey=pd.read_csv(target_path+surveyName+'.csv')
    col=[]
    for c in survey.columns:
        a=survey.loc[0,c]
        n=a.rfind("-") # find location of the last '-' (first occurence from right)
        a=a[n+1:] # only select what comes after '-'
        if c<>a: col.append(c+' '+a)
        else: col.append(c)
    #print col
    survey.columns=col
    survey.drop([0, 1], inplace=True)
    survey.head()
    survey.to_csv(target_path+surveyName+'.csv', index=False)
    
    print "\tQualtrics Survey Saved at {target_path}{surveyName}.csv".format(target_path=target_path,surveyName=surveyName)
    return True
