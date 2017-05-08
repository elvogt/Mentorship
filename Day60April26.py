import urllib.request
from urllib.parse import urlparse
import datetime
import re
from pathlib import Path
import os
import json
import io
import csv

import sys
import argparse
from collections import OrderedDict
from bs4 import BeautifulSoup, SoupStrainer

parser = argparse.ArgumentParser(description = 'Set the variables to be used \
    later in the program. \n If you want to reconstruct a full website saved \
    at location Desktop: \n \
    http://www.mywebsite.org/ full -s /Desktop/ \n If you want to \
    reconstruct a single webpage with a prefix of site: \n \
    http://www.thiswebsite.com/page/ single -p site')
parser.add_argument('URI', nargs = 1, type = str, default = " ", help = "What is the URI (URL) \
    you would like to recover?")
parser.add_argument('Depth', nargs = 1, type = str, default = " ", help = "Would you like to \
    retrieve the whole website? Please indicate full or single.")
parser.add_argument('-s', nargs = '?', type = str, default = " ", help = "Where would you \
    like to save the recovery? Please include the full path.")
parser.add_argument('-p', nargs = '?', type = str, default = " ", help = "Would you like \
    to add a prefix to the beginning of the generic filenames? This can be useful \
    for multiple recoveries.")
args = parser.parse_args()
a = args.__dict__

global InitialURI
URI = a['URI']
URI = str(URI[0])
headers = ""
while headers == "":
    try:
        local_filename, headers = urllib.request.urlretrieve(URI)
    except:
        URI = input("That was not a valid URI. Try again: ")
InitialURI = URI
print (InitialURI)
##InitialURI = 'http://www.nhgs.tec.va.us/'                #Initial URI that was requested

global tagOption                    #Do you want to get the anchor tags? used in FileDump()
tag = a['Depth']
tag = str(tag[0])
tag.lower()
while tag == " " and tag != "full" and tag != "single":
    tag = input("Please indicate full or single: ")
tagOption = tag
print (tagOption)
global saveLocation
s = a['s']
saveLocation = s
print (saveLocation)
##saveLocation = "/Volumes/EMILY/Mentorship/" #"D:/Mentorship/"

global prefix
p = a['p']
print (p)
prefix = str(p)
print (prefix)
##prefix = ""

global pageRequest                  #how many pages that are requested to be retrieved
pageRequest = 1
#pageRequest = int(input("How many pages need to be recovered? "))
global pageCount                    #how many pages have been recovered
pageCount = 1
global frontier
global resourceLocation   #creates a dictionary that will contain each embedded resource and the location of its file
resourceLocation = {}
global soupFixed
soupFixed = {}          #creates a dictionary for all of the stuff taken out of BeautifulSoup {fixed:found}
global InitURI
InitURI = InitialURI
global logFile
logFile = ['InitURI', 'Item Number', 'URI-R', 'URI-M', 'Location', 'HTTP Code']
global tags
tags = []

#LogFile() requires nothing and writes the logFile[] line to the log file (LogFile.csv)
#Called by command line
def LogFile(uri, itemNum):
    global logFile
    global prefix
    file = open(prefix + "LogFile.csv", 'a')
    writer = csv.writer(file)
    writer.writerow(logFile)
    file.close()
    global InitURI
    logFile[0] = InitURI
    logFile[1] = itemNum
    logFile[2] = uri
    InitialURIs(uri)

#GetDate requires nothing and returns the current date to be used in the momento request
#Called in first line of InitialURIs()
def GetDate(): #gets the date to recall the most recent momento
    output = datetime.date.today()
    output = str(output)
    date = output.replace("-", "")
    return date

#InitialURIs requires the date of retrievment and returns a list of URIs from the momento and the initial URI
#Called by command line
def InitialURIs(uri): #all the URIs given
    print ("InitialURIs")
    date = GetDate()
    retrieve = 'http://timetravel.mementoweb.org/memento/' + date + '/' + uri
    global logFile
    logFile[3] = retrieve
    print (retrieve)
    global prefix
    try:
        local_filename, headers = urllib.request.urlretrieve(retrieve) #uses date to access the most recent momento
        html = open(local_filename)
        html = str(html)
        content = str(headers)
        a = re.findall("([<](\S)+[>])", content)
        LastURI(a, uri)
    except urllib.error.HTTPError as err:
        print(err.code)
        logFile[5] = err.code
        logFile[4] = "error"
    except urllib.error.URLError:
        logFile[5] = "Connection Refused"
        logFile[4] = "Connection Refused"
##        global prefix
##        file = open(prefix + "LogFile.csv", 'a')
##        writer = csv.writer(file)
##        writer.writerow(logFile)
##        file.close()

#LastURI requires the URIs and initial URI and returns the last (most recent) URI to be used to create a file in CreateFile()
#Called in last line of InitialURIs()
def LastURI(URIs, uri): #only the last and most recent URI
    print("LastURI")
    u = URIs
    if u != []:
        last = u[-1][0]
        last = re.findall("([^<>]+)", last)
        last = last[0]
        last = IMTrick(last)
        if str(last.find(r"\.htm[l]*")) != "-1":
            try:
                last = IMTrick(last)
            except:
                pass 
        CreateFile(last, uri)

#IMTrick expects the uri and returns the uri with im_ inserted after the numbers
#Called in LastURI() before creating the file
#URI-M --> URI-M original
def IMTrick(uri):
    print ("IMTrick")
    find = re.findall(r"(\d+)", uri)
    uri = uri.replace(find[0], find[0] + "im_")
    return uri

#CreateFile expects the last URI and initial URI and creates directory files and puts the contents of the momento into the most specific directory
#Called in last line of LastURI()
def CreateFile(lURI, iURI): #Create directories based on the path
    print("CreateFile")
    uri = str(lURI)
    global logFile
    try:
        with urllib.request.urlopen(uri) as response:
            html = response.read()                  #this is the whole bunch of content
    except:
        HTTP = urllib.request.urlopen(uri).getcode() #retrieves the HTTP Code number
        logFile[5] = HTTP
        return
    #html = html)
    local_filename, headers = urllib.request.urlretrieve(uri)
    headers = str(headers)                      #retrieves the header which contains the Content Type
    HTTP = urllib.request.urlopen(uri).getcode() #retrieves the HTTP Code number
    logFile[5] = HTTP
    type = re.findall("((C|c)ontent(.)(T|t)ype:(.)+)+", headers) #get content type in a list
    type = type[0]                              #gets the tuple from the list
    type = type[0]                              #gets the content-type phrase
    global InitURI 
    parse = urlparse(iURI)                       #ParseResult(scheme='', netloc='', path='help/Python.html', params='',query='', fragment='')
    main_dir = parse[1]                   #create the first main directory and it has the main website name
    try: os.makedirs(main_dir)                 #skips creation if it already exists
    except OSError as exception:
        pass
    paths = parse[2]
    paths = paths.split('/')                    #separate into subdirectory labels
    length = len(paths)
    directory = main_dir + '/'
    fullPath = '/'
    for x in range(1, length - 1):              #creates a directory for every step of the path except the last one which is the file name
        fullPath = fullPath + paths[x] + '/'
        directory = directory + paths[x] + '/'
        try: os.makedirs(directory)
        except OSError as exception:
                pass
    #my_dir = directory                    #directory to put file into
    if paths[length-1].strip() == '':
        file_name = 'index.html'
    else:
        file_name = paths[length-1]             #file name
    global saveLocation
    fullPath = fullPath + file_name
    fname = saveLocation + directory + file_name + parse[4]           #specifies where to save the file and what to name it
    logFile[4] = fname
    typeText = int(type.find("text"))
    if typeText != -1:
        html = str(html)
        file = open(fname, 'w')
        file.write(html)                           #puts the html (content) and headers into the file
        file.close()
        Clean(fname)
    else:
        os.system('chmod -R 777 "' + saveLocation + directory + '"')
        os.system('/usr/local/bin/wget -O "' + str(fname) + '" ' + uri)
    global soupFixed
    if str(fullPath) in soupFixed:
        found = soupFixed[fullPath]
        resourceLocation[found] = fname
    else:
        resourceLocation[iURI] = fname
    if iURI == InitURI:
        global content
        content = fname
    global pageCount
    global pageRequest
    print (pageCount)
    print (pageRequest)
    #if pageCount <= pageRequest:
    if int(type.find("html")) != -1:
        CreateJSON(iURI)

##Clean() expects a file and returns nothing. The file is simply cleaned up.
##Called whenever a file is created
def Clean(file):
    print ("Clean")
    f = open(file, 'r')
    content = f.read()
    f.close()
    content = content.replace(r"\n", "\n")
    content = content.replace(r"\r", "\r")
    content = content.replace(r"\'", "'")
    content = content.replace(r"\t", "\t")
    if content[:2] == "b'":
        content = content[2:]
    if content[-1:] == "'":
        content = content[:-1]
    f = open(file, "w")
    f.write(content)
    f.close()
    
def CreateJSON(website):
    print("CreateJSON")
    global pageCount
    pageCount = pageCount + 1
    localRecoveryLocation = "none"
    global prefix
    initialDictionary = WebScrape(website)
    if localRecoveryLocation!= None:			# Used to determine if there is a localRecoveryLocation
        if localRecoveryLocation == "none":   #replaced localRecoveryLocation with saveLocation
            pass
        else:
            newDictionary = FileRetrieve(localRecoveryLocation)
    anchorDictionary = OrderedDict()		#OrderedDict is a normal dictionary that remembers the order that items were added to the dictionary
    resourceDictionary = OrderedDict()
    for keys in initialDictionary:			#takes the dictionary from WebScrape and put into initialDictionary and puts the key/value pair either in anchors or resources
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
    completeName = os.path.join(saveLocation, prefix + ".json")                # Assembles the complete path for the inputed document
    completeNameAnchor = os.path.join(saveLocation, fileNameAnchor + ".json")
    completeNameResource = os.path.join(saveLocation, fileNameResource + ".json")
    FileDump(anchorDictionary, resourceDictionary, completeNameAnchor, completeNameResource)
    
#FindReplace expects nothing and goes into the InitURI's index.html file and changes the URIR into the location of the resource
#Called in ReadJSON
def FindReplace():
    print("FindReplace")
    file = open(resourceLocation[InitURI], 'r')
    content = file.read()
    file.close()
    for key in resourceLocation:
        k = str(key)
        v = str(resourceLocation[key])
        if k != v:
            place = replace(k, v)
            while place != -1:
                replace(k, v)
            
def replace(key, value):
    file = open(resourceLocation[InitURI], 'r')
    content = file.read()
    file.close()
    replaced = open(resourceLocation[InitURI], 'w')
    content = content.replace(key, value)
    place = content.find(key)
    replaced.write(content)
    replaced.close()
    return place
    
# WebScrape expects the parameter of a user URL (starting with 'http://') and will return an ordered dictionary containing the links and resources
# for the page. The dictionary sorts the links by type (i.e. img, script, link, a, ect...) by assigning the types as the values inside the dictionary.
def WebScrape(userURL):
    print("WebScrape")
    #if fileName is None:                       only needed when getting user input
    #fileName = 'YourWarrickFile'                # The default file name.
        #print ("No name specified. File name created as 'YourWarrickFile'.")       only needed when interacting with a user
    global prefix
    global fileNameResource
    fileNameResource = prefix + "Resources"
    global fileNameAnchor
    fileNameAnchor = prefix + "Anchors"

    httpString = "http:"                    # ****String variables are used to build URL filler variables and check for fragmented URLs in the webpage.
    dataString = "data" 
    forwardSlashString = "//"
    
##    html_content = urllib.request.urlopen(userURL)                    # html_content contains the entirety of the web page source.
##    file = open('Gavin Content.txt', 'w')
##    file.write(str(html_content.read()))
##    file.close()
    UrlTitlebreakdown = urlparse(userURL)            # UrlTitlebreakdown contains a list of the web identifiers for the website.
    scheme = UrlTitlebreakdown[0]                    # The UrlTitlebreakdown variables are the different parts of the URL.
    netloc = UrlTitlebreakdown[1]
    print (UrlTitlebreakdown)
    path = UrlTitlebreakdown[2]
    query = UrlTitlebreakdown[3]
    fragment = UrlTitlebreakdown[4]

    global myDomain                # Creates search criteria by retrieving the hostname of the URL
    splitDomain = netloc.split('.')
    myDomain = splitDomain[-2] + '.' + splitDomain[-1]
    
    secondaryUrlFiller = scheme + ":"

    global InitURI
    global content
    file = open(content, 'r')
    html_content = file.read()
    file.close()
    soup = BeautifulSoup(html_content, "html.parser")                    # soup takes the html_content and creates a parsable variable. 
    packagingDictionary = {'a':'href', 'img':'src', 'link':'href', 'script':'src', 'video':'src', 'audio':'src'}                    # packagingDictionary is the tool used to sort the parsed URLs into a data structure.
                                                                                                                                    #WHRE DID HE GET THESE THINGS FROM?
    packageList = list(packagingDictionary.keys())                    # packageList is used to allow for iteration tests while parsing. Took the dictionary and made it a list
    outputDictionary = OrderedDict()                    # outputDictionary is the designated data structure that holds the returned URLs and their reference type.
    compiledDictionary = OrderedDict()
    
    for keys in packageList:                    # instances every key in the packagingList. I DON’T THINK THIS NEEDED TO BE A LIST. IT CAN STAY A DICTIONARY.
        for found in soup.find_all(keys):                   # instances every link in the soup that uses the value inside the ().
            output = found.get(packagingDictionary[keys])
            if output is None or len(output) == 0:                    # checks for bad pointers and iterates to the next cycle if found. 
                length = 0    			#AKA no URI was found to get
            else:
                length = len(output)
                addString = ''
                if output[0] == " " or output[0] == ".":
                    fixed = output[1:]              #separate fixed version of the string to put in the dictionary
                    soupFixed[fixed] = str(output)
                    output = fixed                  #set output as the fixed version for future use in WebScape()
                if output[1:4] == "'./":                     
                    fixed = output[3:-2]           #separate fixed version of the string to put in the dictionary
                    soupFixed[fixed] = str(output)
                    output = fixed                  #set output as the fixed version for future use in WebScape()
                index = output.find(InitialURI)
                if index != 0 and index != -1:
                    fixed = output[index:]
                    soupFixed[fixed] = str(output)
                    output = fixed 
                if length > 4:                    # checks if URL length is feasible.
                    if httpString[0:3] == output[0:3] or dataString[0:3] == output[0:3]:                    # checks if http:// is there. If the statement is true, the URI is complete and is added to the outputDictionary
                        addString = output                    # addString is a temp variable which passes the complete URL to the outputDictionary.                    
                    elif forwardSlashString[0:2] == output[0:2]:                    #if // is present but http isn't
                        addString = secondaryUrlFiller + output                    # supplements fragmented URL with http: to add to the existing ‘//‘
                    else:
                        if path != '' and netloc != '':
                            if path[0] == '/' and netloc[-1] == '/':
                                path = path[1:]
                            elif path[0] != '/' and netloc[-1] != '/':
                                path = '/' + path
                        if path != '' and output != '':
                            if output[0] == '/' and path[-1] == '/':
                                output = output[1:]
                            elif output[0] != '/' and path[-1] != '/':
                                output = '/' + output
                        if InitialURI.find(path) != -1:
                            addString = httpString + forwardSlashString + netloc + path + output
                        elif InitialURI.find(path) == -1:
                            addString = httpString + forwardSlashString + netloc + output
                if addString.find(InitialURI) != -1 and addString != InitURI:
                    outputDictionary[addString] = keys                    # adds the URL as a key and assigns the type as the corresponding value.
    
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
    print ("FileDump")
    with open(completeNameAnchor, 'w') as fp:
        json.dump(anchorDictionary, fp, sort_keys=False, indent=4)
    fp.close()
    with open(completeNameResource, 'w') as fp:
        json.dump(resourceDictionary, fp, sort_keys=False, indent=4)
    fp.close()
    ReadJSON(completeNameResource, completeNameAnchor)

#FileRetrieve expects nothing and returns loadedDictionary as a json file
#Called in beginning of InitialURIs()
def FileRetrieve(localRecoveryLocation):
    print("FileRetrieve")
    with open(localRecoveryLocation, 'r') as fp:                    # references a file. 
            loadedDictionary = json.load(fp, object_pairs_hook=OrderedDict)                    # creates an ordered dictionary with the content of the file.
            return loadedDictionary

#ReadJSON expects the filename of a json file and location if needed and prints the contents
#Called in last line of FileDump()
def ReadJSON(filename, completeNameAnchor):
    count = 1
    print("ReadJSON")
    global frontier
    frontier = []
    f = open(filename, 'r')
    f = f.read()
    jsondict = json.loads(f)
    for x in jsondict.keys():               #created frontier from all URIs in JSON file
        frontier.append(x)
    with open(prefix + 'Frontier.txt', 'a') as fp:
        json.dump(frontier, fp, sort_keys = False, indent = 4)
    fp.close()
    for x in range(len(frontier)):
        file = open(prefix + 'LogFile.csv', 'r')
        found = file.read()
        file.close()
        if found.find(frontier[0]) == -1:
            LogFile(frontier[0], count)
            count = count + 1
        del frontier[0]
    FindReplace()
    global tagOption
##    if tagOption == '':
##        tagOption = input("Tags? Yes or no: ")
##        if tagOption == 'yes':
##            AnchorTags(completeNameAnchor)
##        else:
##            LogFile(" ", 0)             #Needed to print the last values in the set
    if tagOption == 'full':
        AnchorTags(completeNameAnchor)
    else:
        print ("Recovery complete")

def AnchorTags(filename):
    print ("AnchorTags")
    global tags
    f = open(filename, 'r')
    f = f.read()
    jsondict = json.loads(f)
    for x in jsondict.keys():
        tags.append(x)
    with open(prefix + 'Tags.txt', 'a') as fp:
        json.dump(tags, fp, sort_keys = False, indent = 4)
    fp.close()
    length = len(tags)
    print (length)
    while length > 0:
        file = open(prefix + 'LogFile.csv', 'r')
        found = file.read()
        file.close()
        if found.find(tags[0]) == -1:
            global soupFixed
            soupFixed = {}
            global pageCount 
            pageCount = 1
            global InitURI
            InitURI = tags[0]
            print (InitURI)
            LogFile(InitURI, 1)
        del tags[0]
        length = length - 1
    print ("Full Recovery Complete")

LogFile(InitURI, 1) 
