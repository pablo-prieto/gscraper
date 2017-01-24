import dryscrape
import re
import random
from time import sleep
from webkit_server import InvalidResponseError

user_agents = ['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
                'Mozilla/5.0 (BlackBerry; U; BlackBerry 9900; en) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.1.0.346 Mobile Safari/534.11+',
                'Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.348; U; en) Presto/2.5.25 Version/10.54',
                'HTC_Touch_3G Mozilla/4.0 (compatible; MSIE 6.0; Windows CE; IEMobile 7.11)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
                'Opera/9.80 (Windows NT 6.1; WOW64; U; pt) Presto/2.10.229 Version/11.62',
                'SamsungI8910/SymbianOS/9.1 Series60/3.0']
                

def start_google_session(search_term, start_on):
    sess = dryscrape.Session(base_url = 'http://www.google.com')
    sess.clear_cookies()
    sess.set_header("user-agent", random.choice(user_agents))
    sess.set_attribute('auto_load_images', True)
    sess.visit('/')
    q = sess.at_xpath('//*[@name="q"]')
    q.set(search_term)
    q.form().submit()
    sess.visit(sess.url()+ '&num=100&start=%s' % start_on)
    return sess

def get_next_page(session, offset=0):
    next_page = session.xpath("//table[@id='nav']//td[last()]//a")[0]['href'] + '&num=100'
    return next_page

def get_results(session):
    results = []
    for link in session.xpath("//div[@id='ires']//a[@href]"):
        href = link['href']
        # print(link)
        # print(href)
        if href.find('webcache') == -1 and href.find('related') == -1 \
        and href.find('#') == -1:
            print(href)
            results.append(href)
    return results

def simulate_human_interaction(session):
    links = session.xpath("//div[@id='res']//a[@href]")
    for i in range(1, random.randrange(2, 6), 1):
        try:
            link = random.choice(links)
            print("Simulating hover to random search result") 
            link.hover()
            pause = random.randrange(1, 5)
            print("Sleeping for %s.." % pause)
            sleep(pause)
        except InvalidResponseError:
            print("Unable to hover. Skipping...")
            continue
    results_to_visit = random.randrange(1, 5)
    
    print("Randomly visiting %s results" % results_to_visit)
    origin_url = session.url()
    for i in range(0, results_to_visit, 1):
        links = [i for i in session.xpath("//div[@id='res']//a[@href]") if i['href'].find('#') == -1 and i['href'].find('webcache') == -1 and i['href'].find('http') != -1]
        try:
            result_to_visit = random.choice(links)
        except IndexError:
            print("Empty SEQ")
            break
        print("Click on: %s" % result_to_visit['href'])
        try:
            result_to_visit.click()
        except InvalidResponseError:
            print("Unable to click, skipping...")
            continue
        pause = random.randrange(10, 30)
        print("Simulating visualization for %s secs..." % pause)
        sleep(pause)
        try:
            session.render('visit_%s.png' % i)
        except InvalidResponseError as E:
            print(E)
        sleep(1)
        session.render("return_to.png")

    print("Returning to search results...")
    session.exec_script('history.back()')
    session.render('return_to.png')
    sleep(1)
    search_field = session.at_xpath('//*[@name="q"]')
    print("Changing Search Term")
    current_term = search_field.value()
    print("Current Search Term: %s" % current_term)
    search_field.set('Lorem Ipsum')
    print("Changing page")
    search_field.form().submit()
    sleep(random.randrange(2,5))
    session.render('changed_term.png')
    search_field = session.at_xpath('//*[@name="q"]') 
    search_field.set(current_term)
    search_field.form().submit()
    return session

def scrape(search_term, minpause=8, maxpause=16, start_on=0, append_to=None, filename='output.txt'):
    try:
        of = open(filename, 'w')
        s = start_google_session(search_term, start_on)
        if append_to is not None:
            print("Will append to existing result list. Current length: %s" % len(append_to) )
            results = append_to
        else:
            results = []
        next_page = ''
        i = 1
        s.render('start_page.png')
        while next_page != get_next_page(s):
            s.render('current_page.png')
            if start_on > 0 and i == 1:
                next_page = get_next_page(s)
                s.visit(next_page)
                print("Starting from result %s." % start_on)
                continue
            extracted_urls = get_results(s)
            for url in extracted_urls:
                of.write(url + '\n')
                results.append(url)
            next_page = get_next_page(s)
            print("PAGE %s" % i)
            print("CURRENT URL: %s" % s.url())
            print("EXTRACTED %s LINKS SO FAR" % len(results))
            print("NEXT PAGE: %s" % next_page)
            i +=1
            pause = random.randrange(minpause, maxpause)
            s = simulate_human_interaction(s)
            s.render('last_page.png')
            print("SLEEPING FOR: %s..." % pause)
            sleep(pause)
            if i % 5 == 0:
                print("---- LONG PAUSE ----")
                print("Pausing for 10 minutes.")
                sleep(600)
                s.clear_cookies()
                print("Cookies cleared")
                s.set_header("user-agent", random.choice(user_agents))
                print("User-Agent changed")
            print("LOADING NEXT PAGE: %s" % next_page)
            s.visit(next_page)
            s.render('visited_page.png')
        of.close()
        return results, s
    except IndexError as E:
        print(E)
        of.close()
        print(s.url())
        return results, s
    
