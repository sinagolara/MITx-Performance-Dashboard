#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 17:52:26 2018

@author: sgolara
"""

import os

from selenium import webdriver
from time import sleep,time
from functools import partial


# <codecell>


def wait_for(condition_function, timeout=10):
    start_time = time()
    while time() < start_time + timeout:
        if condition_function():
            return True
        else:
             sleep(.5)
    raise Exception(
        '\tTimeout waiting for {}'.format(condition_function.__name__)
    )


def wait_for_refresh(driver, condition_function, timeout=10000, interval=5):
    start_time = time()

    while time() < start_time + timeout:
        driver.refresh()
        sleep(2)
        if condition_function():
            return True
        else:
            print '\twaiting for',interval,'sec.'
            sleep(interval)
    raise Exception(
        '\tTimeout waiting for {}'.format(condition_function.__name__)
    )

class wait_for_page_load(object):

    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)

def no_pending_tasks_message(driver):
    try:
        print driver.find_element_by_xpath('''//div[@class="no-pending-tasks-message" and @style="display: block;"]''').text
        return True
    except:
        return False

def pending_tasks_message(driver):
    try:
        print driver.find_element_by_xpath('''//div[@class="no-pending-tasks-message" and @style="display: none;"]''').text
        return True
    except:
        return False

def request_submitted_message(driver):
    try:
        print driver.find_element_by_xpath('''//*[@id="report-request-response"]''').text
        return True
    except:
        return False

# <codecell>

def crawl_edx(course_name,download_dir,driver_path,edXreports=['enrollment','grades']):

    course_name2=course_name.replace("__","+")
    course_name3=course_name.replace("__","-")
    ## launch chrome
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : download_dir} #set default download directory
    chromeOptions.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(executable_path=driver_path,chrome_options=chromeOptions)


    ## login
    driver.get("https://courses.edx.org/login")
    driver.find_element_by_id("login-email").send_keys("MIT.SCM.MicroMastersTeam@gmail.com")
    driver.find_element_by_id("login-password").send_keys("****")
    with wait_for_page_load(driver): driver.find_element_by_xpath('''//*[@id="login"]/button''').click()   # click login button



    ## Download Enrollment Data (if requested)
    if 'enrollment' in edXreports:
        fname='MITx-CTL.{name}--enrollment.csv'.format(name=course_name3)
        if os.path.isfile(download_dir+fname):
            os.remove(download_dir+fname)
            print 'old',fname,'removed'


        url="https://insights.edx.org/courses/course-v1:MITx+CTL.{name}/enrollment/activity/".format(name=course_name2)      # go to the insights page
        driver.get(url)
        sleep(5)
        dl_button=driver.find_element_by_xpath('''//a[@href="/courses/course-v1:MITx+CTL.{name}/csv/enrollment/" and @class="btn btn-default"]'''.format(name=course_name2))
        dl_button.click()
        print '\tEnrollment data saved @', download_dir


    ## Download Grades Data (if requested)
    if 'grades' in edXreports:
        driver.get("https://courses.edx.org/courses/course-v1:MITx+CTL.{name}/instructor#view-data_download".format(name=course_name2)) # go to data downloades page

        # wait until "no pending tasks" appears
        sleep(2)
        wait_for_refresh(driver,partial(no_pending_tasks_message,driver),interval=60)
        print '\tno pending tasks'
        sleep(2)

        # store old report links
        link_elements_old=driver.find_elements_by_xpath('''//div[@class="slick-cell l0 r0 file-download-link"]''') # find the links area
        links_old=[link.text for link in link_elements_old]
        #print '{n} links found'.format(n=len(link_elements_old))



        if len(link_elements_old)<1:
            sleep(3)
            link_elements_old=driver.find_elements_by_xpath('''//div[@class="slick-cell l0 r0 file-download-link"]''')
            links_old=[link.text for link in link_elements_old]
        #print len(link_elements_old)

        # Click on download button
        button_name="Generate Grade Report"
        driver.find_element_by_xpath(u"//*[@value='"+button_name+"']").click()
        print '\t',button_name,'clicked'

        wait_for_refresh(driver,partial(pending_tasks_message,driver),interval=10)
        print '\tpending_tasks table appears'

        wait_for_refresh(driver,partial(no_pending_tasks_message,driver), interval=60)
        print '\treport ready'

        driver.refresh()

        while True:
            sleep(3)
            link_elements_new=driver.find_elements_by_xpath('''//div[@class="slick-cell l0 r0 file-download-link"]''')
            links_new=[link.text for link in link_elements_new]
            if len(link_elements_new)>0: break

        # Make sure a new link is created; then, save
        if links_new[0]<>links_old[0]:
            file_name=links_new[0]
            driver.find_element_by_link_text(file_name).click()
            print '\t',file_name,"saved @", download_dir
        else:
            print '\tWarning: new link is the same!!!'


    sleep(2)
    driver.quit()
        # wait to see the pending message
