from src.tiktokapipy.api import TikTokAPI
import random



def transform_proxy_string(proxy_str):
    parts = proxy_str.split(':')
    
    if len(parts) != 4:
        raise ValueError("Invalid proxy string format!")

    host, port, username, password = parts
    transformed = f"http://{username}:{password}@{host}:{port}"
    
    return transformed

def get_random_proxy(filename):
    with open(filename, 'r') as f:
        proxies = f.readlines()
    
    # Choose a random proxy
    chosen_proxy = random.choice(proxies).strip()
    # strip to remove any trailing newline characters
    
    return transform_proxy_string(chosen_proxy)


def makeTikTokApi(comments=False, img_block=False):
    
    # proxy = 'http://brd-customer-hl_b6481680-zone-tt_res_for_tiktokapipy:24jsxu7l3wfi@brd.superproxy.io:22225'

    # profiles no img block
    proxy_profile = 'http://brd-customer-hl_b6481680-zone-datacenter_proxy1_tt:sznl2982fvhs@brd.superproxy.io:22225'

    # comments no img block
    proxy_comments = 'http://brd-customer-hl_b6481680-zone-datacenter_proxy1_tt_comments:78jf7j8ou92r@brd.superproxy.io:22225'

    # profiles img block
    proxy_img_block = 'http://brd-customer-hl_b6481680-zone-datacenter_proxy1_tt_noimg:hm3ty7qe7wjo@brd.superproxy.io:22225'

    # comments img block
    proxy_img_block_comments = 'http://brd-customer-hl_b6481680-zone-datacenter_proxy1_tt_noimg_com:y985tto0uwt8@brd.superproxy.io:22225'

    if comments:
        if img_block:
            proxy = proxy_img_block_comments
        else:
            proxy = proxy_comments
    else:
        if img_block:
            proxy = proxy_img_block
        else:
            proxy = proxy_profile
    
    # proxy = 'http://rjlrdkcg:tuvlyrqkgpi@38.154.227.167:5868'
    # proxy = None
    
    # =======
    # proxy = 'http://brd-customer-hl_b6481680-zone-tt_res_proxy_1-country-us:jdck5fevng4r@brd.superproxy.io:22225'
    # ========
    # proxy = None
    # =====
    # proxy = get_random_proxy('ig19.txt')
    # print(proxy)
    # exit()
    # =====

    # proxy = 'http://brd-customer-hl_b6481680-zone-ig19-gip-18b3a7a4c370000f:lbnpoiik7ofz@brd.superproxy.io:22225'
    # proxy = 'http://brd-customer-hl_b6481680-zone-ig19-gip-18b3a7a4c370002e:lbnpoiik7ofz@brd.superproxy.io:22225
    
    tt = TikTokAPI(proxy=proxy, headless=True)
    return tt
