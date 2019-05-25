import os
import sys
import os.path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import datetime
import time
import json
import string

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

date = time.strftime('%Y%m%d',time.localtime(time.time()))
groupname = os.environ['groupname']

def directoryexist(directory):
    # create folder
    # directory = userid
    if not os.path.exists(directory):
        os.makedirs(directory)
    directoryIsExist = True
    return directoryIsExist

def savepage(type, userid):
    directory = userid.rstrip('\n')
    # checking directory
    directoryexist('dataset/'+date+'_'+groupname)
    directoryexist('dataset/'+date+'_'+groupname+'/'+directory)
    page_html = driver.page_source
    page_html_file = open('dataset/'+date+'_'+groupname+'/'+directory+'/'+type+'_'+userid+'.html', 'w')
    page_html_file.write(page_html)
    page_html_file.close()

def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def scrollLikePage(current_url, userid):
    # scroll until got 100 top-likes
    if 'profile.php?id=' in current_url:
        likes_url = current_url+'&sk=likes'
    else:
        likes_url = current_url+'/likes'
    driver.get(likes_url)
    time.sleep(1)
    current_url_after_redirect = driver.current_url

    if current_url_after_redirect == likes_url :
        background = driver.find_element_by_css_selector("body")
        for i in range(1, 20):
            time.sleep(0.7)
            background.send_keys(Keys.SPACE)
    savepage('likes', userid)

def scrollTimelinePage(current_url, userid):
    background = driver.find_element_by_css_selector("body")
    # Prevent invalid page.
    try:
        driver.find_element_by_id('fb-timeline-cover-name')
    except Exception as err:
        # save these URLs
        rlog('timeline','invalid page : %s ' %(err), userid)

    try:
        stop = False
        startTag = 0
        sleeptime = 3
        yearlimit = int(os.environ['yearLimit'])

        while (stop == False):
            # auto scrolling by space keypress
            background.send_keys(Keys.SPACE)
            time.sleep(sleeptime)

            # to find elements (date of the post) from its class -> hasilnya array
            tag = driver.find_elements_by_css_selector('._5ptz')
            for x in range(startTag, tag.__len__()):
                # get datetime of the latest post
                postDate = (tag[x].get_attribute("title")).split(",")[0]
                postYear = int(postDate.split("/")[2])+2000
                print("post on date ", postDate)
                if yearlimit <= postYear:
                    stop = False
                else:
                    stop = True
                startTag = x+1
        savepage('timeline', userid)
    except Exception as err:
        rlog('timeline','keterangan timeout : %s' %(err), userid)

def scrollAboutPage(current_url, userid):
    # browse ABOUT page
    if 'profile.php?id=' in current_url:
        username = current_url.split('=')[1].split('&')[0]
        about_url = 'https://m.facebook.com/profile.php?id='+username+'&sk=about'
    else:
        username = current_url.split('/')[3]
        about_url = 'https://m.facebook.com/'+username+'/about'
    # open page based on url
    driver.get(about_url)
    # save webpage
    savepage("about", userid)

def rlog(type, status, userid):
    # Record the start time.
    starttime = datetime.datetime.now()
    filename = "log_"+date+".txt"
    teks = "%s,%s,%s,%s \n" % (type, status, starttime, userid)

    # harus ada pengecekan fileexist atau ga
    directoryexist("log")
    isExist = os.path.isfile(filename)
    if isExist == True :
        # kalo file exist
        file = open('log/'+filename, "a")
    else :
        # kalo file not exist
        file = open('log/'+filename, "w+")
    file.write(teks)
    file.close()
    return True

if __name__ == '__main__':
    urls = (os.environ['userids']).split(",")

    baseurl = 'https://www.facebook.com/'

    # driver init
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications") 
    driver = webdriver.Chrome("./browser/chromedriver", options= options)
    # Set the timeout for the driver and socket.

    # First, login.
    driver.get("https://www.facebook.com/login.php")
    driver.find_element_by_id("email").clear()
    driver.find_element_by_id("email").send_keys(os.environ['email'])
    driver.find_element_by_id("pass").clear()
    driver.find_element_by_id("pass").send_keys(os.environ['password'])
    driver.find_element_by_id("loginbutton").click()

    # Maybe the login failed. It may turn to the login page again.
    # you may need to load again.
    if 'login' in driver.current_url:
        driver.close()

    # visit the url based on urls
    userid = 0
    for useridraw in urls:
        time.sleep(1)
        userid = useridraw.rstrip('\n')
        url = baseurl+userid

        print (time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time())))

        driver.get(url)
        current_url = driver.current_url

        try:
            scrollTimelinePage(current_url, userid)
            rlog('timeline','success', userid)
        except Exception as err:
            rlog('timeline','failed : %s' %(err), userid)

        try:
            scrollLikePage(current_url, userid)
            rlog('like','success', userid)
        except Exception as err:
            rlog('like','failed : %s' %(err), userid)
            
        try:
            scrollAboutPage(current_url, userid)
            rlog('about','success', userid)
        except Exception as err:
            rlog('about','failed : %s' %(err), userid)
            continue
