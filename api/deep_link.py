import requests
import json
import logging

def create_short_link(product_id: int, quantity: int):
    url = "https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key=AIzaSyCM8aGGguAm5fJsaCf7CFePUtL8qsDp9sk"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Xây dựng link động với productId và quantity
    product_link = f"https://apis-public.congtrinhviettel.com.vn/aio/productId={product_id}/quantity={quantity}"
    
    # Dữ liệu JSON cho request
    data = {
        "dynamicLinkInfo": {
            "domainUriPrefix": "https://aioapp.page.link",
            "link": product_link,  # Sử dụng link động
            "androidInfo": {
                "androidPackageName": "com.viettel.aioapp"
            },
            "iosInfo": {
                "iosBundleId": "com.viettel.aioapp",
                "iosAppStoreId": "6447238511",
                "iosIpadBundleId": "com.viettel.aioapp"
            },
            "socialMetaTagInfo": {}
        },
        "suffix": {
            "option": "SHORT"
        }
    }

    # Gửi POST request tới API
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print("Short link created successfully!")
            return response.json()
        else:
            print(f"Failed to create short link. Status code: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        logging.error(f"DEEP LINK: Failed to create short link. Error: {e}")
        return None

if __name__ == "__main__":
    product_id = 11111111
    quantity = 10
    short_link_response = create_short_link(product_id, quantity)

    if short_link_response:
        print("Short link:", short_link_response.get('shortLink'))