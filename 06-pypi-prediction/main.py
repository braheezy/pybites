#!venv/bin/python
'''
Use Wayback machine to fetch RSS feeds for published packages
for time period. 

Use algorithm to extrpolate when n-th package is published.

Should allow any time period to be chosen
    "Use data from date1 to date2 to predict"

Any algorithm (strategy design pattern)

Any number package in the future:
    "Predict the 10000, 99999, 500 to be published"

Program flow:
    Get parameters from above.
    Default:
        Time period: jan 1 2016 - dec 31 2016
        algo: simple average
        n: 100,000

    Data collection:
        Grab RSS feeds for time period
        Parse rss feed for info and add to a data structure
            making sure to avoid duplicates
        
    Apply algo to data collection

    Return result

As is, this program sucks at predicting the n-th package, but it was
fun to write.
'''
import sys
import re
import time
import string
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint

import requests
import feedparser
from bs4 import BeautifulSoup


def report(params):
    '''
    params: dict of strings to use in nice report for CLI

    report_params = {
        'pkg_n': '100000',
        'dates_asked': ['1/1/2015', '12/31/2017'],
        'dates_used': ['4/5/2016', '12/31/2017'],
        'release_rate': '4.03',
        'curr_pkg_count': '94368',
        'curr_pkg_date': '12/15/2017',
        'pred_hours': '1000',
        'pred_date': '06/15/2018'
    }
    '''
    def box(msg, indent=1, width=None, title=None):
        """Print message-box with optional title.
        From: https://stackoverflow.com/questions/39969064/how-to-print-a-message-box-in-python
        """
        lines = msg.split('\n')
        space = " " * indent
        if not width:
            width = max(map(len, lines))
        box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
        if title:
            box += f'║{space}{title:<{width}}{space}║\n'  # title
            box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
        box += ''.join(
            [f'║{space}{line:<{width}}{space}║\n' for line in lines])
        box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
        return box

    report_text = '''
When will the {pkg_n} package be published?
    Dates asked: {dates_asked[0]} - {dates_asked[1]}
Because of limited availability of wayback archives:
    Dates used: {dates_used[0]} - {dates_used[1]}

Number of RSS analyzed: {num_rss}
Found number of packages released: {found_pkgs}
Release Rate during period used: {release_rate:0.4} packages per hour

Based on PyPi homepage availability:
    Package count on {curr_pkg_date}: {curr_pkg_count}

So, to publish ({pkg_n} - {curr_pkg_count}) pkgs:
'''.format(**params)

    # Create graphic, which should be centered with the above message
    report_graphic = box('{pkg_n}-th package on {pred_date}'.format(**params),
                         title='Prediction')
    print(report_text + '\n\n' + report_graphic)


def analyze(data,
            current_pkg_info,
            future_pkg_count,
            strategy=None,
            rss_data=None):
    '''
    data: list of timestamps each for a package published
    current_pkg_info: tuple of (pkg count, timestamp obtained)
    '''
    # print(
    #     f'analyze params:\n data:{data}\ncurrent_pkg_info:{current_pkg_info}\nfuture_pkg_count:{future_pkg_count}'
    # )

    # Each stategy will give a prediction in hours
    prediction = None
    if strategy is None:
        '''Simple average approach.
        For d samples, calculate rate of publishing, m. Use that to estimate y-th publish.
        y = mx + b
        '''
        # Slope is rise over run
        # Rise: # of pkgs released over time
        # Run: amount of time passed
        rise = len(data)
        # Dates are in timestamp seconds
        run = (data[-1] - data[0]) / 60 / 60
        # print("calculating run as {} - {}".format(
        #     datetime.fromtimestamp(data[-1]), datetime.fromtimestamp(data[0])))
        rate = rise / run
        # print(f'{rate} packages / hour')
        # Prediction is how many hours from current pkg date
        prediction = (future_pkg_count - current_pkg_info[0]) / rate
        # print(f'simple average prediction: {prediction} hrs')
        publish_date = current_pkg_info[1] + timedelta(hours=prediction)
        # print(f"{future_pkg_count}-th package will be published on {publish_date}")
        return (rate, publish_date)
    elif strategy == 'linear-regression':
        '''
        Compute a simple linear regression line (i.e. line of best fit) using Least Squares technique

        x - time
        y - # of packages
        '''
        def least_squares(x, y):
            '''Use least squares method to compute line of best fit'''
            N = len(x)
            sum_x = sum(x)
            sum_y = sum(y)

            sum_x_y = sum(map(lambda pair: pair[0] * pair[1], zip(x, y)))
            sum_x_2 = sum(map(lambda n: n * n, x))

            num = (N * sum_x_y) - (sum_x * sum_y)
            den = (N * sum_x_2) - (sum_x * sum_x)
            slope = num / den

            b = (sum_y - (slope * sum_x)) / N
            return (slope, b)

        temp = rss_data[0]
        pkg_info = fetch_pkg_count([temp])

        y = [pkg_info[0] + i for i in range(0, len(data))]
        line = least_squares(data, y)
        print(f"y = {line[0]}x + {line[1]} is the line of best fit")
        publish_timestamp = (future_pkg_count - line[1]) / line[0]
        print(f"publish_timestamp: {publish_timestamp}")
        publish_date = datetime.fromtimestamp(publish_timestamp)
        print(f"publish_date: {publish_date}")
        return (line[0], publish_date)


def fetch_pkg_count(rss_data):
    '''
    rss_data: List of timestamps, each when a pkg was published

    Return package count for latest date in rss_data
    '''
    # Get a recent timestamp
    print(rss_data[0], rss_data[-1])

    date = datetime.fromtimestamp(rss_data[-1]).strftime(WAYBACK_DATE_FORMAT)
    print(f'converted {rss_data[-1]} to {date}')
    # Fetch available pages nearest to timestamp
    query = {
        # Trial and error showed this was the best URL to use.
        'url': 'pypi.python.org/pypi',
        'output': 'json',
        'from': date,
        'fl': 'timestamp,original'
    }
    try:
        result = requests.get(api, params=query).json()
        # print(result)
    except Exception as err:
        print('Failed to fetch pypi pages from API', err)
        sys.exit()

    return find_count(result[1:])


def find_count(pypi_links, latest=False):
    '''
    pypi_links: (timestamp, URL)s to scrape. Start at end and
    keep scraping until good page is found.

    The challenge is:
        Does the url provide the right information?
        Can we find the package count?
    The pypi host and page layout has changed over years.

    Multiple links because some might be dead or redirect.

    return: tuple (count, timestamp used)
    '''
    if latest:
        pypi_links = pypi_links[::-1]
    for link_info in pypi_links:
        url = "/".join(
            ['http://web.archive.org/web', link_info[0], link_info[1]])
        print('Trying beginging pypi count on: {}'.format(url))
        # Fetch page
        try:
            page = requests.get(url)
        except Exception as err:
            print('failed to fetch page for pkg count', err)
            continue

        soup = BeautifulSoup(page.text, 'html.parser')

        try:
            # Style 1
            # Find id 'content', child class 'section', child <p>, child <strong>
            count = soup.find(id='content').find('strong').string
            break
        except Exception as err:
            print("Could not find pypi count using Style 1", err)

        try:
            # Style 2
            # Find id 'content', child class 'statistics-bar', first child <p> with text ###,### projects
            count = soup.find(id='content').find(class_='statistics-bar').find(
                string=re.compile('projects'))
            # Turn result into number with no commas
            count = re.search(r"(\d+.\d+).+", count)
            count = count.group(1).translate(str.maketrans('', '', ','))
            break
        except Exception as err:
            print("Could not find pypi count using Style 2", err)
            continue
    print(f"Pkg count found: {count}")
    return (int(count), datetime.strptime(link_info[0], WAYBACK_DATE_FORMAT))


def process(rss_urls):
    '''
    feed: List of rss urls to obtain and process
    return: List of timestamps, each for a date a package was pub
    '''
    def convert_date(date):
        match = re.match(r'(.+? \d*:\d*:\d*) GMT', date)
        d = datetime.strptime(match.group(1), "%a, %d %b %Y %H:%M:%S")
        return d.timestamp()

    data = []
    for rss_url in rss_urls:
        print(f'processing {rss_url}')
        # First get raw page
        doc = feedparser.parse(rss_url)
        # Grab section we want
        packages_added = doc['entries']
        # pprint(packages_added)
        # Length of list is number of packages published on this date
        date = convert_date(packages_added[0]['published'])
        data.extend([date for i in range(0, len(packages_added))])
        # Parse out date published
        # data.extend(
        #     [convert_date(package['published']) for package in packages_added])

        # break
    # print(data)
    return data


def get_rss_history(period):
    '''
    period: 2 element array of dates to use [from, to]
            format req by wayback: yyyyMMddhhmmss

            url to fetch: https://pypi.org/rss/packages.xml
    
    return: list of rss urls (strings)
    '''
    # Convert to CORRECT format
    period = [
        datetime.strptime(date, DATE_FORMAT).strftime(WAYBACK_DATE_FORMAT)
        for date in period
    ]
    # DEBUG: Read from file instead of calling again
    url_file = Path('rss_urls.txt')
    if url_file.exists():
        with url_file.open('r') as f:
            urls = f.read()
        return urls.split('\n')

    # Web archive to get all feeds for a time period
    query = {
        'url': 'pypi.org/rss/packages.xml',
        'output': 'json',
        'from': period[0],
        'to': period[1],
        'fl': 'timestamp,original'
    }
    try:
        result = requests.get(api, params=query).json()
    except Exception as err:
        print('Failed to fetch RSS feeds from API', err)
        sys.exit()

    # Build list of indivudual RSS urls to call
    rss_urls = [
        "/".join(['http://web.archive.org/web', r[0], r[1]])
        for r in result[1:]
    ]
    # print(rss_urls)

    # DEBUG
    with url_file.open('w') as f:
        f.write("\n".join(rss_urls))
    return rss_urls


if __name__ == "__main__":
    '''
    Predict when the N-th PyPi package will be published.
    Works on historical data to backtest forecast algos.

    Give a date range to use as a data sample.
    Choose N, which hopefully makes sense for the date range chosen.

    The date range is important. The more recent date (or today) is used 
    to obtain the beginning number of pacakges.
    '''
    # [MM/DD/YYYY, MM/DD/YYYY] or time.time()
    DATE_FORMAT = '%m/%d/%Y'
    period = ['1/1/2018', '12/31/2019']
    # Should be greater than package count for latest date in period
    package_n = 250000

    # Wayback internet archive
    api = 'http://web.archive.org/cdx/search/cdx'
    WAYBACK_DATE_FORMAT = "%Y%m%d%H%M%S"

    # Use internet archive to get a list of urls to RSS feeds
    # on package publishing for the time frame
    rss_urls = get_rss_history(period)
    # Download and parse each RSS for package blurb and date added
    rss_data = process(rss_urls)
    # rss_data are data points representing rate of pkg published (pkg / hr)
    # For prediction calculation, need to know beginning pkg count
    # use same data as calculations (not dates requested)
    begin_pkg_info = fetch_pkg_count(rss_data)
    prediction_info = analyze(sorted(rss_data), begin_pkg_info, package_n,
                              'linear-regression', rss_data)

    # # print(begin_pkg_info)
    # # print(type(begin_pkg_info[0]), type(begin_pkg_info[1]))
    report_params = {
        'pkg_n':
        package_n,
        'dates_asked':
        period,
        'dates_used': [
            datetime.fromtimestamp(rss_data[0]).strftime(DATE_FORMAT),
            datetime.fromtimestamp(rss_data[-1]).strftime(DATE_FORMAT)
        ],
        'num_rss':
        len(rss_urls),
        'found_pkgs':
        len(rss_data),
        'release_rate':
        prediction_info[0],
        'curr_pkg_count':
        begin_pkg_info[0],
        'curr_pkg_date':
        begin_pkg_info[1].strftime(DATE_FORMAT),
        'pred_date':
        prediction_info[1]
    }
    report(report_params)
