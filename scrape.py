"""Scrape gradschoolshopper.com to gather data as CSVs"""
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = 'https://www.gradschoolshopper.com/gradschool/'
RANK_URL = BASE_URL + 'rankby.jsp'
BROWSE_URL = BASE_URL + 'browseby.jsp'

N_RANK = 6
N_BROWSE = 7

DATA_DIR = 'data'
if not os.path.isdir(DATA_DIR):
    os.makedirs(DATA_DIR)

def parse_table(r):
    """
    Parse the webpage and convert table contents into a pandas DataFrame.

    Args:
        r (requests.get): GET request response for the webpage

    Returns:
        table_title (str): Title of the table
        df (pd.DataFrame): DataFrame populated with data

    """
    soup = BeautifulSoup(r.content, 'html.parser')
    table_title = soup.h1.text.split(':')[-1].strip()
    col_names = []
    colskip = 0
    for i, tr in enumerate(soup.table.thead.findAll('tr')):
        if colskip > 0:
            row_col_names = [''] * colskip
        else:
            row_col_names = []
        for th in tr.findAll('th'):
            if th.text == u'\xa0':
                continue
            if 'colspan' in th.attrs:
                row_col_names += [th.get_text(' ')] * int(th.attrs['colspan'])
            else:
                row_col_names.append(th.get_text(' '))
            if 'rowspan' in th.attrs:
                colskip += 1

        col_names.append(row_col_names)
    col_names = list(map(' '.join, zip(*col_names)))
    col_names = list(map(lambda x: x.strip(), col_names))

    data = []
    for row in soup.table.findAll('tr'):
        row_data = [td.text.strip() for td in row.findAll('td')][1:]
        row_data = [x.replace(u'\xa0', '') for x in row_data]
        if len(row_data) > 0:
            data.append(row_data)

    df = pd.DataFrame(data, columns=col_names)
    return table_title, df

for i in range(1, N_RANK+1):
    r = requests.get(RANK_URL, params={'q': i})
    title, df = parse_table(r)
    fname = '_'.join(title.replace(',', '').split(' ')).lower() + '.csv'
    df.to_csv(os.path.join(DATA_DIR, fname))

for i in range(1, N_BROWSE+1):
    r = requests.get(BROWSE_URL, params={'q': i})
    title, df = parse_table(r)
    fname = '_'.join(title.replace(',', '').split(' ')).lower() + '.csv'
    df.to_csv(os.path.join(DATA_DIR, fname))
