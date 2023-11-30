from selenium import webdriver
import time

# Start a new instance of Chrome browser
driver = webdriver.Chrome()  # Replace with your path to chromedriver

# List of TikTok links to navigate to

f = open('raminLinks11-16.txt', 'r')
lines = f.readlines()
with open('11-16Out.txt', 'w+') as wout:
    for l in lines:
        # driver.get('https://www.tiktok.com/login')
        print("Starting url:")
        print(l)
        driver.get(l)
        time.sleep(5)  # Wait for 5 seconds to let the page load and potentially redirect
        final_url = driver.current_url
        print(final_url)
        wout.write(final_url + '\n')


driver.quit()