from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from crawler.get_driver import get_driver

def crawl_list_restaurant():
    driver = get_driver()
    driver.get("https://shopeefood.vn/ha-noi/food/deals")

    list_restaurant_data = []

    def wait_for_page_to_load():
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.item-restaurant'))
            )
        except Exception as e:
            print(f"Lỗi khi chờ đợi sản phẩm: {e}")

    def crawl_page():
        stores = driver.find_elements(By.CSS_SELECTOR, '.item-restaurant')
        for store in stores:
            try:
                name = store.find_element(By.CSS_SELECTOR, '.name-res').text
                store_url_ele = store.find_element(By.CSS_SELECTOR, 'a[href]')
                store_url = store_url_ele.get_attribute('href')
                promotion = store.find_element(By.CSS_SELECTOR, '.content-promotion').text
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 2 / 3);")

                list_restaurant_data.append([name, promotion, store_url])
            except Exception as e:
                print(f"Lỗi khi lấy thông tin cửa hàng: {e}")

    wait_for_page_to_load()
    crawl_page()
    # cnt = 0 
    while True:
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'a[href="#"] .icon-paging-next')
            if next_button.get_attribute('class') == 'icon icon-paging-next disabled':  
                break
            next_button.click()
            # cnt += 1
            WebDriverWait(driver, 5).until(EC.staleness_of(next_button))
            wait_for_page_to_load()  
            crawl_page()
        except Exception as e:
            print(f"Lỗi khi chuyển trang hoặc crawl trang: {e}")
            break

    driver.quit()
    return list_restaurant_data
