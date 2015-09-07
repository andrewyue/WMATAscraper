from bs4 import BeautifulSoup
import requests

#BASE = 'http://wmata.com/rail/service_reports/'

#'http://wmata.com/rail/service_reports/viewReportArchive.cfm'
#links = soup.find("ul", "links2")

def getDelays(URL):
    r = requests.get(URL)
    soup = BeautifulSoup(r.text,'html')
    div = soup.find('div','internal-box2-inner')
    delays = [p for p in div.findAll('p')]
    return delays[:-3]
