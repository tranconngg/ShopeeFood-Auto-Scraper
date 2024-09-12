from selenium.webdriver.common.by import By
import time
from concurrent.futures import ThreadPoolExecutor
from crawler.get_driver import get_driver
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def crawl_restaurant_details_defind(links, data_details, driver_id):
    driver = get_driver()

    for row in links:
        promotion, link = row[1], row[2]
        driver.get(link)
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.detail-restaurant-info'))
                )
        except Exception as e:
                print(f"Lỗi khi chờ đợi sản phẩm: {e}")

        try:
            name_res = driver.find_element(By.CSS_SELECTOR, 'h1.name-restaurant').text
        except:
            name_res = ''

        try:
            kind_res = driver.find_element(By.CSS_SELECTOR, 'div.kind-restaurant').text
        except:
            kind_res = ''

        try:
            address = driver.find_element(By.CSS_SELECTOR, 'div.address-restaurant').text
        except:
            address = ''

        try:
            status_element = driver.find_element(By.CSS_SELECTOR, 'div.opentime-status .stt.online')
            status = status_element.get_attribute('title')
        except:
            status = "Đóng cửa"

        try:
            open_time = driver.find_element(By.CSS_SELECTOR, 'div.status-restaurant .time').text
        except:
            open_time = ""

        try:
            cost_res = driver.find_element(By.CSS_SELECTOR, 'div.cost-restaurant').text
        except:
            cost_res = ""

        try:
            full_star = driver.find_elements(By.CSS_SELECTOR, 'div.rating .stars .full')
            half_star = driver.find_elements(By.CSS_SELECTOR, 'div.rating .stars .half')
            star = len(full_star) + 0.5 if len(half_star) > 0 else len(full_star)
        except:
            star = ""

        try:
            number_rating = driver.find_element(By.CSS_SELECTOR, 'div.rating .number-rating').text
        except:
            number_rating = ""

        restaurant_dict = {
            'name_res': name_res,
            'kind_res': kind_res,
            'address': address,
            'promotion': promotion,
            'star': star,
            'number_rating': number_rating,
            'status': status,
            'open_time': open_time,
            'cost_res': cost_res,
            'store_url': link
        }

        data_details.append(restaurant_dict)
    
    driver.quit()
    return data_details

def crawl_restaurant_details_thread(**kwargs):
    data_links = kwargs['ti'].xcom_pull(task_ids='crawl_list_restaurant')

    middle_index = len(data_links) // 2
    data = []

    executors_list = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        executors_list.append(executor.submit(crawl_restaurant_details_defind, data_links[:middle_index], data, "driver1"))
        executors_list.append(executor.submit(crawl_restaurant_details_defind, data_links[middle_index:], data, "driver2"))
    
    for task in executors_list:
        task.result()
  
    fieldnames = ['name_res', 'kind_res', 'address', 'promotion', 'star', 'number_rating', 'status', 'open_time', 'cost_res', 'store_url']
    with open('/opt/airflow/dags/data/raw_restaurant_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)