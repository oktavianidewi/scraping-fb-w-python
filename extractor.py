# -*- coding: utf-8 -*-
import os
import nltk
from bs4 import BeautifulSoup
import json
import re
import time
import datetime

def xtract_timeline():
    res = {}
    post_num = 0

    # Get the user url.
    try:
        url = soup.find(id = 'fb-timeline-cover-name').find_parent("a")["href"]
    except Exception as err:
        url = str(err).replace("'", "")
    
    # First we get the full name of the target.
    # Some posts in the timeline are not posted by the target user some we should get the name of the target to distinguish the posts.
    if soup.find(id = 'fb-timeline-cover-name'):
        user_name = soup.find(id = 'fb-timeline-cover-name').text
        print("username ", user_name)
    else:
        # cannot find the target means this page is not available.
        print ("Sorry, this page isn't available.\n")
        # continue
        pass

    the_post_head = []
    # We get all the posts.
    the_posts = soup.find_all('div', attrs={'class':'_5pcr userContentWrapper'})
    print("lebar posts ", the_posts.__len__())
    


    # Analyse each post.
    for the_posts_num in range(the_posts.__len__()):
        # each post
        the_post_head = the_posts[the_posts_num]

        # list for the information of the post
        the_post_list = []

        # username
        the_post_list.append(user_name)

        # number of the post.
        post_num += 1
        the_post_list.append(post_num)

        # post content
        posts = the_post_head.find('div', attrs={'class':'_5pbx userContent _3576'})
        if (posts != None) :
            desc = posts.text
        else:
            image = the_post_head.find('div', attrs={'class':'mtm'})
            if ( image.img.has_attr('alt') ) :
                desc = image.img['alt']
            else : 
                desc = "No alt image available"
        the_post_head_title_text = desc
        the_post_list.append(the_post_head_title_text)

        # post is shared by other or self
        the_post_head_title = the_post_head.find('span', attrs={'class': 'fwn fcg'})
        the_post_head_title_selforother = "self"
        the_post_head_title_names = the_post_head_title.find_all('a')
        if the_post_head_title_names[0].text not in user_name:
            the_post_head_title_selforother = "other"
        for the_post_head_title_name in the_post_head_title_names:
            the_post_head_title_text = the_post_head_title_text.replace(the_post_head_title_name.text, '')
        if the_post_head_title_text == "":
            the_post_head_title_text = "~"
        the_post_list.append(the_post_head_title_selforother)

        # posting time
        the_post_head_time = the_post_head.find('abbr', attrs={'class': '_5ptz'})
        try:
            the_post_head_time_text = str(the_post_head_time['title'])
        except Exception as err:
            the_post_head_time_text = str(err).replace("'", "")

        # weekday or weekend
        [mm, dd, yy] = (the_post_head_time_text.split(",")[0]).split("/")
        yyyy = int(yy) + 2000
        dayOfTheWeek = datetime.datetime(yyyy, int(mm), int(dd)).weekday()
        the_post_head_time_week = "Weekend" if (dayOfTheWeek == 0 or dayOfTheWeek == 6) else "Weekday" 
        the_post_list.append(the_post_head_time_week)

        # reactions count
        reactions = the_post_head.find('span', attrs={'class':'_3dlh _3dli'})
        if reactions != None :
            regexComment = re.findall("\d+", reactions.text)
            the_post_comment_likes_count = int(regexComment[0]) + 2 if (len(regexComment) > 0) else 1
        else : 
            the_post_comment_likes_count = 0
        the_post_list.append(the_post_comment_likes_count)

        # merge all
        all_post_list.append(the_post_list)

    return all_post_list

def writeToJsonFile(data, jsonfile):
    with open('extracted/'+jsonfile, 'w') as file:
        file.write( json.dumps(data) )
        file.close()
    return True

if __name__ == '__main__':
    def with_id(tag):
        return tag.has_attr('id')

    def with_class(tag):
        return tag.has_attr('class')

    directoryGroup = os.environ['directoryGroup']
    print (directoryGroup)
    user_num = 0
    infoperuser = {}
    alluserinfo = []

    for root, dirs, files in os.walk(directoryGroup):

        # save the all posts
        all_post_list = []
        # Browse the html files
        all = {}
        file = {}
        for dir in dirs:
            file[''+dir+''] = {}
            file['a'] = {}

        for name in files:
            if name != '.DS_Store':

                # post number for every user
                post_num = 0

                # read the file
                file_path_raw = root + '/' + name
                file_path = file_path_raw.replace('\\', '/')
                user_file = open(file_path, 'r')
                user_lines = user_file.read()

                soup = BeautifulSoup(user_lines, "html.parser")
                file['group'] = os.environ['groupNameRow']

                if 'timeline' in file_path:
                    # extract timeline
                    print("extract timeline")
                    timelineres = xtract_timeline()
                    file['timeline'] = timelineres

            userid = str(name.rstrip('.html').lstrip('likes_, about_, timeline_, photos_'))
            infoperuser[userid] = file

    writeToJsonFile(infoperuser, os.environ['savedInfoFile'])