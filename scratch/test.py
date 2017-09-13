import bs4

with open("test.htm", encoding='cp1252') as fil:
    txt = fil.read()
    html = bs4.BeautifulSoup(txt, 'html.parser')

img = html.new_tag('img', src='foobar')
html.body.append(img)

with open("test.htm", "w+") as fil:
    fil.write(str(html))
