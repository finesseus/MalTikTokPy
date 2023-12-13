
import os
import subprocess
import multiprocessing
import threading
import time
from db import create_session, setup_database
from queue import Queue, Empty
from dbReadOperationsNew import get_accounts_ready_to_scrape, get_post
from run_scraper import run_scraper



start_scrape_date = '2023-11-29'
# 28
end_scrape_date = '2023-12-02'
os.environ['end_scrape_date'] = end_scrape_date
os.environ['start_scrape_date'] = start_scrape_date

num_scrapers = 1

def record_num_sleeping(numsleeping):
    with open('master-output.txt', 'a') as file:
        file.write(f'NUM SLEEPING: {numsleeping}\n')


def make_worker(id_num, get_videos, proc_id):
    # Start subprocess and redirect output to file
    if get_videos:
        with open(f'subpOutputs/{id_num}.txt', 'a') as output_file:
            proc = subprocess.Popen(
                    [run_scraper, start_scrape_date, end_scrape_date],
                    text=True,
                    stdout=output_file,
                    stderr=subprocess.STDOUT
            )
    else:
        with open(f'subpOutputs/{id_num}.txt', 'a') as output_file:
            proc = subprocess.Popen(
                    [run_scraper, start_scrape_date, end_scrape_date],
                    text=True,
                    stdout=output_file,
                    stderr=subprocess.STDOUT
            )
    return proc

def main():

    job_list = []

    for i in range(num_scrapers):
        job_list.append({
            'id': i,
            'proc': None,
            'stage': 'account',
            'fail_count': 0
        })

    while True:

        for worker in job_list:
            if worker['proc'] is None and worker['stage'] == 'account':
                worker['proc'] = make_worker(worker['id'], False, worker.id)


main()