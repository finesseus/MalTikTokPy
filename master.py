
from main import scrape_video
import os
import subprocess
import threading
import time
from db import create_session, setup_database
from queue import Queue, Empty


start_scrape_date = '2023-11-29'
# 28
end_scrape_date = '2023-12-02'
os.environ['end_scrape_date'] = end_scrape_date
os.environ['start_scrape_date'] = start_scrape_date

num_scrapers = 20

def main(max_processes, max_bench_size, bench_time, pause_time):
    subprocess_queue = Queue()
    for i in range(max_processes):
        sess = create_session()
        base = setup_database(sess)

# Parameters
max_processes = 20
max_bench_size = 15
pause_time = 20 * 60

main(max_processes, max_bench_size, pause_time)