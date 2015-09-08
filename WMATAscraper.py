from bs4 import BeautifulSoup
import requests
import pandas as pd

# write out a csv file containing every incident from the archive, a timestamp,
# type of delay, line information, station, and delay time (if applicable)

def getLinks(URL):
    BASE = 'http://wmata.com/rail/service_reports/'
    r = requests.get(URL)
    soup = BeautifulSoup(r.text,'html')
    allLinks = soup.find('ul','links2')
    dates = [link.string for link in allLinks.findAll('a')]
    links = [BASE + str(link['href']) for link in allLinks.findAll('a')]
    return zip(dates, links)

def getDelays(URL):
    r = requests.get(URL)
    soup = BeautifulSoup(r.text,'html')
    div = soup.find('div','internal-box2-inner')
    delays = [p.string for p in div.findAll('p')]
    # last three <p></p> instances are junk
    return delays[:-3]

archive='http://wmata.com/rail/service_reports/viewReportArchive.cfm'
datesLinks = getLinks(archive)
delayTime = []
delayMSG = []
for dateLink in datesLinks:
    # pitfalls - entries with embedded hyperlinks, empty entries
    # need to fix more elegantly
    delays = getDelays(dateLink[1])
    for delay in delays:
        try:
            delayTime.append(pd.Timestamp(dateLink[0]+ ' ' + delay.split()[0] + ' ' + delay.split()[1]))
            delayMSG.append(' '.join(delay.split()[2:]))
        except AttributeError:
            pass
        except IndexError:
            pass
        except ValueError:
            pass

df_dict = {'timestamp' : delayTime, 'message' : delayMSG}
df = pd.DataFrame(df_dict)
df.to_csv('~/Projects/WMATAscraper/test.csv')
