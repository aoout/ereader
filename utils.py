from bs4 import BeautifulSoup

def add_css_to_html(css, html):
    soup = BeautifulSoup(html, 'html.parser')
    style_tag = soup.new_tag('style')
    style_tag.string = css
    soup.head.append(style_tag)
    return str(soup)
