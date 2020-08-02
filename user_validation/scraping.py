from django.http import HttpResponse
from requests.compat import quote_plus

def amazon_primary(URL,soup,primary):
    title = soup.find(id="productTitle").text  
    spec = soup.find(id="productDescription").p.text.strip()
    if primary:
        image = soup.find(id="landingImage").get("src")
    else:
        image = None 
    rating = soup.find(class_="a-size-medium a-color-base").text.strip()
    #check deal price or not
    deal_price = soup.find(id="priceblock_dealprice")
    if deal_price is not None:
        price_data = deal_price
    else:
        price_data = soup.find(id="priceblock_ourprice")
    try:
        price_data = price_data.text.strip()
        price = price_data
        price = price[1:len(price)-3].replace(",","").strip() #converting into a number
        price = int(price)
    except Exception as e:
        price = "Unavailable"
        price_data = "Unavailable"
    data = {
        "website":"Amazon",
        "color":"orange",
        "product_url":URL,
        "image":image,
        "price_data":price_data,
        "price":price,
        "rating":rating,
        "title":title.strip(),
        'exist':True,
        'specification':spec
    }
    return data


def flipkart_primary(URL,soup,primary):
    #flipkart data is dynamic
    #set pincode
    try:
            
        if primary:
            image = soup.find(class_="bhgxx2").div.find("img").get("src")
        else:
            image = None

        title = soup.find(class_="_35KyD6").text.strip()
        price_data = soup.find(class_="_3qQ9m1").text.strip()
        price = price_data.replace(",","").replace("₹","").strip()
        price = int(price)
        rating = soup.find(class_="hGSR34").text.strip()+" out of 5"
        data = {
            "website":"Flipkart",
            "color":"blue",
            "product_url":URL,
            "image":image,
            "price_data":price_data,
            "price":price,
            "rating":rating,
            "title":title,
            'exist':True,
            #'specification':spec
        }
    except Exception:
         data = {
        "website":"Snapdeal",
        "color":"blue",
        "price_data":'Unavailable',
        "price":'Unavailable',
        "rating":"Unavailable",
        "title":'Unavailable',
        'exist':False,
        }
    return data

def snapdeal_primary(URL,soup,primary):
    try:
        if primary:
            image = soup.find(class_="cloudzoom").get("src")
        else:
            image = None
            
        title = soup.find(class_="pdp-comp comp-product-description clearfix").find("h1").text.strip()
        price_data = soup.find(class_="payBlkBig").text.strip()
        try:
            spec = soup.find_all(class_="detailssubbox")[1].text.strip()
        except Exception:
            spec = "Not available"
        price = int(price_data.replace(",",""))
        try:
            rating = soup.find(class_="avrg-rating").text[1:4].strip()+" out of 5"
        except Exception as e:
            rating = "No ratings available"
        data = {
        "website":"Snapdeal",
        "color":"red",
        "product_url":URL,
        "image":image,
        "price_data":"₹ "+price_data,
        "price":price,
        "rating":rating,
        "title":title,
        'exist':True,
        'specification':spec
        }
    except Exception as e:
        data = {
        "website":"Snapdeal",
        "color":"red",
        }

    print(data)
    return data



