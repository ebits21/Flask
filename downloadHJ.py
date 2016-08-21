#! python3
''' Download all ENT articles from the hearing journal'''
#Import requests for downloading, os to make directory, re to match titles
import requests, os, re, time
import bs4

#Website to load and directory to save files in
pageUrl = 'http://journals.lww.com/thehearingjournal/pages/author.aspx?firstName=Hamid&middleName=R.&lastName=Djalilian'
pdfDirectory = r'.\\HJ_ENT_Articles_test'

def check_directory (pdfDirectory):
    #Check to see if article folder exists.  If not then create it
    if os.path.exists(pdfDirectory):
        return True
    os.makedirs(pdfDirectory)
    return False
    
def load_soup(pageUrl):
    #Download page as a stream.  Create soup object using lxml parser
    res = requests.get(pageUrl, stream=True)
    soup = bs4.BeautifulSoup(res.text, "lxml")
    return (res, soup)

def load_titles(soup):
    #Find all article titles and save to a list.
    titles = soup.find_all("div", id="ej-featured-article-info")
    fileNames=[]
    regex=re.compile(r"""(Through\sthe\sOtoscope:\s\s)?   #optional title
                         (Clinical\sConsultation:\s\s)?  #optional title
                         (Symptoms?:\s\s?)?             #optional title
                         (.*)?                  #title we want""",re.VERBOSE)
    for title in titles:
        #select 4th regex group as file title    
        description = regex.search(title.a.string).group(4)
        #get rid of undesired characters in the title
        description = description.replace(" ", "_").replace(",", "").replace("-","_").replace("__","_")
        fileNames.append(description)
    return fileNames
    
def load_pdf_urls(soup):   
    match = soup.find_all("a", class_="ejp-standard-pdf")
    return [link.get('href') for link in match] 

def __save_pdf(pdfLocation, link, website):
    #download pdf using requests module
    website = requests.get(link)
    #Create .pdf file and save content from website to file
    with open(pdfLocation, "wb") as f:
        f.write(website.content)
        
def create_files(website, matches, mainTitle, pdfDirectory):
    #loop through all found links and save .pdf's
    for counter, link in enumerate(matches, start=1):
        #create item number starting at most recent 
        itemNum = len(matches)+1-counter
        #check to see if the article is already saved
        if os.path.isfile(pdfDirectory + r'\{}_{}.pdf'.format(itemNum, mainTitle[counter-1])):
            print('Skipping article {}, already saved...\n'.format(itemNum))
            continue
        print('Downloading article {} ...'.format(itemNum))
        #generate file path and save the file
        __save_pdf(pdfDirectory + r'\{}_{}.pdf'.format(itemNum, mainTitle[counter-1]), link, website)
        print ('Article {} has been saved!\n'.format(itemNum))
    #print the total number of files saved
    print ('Finished.  {} scraped pdf files in directory.'.format(counter))
    
def load_all(pageUrl):
    print ('Downloading html and creating soup object...', end="")
    res, soup = load_soup(pageUrl)
    print ('done')

    print('Finding all .pdf articles...', end=" ")
    matches = load_pdf_urls(soup)
    print('{} .pdf links found.'.format(len(matches)))

    print('Finding all article titles...', end=" ")
    mainTitle = load_titles(soup)
    print('{} titles found\n'.format(len(mainTitle)))
    return (res, matches, mainTitle)
        
if __name__=='__main__':
    #Create file to put .pdfs in if necessary
    print('Checking file directory...', end="")
    if check_directory(pdfDirectory):
        print('file folder already created')
    else:
        print('file folder created')
    
    #load website, pdf urls and titles        
    website, matches, mainTitle = load_all(pageUrl) 
    
    startTime = time.time()
    #For each .pdf link, check if it exists and save it of not.
    create_files(website, matches, mainTitle, pdfDirectory)
    endTime = time.time()
    
    print ('Program took {} seconds to create files'.format(endTime-startTime))
