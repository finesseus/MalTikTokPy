from bs4 import BeautifulSoup

html_content = open('finusfollowers.txt', 'r').read()

soup = BeautifulSoup(html_content, 'html.parser')

# Find all <li> elements
list_items = soup.find_all('li')

# Extract unique IDs
usernames = []
for li in list_items:
    user_info_div = li.find('div', class_='tiktok-15pr20e-DivUserInfo')
    if user_info_div:
        unique_id_p = user_info_div.find('p', class_='tiktok-swczgi-PUniqueId')
        if unique_id_p:
            usernames.append(unique_id_p.text)
    
# exit()
print(len(usernames))
print(usernames[0])
input()
with open('newAdds.txt', 'w+') as dddd:
    for u in usernames:
        dddd.write(u + '\n')