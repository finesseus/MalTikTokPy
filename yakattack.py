import os
import requests

# Set the proxy

hur = set()
for i in range(100):
    print(i)
    proxy_url = "http://brd-customer-hl_b6481680-zone-datacenter_proxy1_tt:sznl2982fvhs@brd.superproxy.io:22225"
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url

    # Test the IP
    response = requests.get("https://httpbin.org/ip")
    
    for l in response.text.split('"'):
        if '.' in l:
            hur.add(l)
            break

print(len(hur))