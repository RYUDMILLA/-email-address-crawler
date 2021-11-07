from selenium import webdriver
import selenium.common.exceptions
#from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
#from bs4 import BeautifulSoup
import time
import csv

#without browser
#options = webdriver.ChromeOptions()
#options.add_argument('headless')

class crawler():
    def __init__(self):
        self.options = Options()
        # self.options.add_argument("headless")
        self.driver = webdriver.Chrome(r"driver_directory\chromedriver.exe")  # chromedriver.exe directory
        self.driver.implicitly_wait(3)


    def extract_links(self, center):
        self.driver.get('https://www.longtermcare.or.kr/npbs/r/a/201/selectLtcoSrch.web?menuId=npe0000000650&zoomSize=')

        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, 'si_do_cd')))
        # expand housing type dropdown using javascript
        dropdown_trigger = self.driver.find_element_by_class_name("ui-icon")
        self.driver.execute_script("arguments[0].click();", dropdown_trigger)
        time.sleep(1)
        # select an option 서울특별시
        dropdown_option = WebDriverWait(self.driver, 15).until( 
            EC.presence_of_element_located((By.XPATH, "//li[text()='서울특별시']")))
        dropdown_option.click()
        time.sleep(2)

        self.driver.find_element_by_name("ltcAdminNm").send_keys(center)

        self.driver.find_element_by_id("btn_search").click()
        time.sleep(0.1)
        
        elements = self.driver.find_elements_by_xpath("//*[@id='ltco_info_list']/tbody//tr")
        links = []
        maps = []
        for element in elements:
            map = element.find_element_by_xpath("./td[11]/a").text
            link = element.find_element_by_xpath("./td[13]/a").get_attribute('href')
            maps.append(map)
            links.append(link)

        next_pages = self.driver.find_elements_by_xpath('//*[@id="main_paging"]//a')
        pages = len(next_pages)
        if next_pages:
            for i in range(pages):
                next_page = self.driver.find_element_by_xpath(f'//*[@id="main_paging"]/a[{i+1}]')
                next_page.click()
                time.sleep(2)
                
                next_elements = self.driver.find_elements_by_xpath("//*[@id='ltco_info_list']/tbody//tr")
                next_links = []
                next_maps = []
                for element in next_elements:
                    map = element.find_element_by_xpath("./td[11]/a").text
                    link = element.find_element_by_xpath("./td[13]/a").get_attribute('href')
                    next_maps.append(map)
                    next_links.append(link)
                maps += next_maps
                links += next_links
                continue          
        
        center_info = {'center':center,'maps':maps,'links':links}
        return center_info

    def extract_emails(self, links):
        emails = []
        names = []  
        for link in links:
            # #open tab
            # self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't') 

            # # Load a page 
            # self.driver.get(link)
            # # Make the tests...

            # # close the tab
            # self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w') 
            self.driver.get(link)
            name = self.driver.find_element_by_xpath("//*[@id='my_blog_vo']/div[1]/div[1]/div[1]/p/span").text
            email = self.driver.find_element_by_xpath('//*[@id="my_blog_vo"]/div[1]/div[1]/div[2]/div/ul/li[4]/dl/dd').text
            if email in emails:
                email = None
            emails.append(email)
            names.append(name)
        center_info = {'emails':emails,'names':names}
        return center_info

    def kill(self):
        self.driver.quit()

    def save_to_file(self, info, out_file, error_file):
        file = open(out_file, mode='a', newline='')
        writer = csv.writer(file)
        error = open(error_file, mode='a', newline='')
        error_writer = csv.writer(error)
        for i in range(len(info['emails'])):
            if info['emails'][i]:
                if info['names'][i].strip() == info['center'].strip():
                    writer.writerow([info['center'], info['emails'][i], info['maps'][i]])
                else:
                    error_writer.writerow([info['names'][i], info['emails'][i], info['maps'][i]])
        file.close()
        error.close()
        return

    def record_error(self, file, center):
        error_log = open(file, "a", newline='')
        error_log.write(center)
        error_log.close()