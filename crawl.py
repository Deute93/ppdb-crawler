from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def no_space(text):
   text1 = re.sub('&nbsp; | &nbsp;| \n|\t|\r', '', text)
   text2 = re.sub('\n\n', '', text1)
   return text2


def getDnaLine(dnaStr,driver):
    # driver = webdriver.PhantomJS('/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs')
    driver.get('http://ppdb.agr.gifu-u.ac.jp/ppdb/cgi-bin/display.cgi?organism=At&gene=' + dnaStr)
    targetStr = ""
    try:
        iframes = driver.find_elements_by_css_selector('iframe')
        # for iframe in iframes:
        #    print(iframe.get_attribute('name'))
        driver.switch_to.frame(iframes[0])
        # id가 locus tag를 10초 내에 검색, 그렇지 않으면 timeoutexception 발생
        element = WebDriverWait(driver, 10).until(
            # By.ID 는 fvtti0 ID로 검색, By.CSS_SELECTOR 는 CSS Selector 로 검색
            EC.presence_of_element_located((By.ID, "fvtti0"))
        )
        str = driver.page_source
        str2 = bs(str, 'html.parser')
        nav_b = str2.find_all("nobr")
        # print("[!!!5] : " , nav_b[5])
        iter = 2;
        while iter<15:
            targetStr = nav_b[iter].get_text("", strip=True)
            targetStr=no_space(targetStr)
            if((targetStr.startswith('A') or targetStr.startswith('C') or targetStr.startswith('G') or targetStr.startswith('T')) and len(targetStr) > 900) :
                return targetStr[:1000]
            else:
                iter = iter+1
    except TimeoutException:
        print("해당 페이지에 locus tag 을 ID 로 가진 태그가 존재하지 않거나, 해당 페이지가 10초 안에 열리지 않았습니다.")

    finally:
        return targetStr[:1000]

driver = webdriver.Chrome()
ofile= open("text.txt",'r')
urls = []
while True:
    line = ofile.readline()
    if not line: break
    print(">"+line[:-1])
    urls.append(line)

count = 1
dnalines =[]
for url in urls :
    dnalinestr = getDnaLine(url,driver)
    dnalines.append(">"+url)
    dnalines.append(dnalinestr+"\n")
    if count% 500 == 0 :
        ifile = open("lines_" + str(count) +".txt", 'w')
        for line in dnalines :
            ifile.write(line)
        dnalines.clear();
        ifile.close()
    count = count + 1
ifile = open("lines_" + str(count) + ".txt", 'w')
for line in dnalines:
    ifile.write(line)
dnalines.clear();
ofile.close()
driver.quit()
