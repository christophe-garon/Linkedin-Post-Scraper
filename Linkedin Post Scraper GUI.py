#!/usr/bin/env python
# coding: utf-8

# In[1]:


#required installs (i.e. pip3 install in terminal): pandas, selenium, bs4, and possibly chromedriver(it may come with selenium)
#Download Chromedriver from: https://chromedriver.chromium.org/downloads
#To see what version to install: Go to chrome --> on top right click three dot icon --> help --> about Google Chrome
#Move the chrome driver to (/usr/local/bin) -- open finder -> Command+Shift+G -> search /usr/local/bin -> move from downloads

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
import pandas as pd
import random
import openpyxl
import caffeine
from openpyxl import load_workbook
caffeine.on(display=True)
import tkinter as tk
import threading


# In[2]:


root = tk.Tk()

#Defining our variables
tk_page = tk.StringVar()
tk_username = tk.StringVar()
tk_password = tk.StringVar()


canvas = tk.Canvas(root, height = 300 , width = 400, bg ='#49694b')
canvas.pack()

#making all of the frames
frame = tk.Frame(root, bg ='#49694b', bd =6)
frame.place(relx=0.5, rely=0.1, relwidth=0.8, relheight=0.15, anchor='n')

frame2 = tk.Frame(root, bg ='#49694b', bd =6)
frame2.place(relx=0.5, rely=0.25, relwidth=0.8, relheight=0.15, anchor='n')

frame3 = tk.Frame(root, bg ='#49694b', bd =6)
frame3.place(relx=0.5, rely=0.4, relwidth=0.8, relheight=0.15, anchor='n')

button_frame = tk.Frame(root, bg ='#49694b', bd =8)
button_frame.place(relx=0.5, rely=0.6, relwidth=0.8, relheight=0.15, anchor='n')


#Making all of our labels and inputs
label1 = tk.Label(frame, text="Linkedin URL: ", bg='#49694b')
label1.place(relwidth=0.35,relheight=1)

entry1 = tk.Entry(frame)
entry1.place(relx=0.375, relwidth=0.6,relheight=1)


def get_username():
    label2 = tk.Label(frame2, text="Username: ", bg='#49694b')
    label2.place(relwidth=0.35,relheight=1)

    entry2 = tk.Entry(frame2)
    entry2.place(relx=0.375, relwidth=0.6,relheight=1)
    return entry2


def get_password():
    label3 = tk.Label(frame3, text="Password: ", bg='#49694b')
    label3.place(relwidth=0.35,relheight=1)

    entry3 = tk.Entry(frame3)
    entry3.place(relx=0.375, relwidth=0.6, relheight=1)
    return entry3


#Functions to get variables from inputs
def submit1(entry1):
    tk_page.set(entry1)


def submit2(entry2,entry3):
    tk_username.set(entry2)
    tk_password.set(entry3)
    

#Button that calls function and waits until variables are defined to pass
button = tk.Button(button_frame, text= "Check for Existing Project", command=lambda: submit1(entry1.get()))
button.place(relx=0.3, relwidth=0.6,relheight=1)
button.wait_variable(tk_page)

page = tk_page.get()
company_name = page[33:-1]

#See if credetial file exists and create a project if not
try:
    f= open("{}_credentials.txt".format(company_name),"r")
    contents = f.read()
    username = contents.replace("=",",").split(",")[1]
    password = contents.replace("=",",").split(",")[3]
    page = contents.replace("=",",").split(",")[5]
    company_name = page[33:-1]
    post_index = int(contents.replace("=",",").split(",")[7])
    user_index = int(contents.replace("=",",").split(",")[9])
    
    wait = tk.StringVar()
    button = tk.Button(button_frame, text= "Let's Scrape", command=lambda: wait.set("go"))
    button.place(relx=0.3, relwidth=0.6,relheight=1)
    button.wait_variable(wait)
    
except:
    f= open("{}_credentials.txt".format(company_name),"w+")
    entry2 = get_username()
    entry3 = get_password()

    #Button that calls function and waits until variables are defined to pass
    button = tk.Button(button_frame, text= "Let's Srape", command=lambda: submit2(entry2.get(),entry3.get()))
    button.place(relx=0.3, relwidth=0.6,relheight=1)
    button.wait_variable(tk_password)

    #transforming our tk variables into python variables
    username = tk_username.get()
    password = tk_password.get()
    post_index = 1
    user_index = 1
    f.write("username={}, password={}, page={}, post_index={}, user_index={}".format(username,password,page,post_index,user_index))
    f.close()


# In[3]:


#accessing Chromedriver
browser = webdriver.Chrome('chromedriver')

#Open login page
browser.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
time.sleep(2)

#Enter login info:
elementID = browser.find_element_by_id('username')
elementID.send_keys(username)

elementID = browser.find_element_by_id('password')
elementID.send_keys(password)
time.sleep(1)
elementID.submit()
time.sleep(1)

# In[4]:


#Scrolls the main page
def scroll():
    #Simulate scrolling to capture all posts
    SCROLL_PAUSE_TIME = 1.5

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# In[6]:


def scrape_posts(containers):
    
    for container in containers:

        try:
            posted_date = container.find("span",{"class":"visually-hidden"})
            text_box = container.find("div",{"class":"feed-shared-update-v2__description-wrapper ember-view"})
            text = text_box.find("span",{"dir":"ltr"})
            new_likes = container.findAll("li", {"class":"social-details-social-counts__reactions social-details-social-counts__item"})
            new_comments = container.findAll("li", {"class": "social-details-social-counts__comments social-details-social-counts__item"})


            post_dates.append(posted_date.text.strip())
            post_texts.append(text.text.strip())



            try:
                video_box = container.findAll("div",{"class": "feed-shared-update-v2__content feed-shared-linkedin-video ember-view"})
                video_link = video_box[0].find("video", {"class":"vjs-tech"})
                media_links.append(video_link['src'])
                media_type.append("Video")
            except:
                try:
                    image_box = container.findAll("div",{"class": "feed-shared-image__container"})
                    image_link = image_box[0].find("img", {"class":"ivm-view-attr__img--centered feed-shared-image__image feed-shared-image__image--constrained lazy-image ember-view"})
                    media_links.append(image_link['src'])
                    media_type.append("Image")
                except:
                    try:
                        #mutiple shared images
                        image_box = container.findAll("div",{"class": "feed-shared-image__container"})
                        image_link = image_box[0].find("img", {"class":"ivm-view-attr__img--centered feed-shared-image__image lazy-image ember-view"})
                        media_links.append(image_link['src'])
                        media_type.append("Multiple Images")
                    except:
                        try:
                            article_box = container.findAll("div",{"class": "feed-shared-article__description-container"})
                            article_link = article_box[0].find('a', href=True)
                            media_links.append(article_link['href'])
                            media_type.append("Article")
                        except:
                            try:
                                video_box = container.findAll("div",{"class": "feed-shared-external-video__meta"})          
                                video_link = video_box[0].find('a', href=True)
                                media_links.append(video_link['href'])
                                media_type.append("Youtube Video")   
                            except:
                                try:
                                    poll_box = container.findAll("div",{"class": "feed-shared-update-v2__content overflow-hidden feed-shared-poll ember-view"})
                                    media_links.append("None")
                                    media_type.append("Other: Poll, Shared Post, etc")
                                except:
                                    media_links.append("None")
                                    media_type.append("Unknown")



            #Getting Video Views. (The folling three lines prevents class name overlap)
            view_container2 = set(container.findAll("li", {'class':["social-details-social-counts__item"]}))
            view_container1 = set(container.findAll("li", {'class':["social-details-social-counts__reactions","social-details-social-counts__comments social-details-social-counts__item"]}))
            result = view_container2 - view_container1

            view_container = []
            for i in result:
                view_container += i

            try:
                video_views.append(view_container[1].text.strip().replace(' Views',''))

            except:
                video_views.append('N/A')


            try:
                post_likes.append(new_likes[0].text.strip())
            except:
                post_likes.append(0)
                pass

            try:
                post_comments.append(new_comments[0].text.strip())                           
            except:                                                           
                post_comments.append(0)
                pass

        except:
            pass


# In[7]:


def export_post_data():
    
    comment_count = []
    for i in post_comments:
        s = str(i).replace('Comment','').replace('s','').replace(' ','')
        comment_count += [s]
    
    
    data = {
    "Date Posted": post_dates,
    "Media Type": media_type,
    "Post Text": post_texts,
    "Post Likes": post_likes,
    "Post Comments": comment_count,
    "Video Views": video_views,
    "Media Links": media_links
    }


    df = pd.DataFrame(data)

    writer = pd.ExcelWriter("{}_page_posts.xlsx".format(company_name), engine='xlsxwriter')
    df.to_excel(writer, index =False)
    writer.save()
    


# In[8]:



browser.get(page + 'posts/')
time.sleep(2)

#scroll through the page
scroll()

#get html from page
company_page = browser.page_source
linkedin_soup = bs(company_page.encode("utf-8"), "html")
containers = linkedin_soup.findAll("div",{"class":"occludable-update ember-view"})

#define the variables we want
post_dates = []
post_texts = []
post_likes = []
post_comments = []
video_views = []
media_links = []
media_type = []

#scrape the post data
scrape_posts(containers)

#export the df as excel file
export_post_data()

    

done_frame = tk.Frame(canvas, bg ='#49694b', bd =8)
done_frame.place(relx=0.5, rely=0.75, relwidth=0.8, relheight=0.15, anchor='n')

label_done = tk.Label(done_frame, text="The Scrape is Complete", bg='gold')
label_done.place(relx=0.33, relwidth=0.5,relheight=1)


root.mainloop()


# In[ ]:




