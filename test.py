from selenium import webdriver
import time

#url="https://mobile.twitter.com/ars_almal/status/1184867928530808834"
#url="https://mobile.twitter.com/ars_almal/status/1185513726109044738"
#url="https://mobile.twitter.com/ars_almal/status/1185567555458519043"
url="https://mobile.twitter.com/mkZH0740/status/1176654590453796870"

driver=webdriver.Chrome()
driver.get(url)
time.sleep(2)
mainclass=driver.find_element_by_css_selector("section")
#driver.execute_script("window.scrollTo(0,-10000)")
this=driver.find_element_by_css_selector("section>div>div>div>:nth-last-child(2)")
this.screenshot("loc.png")
height=this.size['height']
print(height)
driver.execute_script("window.scrollBy(0,-"+str(height)+")")
mainclass.screenshot("test.png")


