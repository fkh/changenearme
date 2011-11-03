import scraperwiki
import lxml.html 
import json

import sys

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# first we get everything from ioby
print "starting on ioby"
html = scraperwiki.scrape("http://ioby.org/projects?phrase=&status=All&vols=All&sort_by=title&sort_order=ASC&items_per_page=All")
root = lxml.html.fromstring(html)

for project in root.cssselect("div[class='main-info']"):
    project_name = project.cssselect("h3")[0].text_content()
    
    print project_name

# get the url
    url = project.cssselect("h3 a")[0].attrib.get("href")
    
    project_url = "http://ioby.org" + url

# go get the project page, to grab geo info 
    subpage = scraperwiki.scrape(project_url)

    start = subpage.find("jQuery.extend(Drupal.settings")
    end = subpage.find("\n", start)
    line = subpage[start:end]
    line = line.replace('jQuery.extend(Drupal.settings, ', '')[:-2]

# see if the grabbed jQuery line has location info, if it doesn't, move on
    if line.find("gmap") == -1:
        print "Found a bad line"
        continue

# convert the line to json and get the location info
    bigjson = json.loads(line)
    project_lat = bigjson["gmap"]["project-map"]["markers"][0]["latitude"]
    project_lon = bigjson["gmap"]["project-map"]["markers"][0]["longitude"]

    data = {
      'source' : "ioby",
      'project' : project_name,
      'url' : project_url,
      'latitude' : project_lat,
      'longitude' : project_lon,
    }

    scraperwiki.sqlite.save(unique_keys=['project'], data=data)

# that's it for ioby.

# get everything from Change By Us
print "starting on cbu"
html = scraperwiki.scrape("http://nyc.changeby.us/search#projects")
root = lxml.html.fromstring(html)

# fetch project details
for project in root.cssselect("div[class='project-info']"):

# name and url
    project_name = project[0].text_content()
    url = project[0].cssselect("a")[0].attrib.get("href")

    project_url = "http://nyc.changeby.us" + url
    print project_url
    
    if url == "/project/":
        break
    
# go to subpage for the location details
    subpage = scraperwiki.scrape(project_url) # this is a long page, we're looking for the map config info in a line containing app_page.data.project
    
    start = subpage.find("app_page.data.project")
    end = subpage.find("\n", start)
    line = subpage[start:end]

# clean it up
    projectjson = line.replace('app_page.data.project = ', '')[:-1]

    bigjson = json.loads(projectjson)

# this is not very elegant, but I'm confused about dealing with this json-like string
    project_lat = bigjson["info"]["location"]["position"]["lat"][0:]
    project_lon = bigjson["info"]["location"]["position"]["lng"][0:]
    scope = bigjson["info"]["location"]["name"][0:]

    data = {
      'source' : "Change By Us",
      'project' : project_name,
      'url' : project_url,
      'latitude' : project_lat,
      'longitude' : project_lon,
    }

    scraperwiki.sqlite.save(unique_keys=['project'], data=data)

