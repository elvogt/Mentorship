import urllib.request
from urllib.parse import urlparse
import datetime
import re
from pathlib import Path
import os
import json

import sys
import argparse
from collections import OrderedDict
from bs4 import BeautifulSoup, SoupStrainer

#GetDate requires nothing and returns the current date to be used in the momento request
#Called in first line of InitialURIs()
def GetDate(): #gets the date to recall the most recent momento
    output = datetime.date.today()
    output = str(output)
    date = output.replace("-", "")
    return date

#InitialURIs requires the date of retrievment and returns a list of URIs from the momento and the initial URI
#Called by command line
def InitialURIs(URI): #all the URIs given
    print (URI)
    date = GetDate()
    #global website
    #website = 'http://i2.cdn.turner.com/cnnnext/dam/assets/160804100836-obama-clinton-hug-dnc-medium-plus-169.jpg'#'http://www.cnn.com/2016/09/26/health/wait-for-flu-shot/index.html'
    #'http://i2.cdn.turner.com/cnnnext/dam/assets/160804100836-obama-clinton-hug-dnc-medium-plus-169.jpg'#'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png'
    local_filename, headers = urllib.request.urlretrieve('http://timetravel.mementoweb.org/memento/' + date + '/' + URI) #uses date to access the most recent momento
    html = open(local_filename)
    html = str(html)
    content = str(headers)
    a = re.findall("([<](\S)+[>])", content)
    LastURI(a, URI)

#LastURI requires the URIs and initial URI and returns the last (most recent) URI to be used to create a file in CreateFile()
#Called in last line of InitialURIs()
def LastURI(URIs, iURI): #only the last and most recent URI
    u = URIs
    last = u[3][0]
    last = re.findall("([^<>]+)", last)
    last = last[0]
    CreateFile(last, iURI)

#CreateFile expects the last URI and initial URI and creates directory files and puts the contents of the momento into the most specific directory
#Called in last line of LastURI()
def CreateFile(lURI, iURI): #Create directories based on the path 
    uri = str(lURI)
    with urllib.request.urlopen(uri) as response:
        html = response.read()                  #this is the whole bunch of content
    html = str(html)
    print(html)
    local_filename, headers = urllib.request.urlretrieve(uri) 
    headers = str(headers)                      #retrieves the header which contains the Content Type
    HTTP = urllib.request.urlopen(uri).getcode() #retrieves the HTTP Code number
    type = re.findall("((C|c)ontent(.)(T|t)ype:(.)+)+", headers) #get content type in a list
    type = type[0]                              #gets the tuple from the list
    type = type[0]                              #gets the content-type phrase
    parse = urlparse(iURI)                       #ParseResult(scheme='', netloc='', path='help/Python.html', params='',query='', fragment='')
    directory = parse[1]                        #create the first main directory and it has the main website name
    print(directory)
    try: os.makedirs(directory)                 #skips creation if it already exists
    except OSError as exception:
        pass
    paths = parse[2]
    paths = paths.split('/')                    #separate into subdirectory labels
    length = len(paths)
    my_dir = ''
    for x in range(1, length - 1):              #creates a directory for every step of the path except the last one which is the file name
        directory = paths[x]
        try: os.makedirs(directory)
        except OSError as exception:
            pass
    my_dir = directory                    #directory to put file into
    print(paths)
    if paths[length-1] == '':
        file_name = 'index.html'
    else:
        file_name = paths[length-1]             #file name
    print(file_name)
    saveLocation = "/Volumes/EMILY\'S/Mentorship/"
    fname = saveLocation + my_dir + '/' + file_name            #specifies where to save the file and what to name it
    file = open(fname, 'w')
    file.write(html)                            #puts the html (content) and headers into the file
    file.close()
    CreateJSON(iURI)
    
def CreateJSON(website):
    saveLocation = "/Volumes/EMILY\'S/Mentorship"
    localRecoveryLocation = "none"
    global fileName
    fileName = "Test"
    initialDictionary = WebScrape(website, saveLocation, fileName)
    if localRecoveryLocation!= None:			# Used to determine if there is a localRecoveryLocation
        if localRecoveryLocation == "none":   #replaced localRecoveryLocation with saveLocation
            pass
        else:
            newDictionary = FileRetrieve(localRecoveryLocation)
    anchorDictionary = OrderedDict()
    resourceDictionary = OrderedDict()
    for keys in initialDictionary:
        if initialDictionary[keys] == "domainAnchor":
            anchorDictionary[keys] = "domainAnchor"
        if initialDictionary[keys] == "image":
            resourceDictionary[keys] = "image"
        if initialDictionary[keys] == "javaScript":
            resourceDictionary[keys] = "javaScript"
        if initialDictionary[keys] == "link":
            resourceDictionary[keys] = "link"
        if initialDictionary[keys] == "audio":
            resourceDictionary[keys] = "audio"
        if initialDictionary[keys] == "video":
            resourceDictionary[keys] = "video"
    completeName = os.path.join(saveLocation, fileName + ".json")                # Assembles the complete path for the inputed document
    completeNameAnchor = os.path.join(saveLocation, fileNameAnchor + ".json")
    completeNameResource = os.path.join(saveLocation, fileNameResource + ".json")
    print(anchorDictionary)
    FileDump(anchorDictionary, resourceDictionary, completeNameAnchor, completeNameResource)        
    
# WebScrape expects the parameter of a user URL (starting with 'http://') and will return an ordered dictionary containing the links and resources
# for the page. The dictionary sorts the links by type (i.e. img, script, link, a, ect...) by assigning the types as the values inside the dictionary.
def WebScrape(userURL, saveLocation, fileName):
    #if fileName is None:                       only needed when getting user input
    #fileName = 'YourWarrickFile'                # The default file name.
        #print ("No name specified. File name created as 'YourWarrickFile'.")       only needed when interacting with a user
    global fileNameResource
    fileNameResource = fileName + "Resources"
    global fileNameAnchor
    fileNameAnchor = fileName + "Anchors"

    #if saveLocation is None:                   only needed when getting user input
    #saveLocation = 'C:\Python27'                # The default file save location.
        #print ("No save location specified. Save location created as 'C:\Python27'.")
    #elif saveLocation == 'none':               only needed when getting user input
        #saveLocation = None    
    #else:
        #pass

    html_content = urllib.request.urlopen(userURL)                    # html_content contains the entirity of the web page source.
    UrlTitlebreakdown = urlparse(userURL)            # UrlTitlebreakdown contains a list of the web identifiers for the websight.
    
    scheme = UrlTitlebreakdown[0]                    # The UrlTitlebreakdown variables are the different parts of the URL.
    netloc = UrlTitlebreakdown[1]
    path = UrlTitlebreakdown[2]
    query = UrlTitlebreakdown[3]
    fragment = UrlTitlebreakdown[4]
    global myDomain                # Creates search crietera by retreiving the hostname of the URL
    splitDomain = netloc.split('.') 
    myDomain = splitDomain[-2] + '.' + splitDomain[-1]

    httpString = "http"                    # ****String variables are used to build URL filler variables and check for fragmented URLs in the webpage.
    dataString = "data" 
    forwardSlashString = "//"
    
    html_content = urllib.request.urlopen(userURL)                    # html_content contains the entirity of the web page source.
    UrlTitlebreakdown = urlparse(userURL)            # UrlTitlebreakdown contains a list of the web identifiers for the websight. 

    scheme = UrlTitlebreakdown[0]                    # The UrlTitlebreakdown variables are the different parts of the URL.
    netloc = UrlTitlebreakdown[1]
    path = UrlTitlebreakdown[2]
    query = UrlTitlebreakdown[3]
    fragment = UrlTitlebreakdown[4]    
    
    UrlFiller = scheme + "://" + netloc                    # UrlFiller variables are used to suppliment partial URLs.
    secondaryUrlFiller = scheme + ":"
    
    soup = BeautifulSoup(html_content, "html.parser")                    # soup takes the html_content and creates a parsable variable. 
    packagingDictionary = {'a':'href', 'img':'src', 'link':'href', 'script':'src', 'video':'src', 'audio':'src'}                    # packagingDictionaryis the tool used to sort the parsed URLs into a data structure.
    packageList = list(packagingDictionary.keys())                    # packageList is used to allow for iteration tests while parsing. 
    outputDictionary = OrderedDict()                    # outputDictionary is the designated data structure that holds the returned URLs and their reference type.
    compiledDictionary = OrderedDict()
    
    for keys in packageList:                    # instances every key in the packagingList.
        for link in soup.find_all(keys):                    # instances every link in the soup that uses the value inside the ().
            output = link.get(packagingDictionary[keys])
            if output is None:                    # checks for bad pointers and iterates to the next cycle if found.
                length = 0    
            else:
                length = len(output)
                if length > 4:                    # checks if URL length is fesiable.
                    if httpString[0:3] == output[0:3] or dataString[0:3] == output[0:3]:                    # checks if URL is fragmented.
                        addString = output                    # addString is a temp variable which passes the complete URL to the outputDictionary.
                        outputDictionary[addString] = keys                    # adds the URL as a key and assigns the type as the coresponding value.
                elif forwardSlashString[0:2] == output[0:2]:                    # checks for specific fragmented URL.
                        addString = secondaryUrlFiller + output                    # supplements fragmented URL. 
                        outputDictionary[addString] = keys
                else:
                    addString = UrlFiller + output                     
                    outputDictionary[addString] = keys
    
    for keys in outputDictionary:			#Re-establishes the outputDictionary into a new compiledDictionary assigning new 'Types' to URLs.
        if outputDictionary[keys]=="img":
            compiledDictionary[keys] = "image"
        if outputDictionary[keys]=="link":
            compiledDictionary[keys] = "link"
        if outputDictionary[keys]=="script":
            compiledDictionary[keys] = "javaScript"
        if outputDictionary[keys]=="video":
            compiledDictionary[keys] = "video"
        if outputDictionary[keys]=="audio":
            compiledDictionary[keys] = "audio"
        if outputDictionary[keys]=="a":       # Checks the host name against the current URL and decides to either flag it as a domain anchor or normal anchor.
            if myDomain in keys:
                compiledDictionary[keys] = "domainAnchor"
            else:
                compiledDictionary[keys] = "anchor"                  
    return compiledDictionary                    # compiledDictionary holds the URLs as keys linked to their types as the values.

# FileDump expects the parameter of a anchorDictionary, resourceDictionary, completeNameAnchor, completeNameResource and will create 2 json files
# Called in last line of CreateJSON()
def FileDump(anchorDictionary, resourceDictionary, completeNameAnchor, completeNameResource):
    with open(completeNameAnchor, 'a') as fp:
        json.dump(anchorDictionary, fp, sort_keys=False, indent=4)
    #fp.close()
    with open(completeNameResource, 'a') as fp:
        print(json.dump(resourceDictionary, fp, sort_keys=False, indent=4))
    #fp.close()
    #ReadJSON(completeNameAnchor)     #######STOPPED HERE#######
    #ReadJSON(completeNameResource)

#FileRetrieve expects nothing and returns loadedDictionary as a json file
#Called in beginning of InitialURIs()
def FileRetrieve(localRecoveryLocation):
    with open(localRecoveryLocation, 'r') as fp:                    # references a file. 
            loadedDictionary = json.load(fp, object_pairs_hook=OrderedDict)                    # creates an ordered dictionary with the content of the file.
            return loadedDictionary
        
#ReadJSON expects the filename of a json file and location if needed and prints the contents
#Called in last line of FileDump()
def ReadJSON(filename):
    frontier = []
    file = open(filename, 'r')
    file = file.read()
    jsondict = json.loads(file)
    for x in jsondict.keys():               #created frontier from all URIs in JSON file
        frontier.append(x)
    for x in range(len(frontier)):
        InitialURIs(frontier[0])
        del frontier[0]
        print(frontier)
#ReadJSON("CNNSourceAnchors.json")           #hardcoded using Gavin's examples for working at home
#ReadJSON("CNNSourceResources.json")         #hardcoded using Gavin's examples for working at home
#CreateJSON()
#ReadJSON('CnnSourceRecursiveAnchors.json')
InitialURIs('http://www.cnn.com/') #'http://i2.cdn.turner.com/cnnnext/dam/assets/160804100836-obama-clinton-hug-dnc-medium-plus-169.jpg'
