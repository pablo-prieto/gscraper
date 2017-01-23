import dryscrape
import re
import random
from time import sleep

def start_google_session(search_term):
    sess = dryscrape.Session(base_url = 'http://www.google.com')
    sess.set_header("User-Agent", "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0")
    sess.set_attribute('auto_load_images', True)
    sess.visit('/')
    q = sess.at_xpath('//*[@name="q"]')
    q.set(search_term)
    q.form().submit()
    return sess

def get_next_page(session, offset=0):
    next_page = session.xpath("//table[@id='nav']//td[last()]//a")[0]['href']
    next_page = next_page.replace('start=10', 'start=%s' % offset)
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
    search_field = session.at_xpath('//*[@name="q"]')
    for i in range(1, random.randrange(5, 10), 1):
        link = random.choice(links)
        print("Simulating hover to random search result") 
        link.hover()
        pause = random.randrange(1, 5)
        print("Sleeping for %s.." % pause)
        sleep(pause)
    
    print("Changing Search Term")
    current_term = search_field.value()
    print("Current Search Term: %s" % current_term)
    search_field.set('Lorem Ipsum')
    sleep(random.randrange(2,5))
    session.render('changed_term.png')
    search_field.set(current_term)
    return session

def scrape(search_term, minpause=8, maxpause=16, start_on=0, append_to=None):
    s = start_google_session(search_term)
    try:
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
            results += get_results(s)
            next_page = get_next_page(s)
            print("Page %s" % i)
            print("Current URL: %s" % s.url())
            print("Extracted %s links so far" % len(results))
            print("Next page: %s" % next_page)
            i +=1
            pause = random.randrange(minpause, maxpause)
            s = simulate_human_interaction(s)
            sleep(2)
            s.render('last_page.png')
            print("Sleeping for: %s..." % pause)
            sleep(pause)
            s.visit(next_page)
            s.render('visited_page.png')
        return results, s
    except ValueError as E:
        print(E)
        return results, s
