import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CrawlerWebsite:
    def __init__(self, url: str):
        """
        Khởi tạo một số thông tin cần thiết cho việc crawl dữ liệu từ trang web.
        """
        self.url = url
        self.WEBDRIVER_DELAY_TIME_INT = 10
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.headless = True
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)
        self.wait = WebDriverWait(self.driver, self.WEBDRIVER_DELAY_TIME_INT)
        self.store_products = []

    def crawl_info_product(self) -> pd.DataFrame:
        """
        Truy cập vào trang web và lấy thông tin sản phẩm.
        1. Lấy  danh sách tất cả các sản phẩm thông có trong trang web thông qua thẻ "ul.listproduct > li"
        2. Truy cập vào từng thẻ và chuyển qua link web sản phẩm đó.
        3. Lấy ra tên sẩn phẩm qua thẻ 'product-name'.
        4. Lấy giá sản phẩm qua thẻ 'bs_price'(giá đang sale) hoặc 'box-price' (giá không sale). Tùy thuộc vào giá sale hay không sale thì html sẽ khác.
        5. Lấy ra từng thông số kỹ thuật của sản phẩm qua thẻ 'ul.text-specifi.active > li'.
        6. Lưu thông tin sản phẩm vào store_products.
        """

        self.driver.get(self.url) 
        listproduct_items = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.listproduct > li")))
        for idx in tqdm(range(min(10, len(listproduct_items)))):  # Chỉ lấy 10 sản phẩm
            print(idx)
            """Đoạn này tìm tất cả các thẻ <li> là con trực tiếp của <ul> có class "listproduct".
            Dấu > trong CSS selector chỉ định quan hệ cha-con trực tiếp.
            """
            listproduct_items = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.listproduct > li"))) # cần chờ cho đến khi tất cả các phần tử được load xong, nếu không sẽ báo lỗi
            li_item = listproduct_items[idx]
            a_item = li_item.find_element(By.CSS_SELECTOR, "a")
            href_sub_product = a_item.get_attribute('href')
            print(href_sub_product)

            try:
                self.driver.get(href_sub_product)

                product_name = self.driver.find_element(By.CLASS_NAME, "product-name").find_element(By.TAG_NAME, "h1").text
                product_name = product_name.strip().lower().replace("máy lạnh", "điều hòa")
                try:
                    # lấy giá sản phảm đang sale 
                    box_info_product = self.driver.find_element(By.CLASS_NAME, "box_saving.v2.olgr.twoprice")
                    product_price = box_info_product.find_element(By.CLASS_NAME, "bs_price").find_element(By.TAG_NAME, "strong").text
                except:
                    # lấy giá sản phẩm không sale
                    box_info_product = self.driver.find_element(By.CLASS_NAME, "box04.box_normal ")
                    product_price = box_info_product.find_element(By.CLASS_NAME, "box-price").find_element(By.TAG_NAME, "p").text
                
                print(product_name, product_price)

                # lay thong tin san pham
                store_specification = {}
                specification_items = self.driver.find_elements(By.CSS_SELECTOR, "ul.text-specifi.active > li")
                for item in specification_items:
                    try:
                        key = item.find_element(By.XPATH, ".//aside[1]/strong").text.replace(":", "")
                    except:
                        key = item.find_element(By.XPATH, ".//aside[1]/a").text
                    try:
                        value = item.find_element(By.XPATH, ".//aside[2]/a").text.replace(":", "")
                    except:
                        value = item.find_element(By.XPATH, ".//aside[2]/span").text
                    store_specification[key] = value
                
                specification_info = "\n".join([f"{key}: {value}" for key, value in store_specification.items()])
                product_info = {
                    "product_name": product_name,
                    "product_price": product_price,
                    "specifications": specification_info
                }
                self.store_products.append(product_info)

                self.driver.back()
            except Exception as e:
                print(e)
        #  store product info to dataframe
        df = pd.DataFrame(self.store_products)
        df.to_csv("data/data_dienmayxanh.csv", index=True)
        
        return df
    
if __name__ == "__main__":
    crawler = CrawlerWebsite(url="https://www.dienmayxanh.com/may-lanh-midea")
    df = crawler.crawl_info_product()