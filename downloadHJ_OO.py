#! python3
# downloadHJ_OO.py
# Import requests for downloading, os to make directory, re to match titles
# Import beautiful soup for finding articles and titles
import requests
import os
import re
import bs4


class hjWebScraper:
    '''Save .pdf ENT articles from the HearingJournal.com
       Use self.scrape() to scrape articles from the website

       Attributes:
           PAGE_URL(string): static website address of articles.\n
           PDF_DIRECTORY(r'string'): static folder path to save .pdfs to.\n

           website(request object): downloaded website object.\n
           soup(soup object): beautiful soup object from website text.\n
           matches(list): list of pdf urls.\n
           mainTitle(list): list of .pdf article titles.\n
    '''

    PAGE_URL = 'http://journals.lww.com/thehearingjournal/pages/author.aspx?firstName=Hamid&middleName=R.&lastName=Djalilian'
    PDF_DIRECTORY = r'.\\HJ_ENT_Articles_OO'

    def __init__(self):
        '''Initialize the hjWebScraper object.'''
        self.website = requests.get(hjWebScraper.PAGE_URL, stream=True)
        self.soup = bs4.BeautifulSoup(self.website.text, "lxml")
        self.matches = []
        self.mainTitle = []

    def check_directory():
        '''Check if article folder exists.  If not then create it.'''
        if os.path.exists(hjWebScraper.PDF_DIRECTORY):
            return True
        os.makedirs(hjWebScraper.PDF_DIRECTORY)
        return False

    def load_titles(self):
        '''Find all article titles and append to self.mainTitle list.

           Attributes:
               titles(match): list of divs containing article titles./n
               regex(regex): compiled regex object used to find part of title./n
               description(string): desired text to use from title./n
        '''
        titles = self.soup.find_all("div", id="ej-featured-article-info")
        for title in titles:
            regex = re.compile(r"""(Through\sthe\sOtoscope:\s\s)?   #optional title
                                 (Clinical\sConsultation:\s\s)?  #optional title
                                 (Symptoms?:\s\s?)?             #optional title
                                 (.*)?                  #title we want""", re.VERBOSE)
            # select 4th regex group as file title
            description = regex.search(title.a.string).group(4)
            # get rid of undesired characters in the title
            description = description.replace(" ", "_").replace(
                ",", "").replace("-", "_").replace("__", "_")
            self.mainTitle.append(description)

    def load_pdf_urls(self):
        ''' Create list of .pdf urls.

            Attributes:
                match(match object): found <a> tags in html object./n

            Returns:
                list of .pdf 'href' links in the match object.
        '''
        match = self.soup.find_all("a", class_="ejp-standard-pdf")
        return [link.get('href') for link in match]

    def __save_pdf(self, pdfFileName, link):
        '''Save .pdf's to file.'''
        # download pdf using requests module
        pdf = requests.get(link)
        # Create .pdf file and save binary content to file.
        with open(pdfFileName, "wb") as f:
            f.write(pdf.content)

    def load_all(self):
        '''Load .pdf urls and titles.'''
        print('Finding all .pdf articles...', end=" ")
        self.matches = self.load_pdf_urls()
        print('{} .pdf links found.'.format(len(self.matches)))

        print('Finding all article titles...', end=" ")
        self.load_titles()
        print('{} titles found\n'.format(len(self.mainTitle)))

    def create_files(self):
        '''loop through all .pdf links in matches and save .pdf to file.'''
        for counter, link in enumerate(self.matches, start=1):
            # create item number starting at most recent
            itemNum = len(self.matches) + 1 - counter
            # check to see if the article is already saved.  Skip if it is.
            if os.path.isfile(hjWebScraper.PDF_DIRECTORY + r'\{}_{}.pdf'.format(itemNum, self.mainTitle[counter - 1])):
                print('Skipping article {}, already saved...\n'.format(itemNum))
                continue
            print('Downloading article {} ...'.format(itemNum))
            # generate file path and save the file
            self.__save_pdf(hjWebScraper.PDF_DIRECTORY +
                            r'\{}_{}.pdf'.format(itemNum, self.mainTitle[counter - 1]), link)
            print('Article {} has been saved!\n'.format(itemNum))
        print('Finished.  {} scraped pdf files in directory.'.format(counter))

    def scrape(self):
        '''Main method of class.  Checks if directory is made, loads files, saves them.'''
        print('Checking file directory...', end="")
        if self.check_directory:
            print('file folder already created')
        else:
            print('file folder created')
        self.load_all()
        self.create_files()

if __name__ == '__main__':
    hjWebScraper().scrape()
