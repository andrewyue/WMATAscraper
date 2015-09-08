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

def parseDelays(descriptions):
    # take an entry in the service record and parse out some pertinent information:
    # 1) was it a delay, an expressed train, or something else?
    # 2) what line was it on?
    # 3) what was the delay incurred?
    colors = ['red', 'blue', 'yellow', 'green', 'orange', 'silver']
    delay = []
    cause = []
    line = []
    exp = 0
    dl = 0
    dl_by_line = {'red' : 0, 'blue' : 0, 'yellow' : 0, 'green' : 0, 'orange' : 0, 'silver' : 0}
    esch = ('expressed', 'adherence')
    for description in  descriptions:
        # TY for bad typesetting WMATA
        description = description.lower()
        description = description.replace('.',' ')
        description = description.replace(',',' ')
        description = description.replace('-', ' ')
        description = description.replace('minutes',' minute')
        description = description.replace('  ', ' ')
        if any(s in description for s in esch):
            delay.append(0)
            exp += 1
        elif('minute' in description):
            try:
                delay.append(int(description.split()[description.split().index('minute')-1]))
            except ValueError:
                delay.append(0)
            dl += 1
        else:
            delay.append('')
        if any(s in description for s in esch):
            cause.append('expressed')
        elif('not operate' in description):
            cause.append('did not operate')
        elif('equipment' in description):
            cause.append('equipment problem')
        elif('brake' in description):
            cause.append('brake problem')
        elif('door' in description):
            cause.append('door problem')
        elif('signal' in description):
            cause.append('signal problem')
        elif('operational' in description):
            cause.append('operational problem')
        elif('track' in description):
            cause.append('track problem')
        else:
            cause.append('misc') 
        if any([color in description.split() for color in colors]):
            # please forgive me for this code
            colorBool = [index for index, value in enumerate([color in description.split() for color in colors]) if value == True]
            color = colors[colorBool[0]]
            line.append(color)
            dl_by_line[color] += 1
        else:
            line.append('')
    return delay, cause, line, dl, exp, dl_by_line

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

# set up the lists, numbers, and dict to catch the output
delay = []
cause = []
line = []
num_delays = 0
num_exp = 0
delay_by_line = {}

# fill em up
delay, cause, line, num_delays, num_exp, delay_by_line = parseDelays(delayMSG)

# ready the dataframe
df_dict = {'delay' : delay, 'cause' : cause, 'message' : delayMSG, 'timestamp' : delayTime, 'line' : line}
df = pd.DataFrame(df_dict)
df.timestamp = pd.to_datetime(df.timestamp)
df.index = df.timestamp
df = df.drop('timestamp',axis=1)

# and write it to a csv
df.to_csv('test.csv',encoding='utf-8')