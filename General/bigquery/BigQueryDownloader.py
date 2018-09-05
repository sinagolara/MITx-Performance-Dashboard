#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 20:41:50 2018

@author: sgolara

Adds the path for BigQuery user credential to the os environment.
Converts a query to a Pandas dataframe.
Then saves as csv.
If no outfile path provided returns the data frame.

"""

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/sgolara/MITx Data Sets-669606ab3fd5.json"
print "BQ Credentials read from",os.environ['GOOGLE_APPLICATION_CREDENTIALS']

from google.cloud import bigquery

# <codecell>
def BQDL(query,outfile_path=""):
    # Submit the query and read data
    query
    client = bigquery.Client()
    query_job = client.query(query)
    results = query_job.result()  # Waits for job to complete.
    df=results.to_dataframe()
    
    if outfile_path<>"":
        df.to_csv(outfile_path,index=False, encoding='utf8')
        return True
    else:
        return df


# <codecell>

