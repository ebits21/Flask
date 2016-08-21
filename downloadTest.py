#! python3
#filename.py
#
''' Download all ENT articles from the hearing journal'''
#Import requests for downloading, os to make directory, re to match titles
import requests, os, time, threading, multiprocessing
import bs4

#Website to load and directory to save files in
pageUrl = 'http://journals.lww.com/thehearingjournal/pages/author.aspx?firstName=Hamid&middleName=R.&lastName=Djalilian'
pdfDirectory = r'.\\HJ_Download_Test'

def check_directory (pdfDirectory):
    #Check to see if article folder exists.  If not then create it
    if os.path.exists(pdfDirectory):
        outcome = True
    else:
        os.makedirs(pdfDirectory)
        outcome = False
    return outcome
    
def load_soup(pageUrl):
    #Download page as a stream.  Create soup object using lxml parser
    res = requests.get(pageUrl, stream=True)
    soup = bs4.BeautifulSoup(res.text, "lxml")
    return (res, soup)
    
def load_pdf_urls(soup):   
    match = soup.find_all("a", class_="ejp-standard-pdf")
    return [link.get('href') for link in match] 

def save_pdf(pdfLocation, article):
    #Create .pdf file and save content from website to file
    with open(pdfLocation, "wb") as f:
        f.write(article.content)
        
def download_pdf(res,link,pdfLocation):
        res = requests.get(link)
        with open(pdfLocation, "wb") as f:
            f.write(res.content)
            print('Article Saved')
        
def create_files_processes(res, links, pdfDirectory):
    downloadProcesses = []
    for i, link in enumerate(links):
        pdfLocation = pdfDirectory + r'\Article_{}.pdf'.format(i)
        downloadProcess = multiprocessing.Process(target=download_pdf, args=(res, link, pdfLocation))
        downloadProcesses.append(downloadProcess)
        downloadProcess.start()
        print('Article {} downloading'.format(i))
    for downloadProcess in downloadProcesses:
        downloadProcess.join()
    print ('All files downloaded')

def create_files_threaded(res, links, pdfDirectory):
    downloadThreads = []
    for i, link in enumerate(links):
        pdfLocation = pdfDirectory + r'\Article_{}.pdf'.format(i)
        downloadThread = threading.Thread(target=download_pdf, args=(res, link, pdfLocation))
        downloadThreads.append(downloadThread)
        downloadThread.start()
        print('Article {} downloading'.format(i))
    for downloadThread in downloadThreads:
        downloadThread.join()
    print ('All files downloaded')
    
def create_files(res, links, pdfDirectory):
    for i, link in enumerate(links):
        pdfLocation = pdfDirectory + r'\Article_{}.pdf'.format(i)
        download_pdf(res,link,pdfLocation)
        print('Article {} downloading'.format(i))
    print ('All files downloaded')
    
    
def load_all(pageUrl):
    print ('Downloading html and creating soup object...', end="")
    res, soup = load_soup(pageUrl)
    print ('done')

    print('Finding all .pdf articles...', end=" ")
    links = load_pdf_urls(soup)
    print('{} .pdf links found.'.format(len(links)))

    return (res, links)
        
if __name__=='__main__':
    #Create file to put .pdfs in if necessary
    print('Checking file directory...', end="")
    if check_directory(pdfDirectory):
        print('file folder already created')
    else:
        print('file folder created')
    
    #load website, pdf urls and titles        
    res, links = load_all(pageUrl) 
    
    #For each .pdf link, check if it exists and save it of not.
    startTime = time.time()
    create_files_processes(res, links, pdfDirectory)
    endTime = time.time()
    print ('Program took {} to execute'.format(endTime-startTime))