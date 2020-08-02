from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth#builtin login model
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
import requests
from requests.compat import quote_plus
from .models import Searches
from .scraping import *
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from time import sleep
from .productValidation import ProductValidation
from .models import Monitor
from django.core.mail import send_mail
from django.conf import settings
import matplotlib.pyplot as plt
import numpy as np

# in admin panel visualize data
# pie chart -> shows products count from various sites

AMAZON_SEARCH_URL = "https://www.amazon.in/s?k={}"
FLIPKART_SEARCH_URL = "https://www.flipkart.com/search?q={}"
SNAPDEAL_SEARCH_URL = "https://www.snapdeal.com/search?keyword={}"

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
primary = ""
validate = ProductValidation()
#create headless chrome
options = Options()
options.headless = True
CHROMEDRIVER = r"C:\Users\dileep8417\Downloads\chromedriver-v83.exe"

images_loaded = False

product_data = {
    "amazon":"",
    "flipkart":"",
    "snapdeal":""
}

def title_sanitizer(title):
    #title = title.split()
    #get all the data within the brackets
    option_data = ''
    left_par = [] 
    right_par = []
    updated_title = title
    for i in range(len(title)):
        if(title[i]=='('):
            left_par.append(i)
        if(title[i]==')'):
            right_par.append(i)  #if right came left also came
    new_option = ""
    for i in range(len(left_par)):
         option_data+= title[left_par[i]:right_par[i]+1]+" "
         updated_title = updated_title.replace(title[left_par[i]:right_par[i]+1],'')
         
    return updated_title
    

def signup(req):
    if req.user.id is not None:
        return redirect("/dashboard")
    err = ""
    if req.method=="POST":
        pass1 = req.POST['pass1']
        pass2 = req.POST['pass2']
        email = req.POST['email'].lower()
        #Validation
        #1. check whether email already exist or not
        #2. Validate password size and compare pass1 and 2
        #3. check whether all the fields are null or not
        #Then create_user()
        if(User.objects.filter(username=email)):
            err = "Email ID already exist."
        elif(pass1!=pass2):
            err = "Password not matching"
        elif(len(pass1)<=3):
            err = "Password should be greater than 3 digits"
        else:
            #insert data
            insert = User.objects.create_user(email=email,username=email,password=pass1)
            insert.save()
            return redirect("/login")
        return render(req,"registration.html",{'formtype':"Registration","err":err})
    else:
        return render(req,"registration.html",{'formtype':"Registration"})


def login(req):
    if req.user.id is not None:
        return redirect("/dashboard")
    if req.method=="POST":
        email = req.POST['email'].lower()
        pwd = req.POST['pass']
        err = ""
        user = auth.authenticate(username=email,password=pwd)
        if user is not None:
            auth.login(req,user)
            return redirect("/dashboard")
        err = "Invalid Username or Password"
        return render(req,"login.html",{"err":err})
    else:
        return render(req,"login.html",{'formtype':"Login"})


@login_required(login_url="/login") 
def dashboard(req):
    return render(req,"dashboard.html",{'userid':req.user.id})


def scraping(URL,primary=False):
    if(URL.find("https://")==-1):
        URL = "https://{}".format(URL)
    if len(URL)<10:
        print("-----------------------Error in URL")
        return redirect("/dashboard")
    if URL.find("flipkart")!=-1 and primary:
        driver = webdriver.Chrome(CHROMEDRIVER,chrome_options=options)
        driver.get(URL)
        response = driver.execute_script("return document.documentElement.outerHTML")
        driver.quit()
    else:
        response = requests.get(URL,headers=HEADERS).text
    
    soup = BeautifulSoup(response,features="html.parser")
        
    if URL.find("amazon")!=-1:
        product_data['amazon'] = amazon_primary(URL,soup,primary)
        #flipkart_secondary(data["title"])
    elif URL.find("flipkart")!=-1:
        product_data["flipkart"] = flipkart_primary(URL,soup,primary)
    elif URL.find("snapdeal")!=-1:
        product_data["snapdeal"] = snapdeal_primary(URL,soup,primary)
    else:
        return 0
    return 1

def search(req):
    if req.method=="POST":
        URL = req.POST['search']
        product_data["amazon"] = product_data["flipkart"] = product_data["snapdeal"] = ""
        data = scraping(URL,True)
        if data==0:
            print("-----------------------Error in URL")
            return redirect("/dashboard")
        else:
            if URL.find("amazon")!=-1:
                flipkart_secondary(product_data["amazon"]["title"])
                snapdeal_secondary(product_data["amazon"]["title"])
            elif URL.find("flipkart")!=-1:
                snapdeal_secondary(product_data["flipkart"]["title"])
                amazon_secondary(product_data["flipkart"]["title"])
            elif URL.find("snapdeal")!=-1:
                amazon_secondary(product_data["snapdeal"]["title"])
                flipkart_secondary(product_data["snapdeal"]["title"])
            #print(product_data)
            return render(req,"product.html",{"product_data":product_data,"userid":req.user.id})
    else:
        return redirect("/dashboard")
        


def flipkart_secondary(title):
    search_url = FLIPKART_SEARCH_URL.format(quote_plus(title_sanitizer(title)))
    # print(search_url+"\n\n")
    # driver = webdriver.Chrome(CHROMEDRIVER,chrome_options=options)
    # driver.get(search_url)
    # resp = driver.execute_script("return document.documentElement.outerHTML")
    resp = requests.get(search_url,headers=HEADERS).text
    fsoup = BeautifulSoup(resp,features="html.parser")
    product_exist = validate.flipkart_product_not_found(fsoup)
    if product_exist:
        try:
            product_url = fsoup.find("div",{"class":"_3O0U0u"}).div.div.a.get("href")
            product_url = "https://www.flipkart.com"+product_url    
            scraping(product_url)
            #driver.quit()
        except Exception as e:
            print("Flipkart Err: flipkart_seconday()")
            product_data['flipkart'] = {
        "website":"Flipkart",
        "color":"blue",
        "product_url":"Unavailable",
        "image":None,
        "price_data":"Unavailable",
        "price":"Unavailable",
        "rating":"Unavailable",
        "title":"Unavailable",
        'exist':False,
        #'specification':spec
        }
    else:
        product_data['flipkart'] = {
        "website":"Flipkart",
        "color":"blue",
        "product_url":"Unavailable",
        "image":None,
        "price_data":"Unavailable",
        "price":"Unavailable",
        "rating":"Unavailable",
        "title":"Unavailable",
        'exist':False,
        #'specification':spec
        }



def amazon_secondary(title):
    search_url = AMAZON_SEARCH_URL.format(quote_plus(title_sanitizer(title)))
    print(search_url)
    # driver = webdriver.Chrome(CHROMEDRIVER,chrome_options=options)
    # driver.get(search_url)
    # resp = driver.execute_script("return document.documentElement.outerHTML")
    # driver.quit()
    resp = requests.get(search_url,headers=HEADERS).text
    fsoup = BeautifulSoup(resp,features="html.parser")
    product_exist = validate.amazon_product_not_found(fsoup)
    if product_exist:
        try:
            product_url = fsoup.find("div",{"class":"a-section a-spacing-medium"}).find(class_='rush-component').a.get("href")
            print("__________________________-----------------------___________________")
            product_url = "https://www.amazon.in"+product_url    
            scraping(product_url)
        except Exception as e:
            print("Amazon Error: amazon_secondary()")
    else:
        product_data['amazon'] = {'exist':False,'website':"Amazon","color":"orange"}
        product_data['amazon'] = {
        "website":"Flipkart",
        "color":"blue",
        "product_url":"Unavailable",
        "image":None,
        "price_data":"Unavailable",
        "price":"Unavailable",
        "rating":"Unavailable",
        "title":"Unavailable",
        'exist':False,
        #'specification':spec
        }
       


def snapdeal_secondary(title):
    search_url = SNAPDEAL_SEARCH_URL.format(quote_plus(title_sanitizer(title)))
    resp = requests.get(search_url,headers=HEADERS).text
    ssoup = BeautifulSoup(resp,features="html.parser")
    product_exist = validate.snapdeal_product_not_found(ssoup)
    #get product url
    if product_exist:
        try:
            item_not = ssoup.find(class_="alert-heading").text
        except Exception as e:
            product_url = ssoup.find(class_="product-tuple-image").a.get("href")
            print(product_url)
            scraping(product_url)
    else:
        product_data['snapdeal'] = {
        "website":"Flipkart",
        "color":"blue",
        "product_url":"Unavailable",
        "image":None,
        "price_data":"Unavailable",
        "price":"Unavailable",
        "rating":"Unavailable",
        "title":"Unavailable",
        'exist':False,
        #'specification':spec
        }

def logout(req):
    auth.logout(req)
    return redirect("/")

@login_required(login_url="/login")
def getMonitoring(req):
    #get data from Monitor where user_id -> id
    uid = req.GET["uid"]
    data = Monitor.objects.filter(user_id=uid)
    items = []
    for item in data:
        d = {
            'title' : item.title,
            'actual':item.actual_price,
            'current':item.current_price,
            'site':item.site,
            'url':item.url,
            'id':item.id
        }
        items.append(d)
    return JsonResponse(items,safe=False)

#add for monitoring
def addToMonitor(req):
    if req.method=="GET":
        dataObj = Monitor(email=req.user.email,user_id=req.GET['userid'],title=req.GET['title'],actual_price=req.GET['price'],current_price=req.GET['price'],url=req.GET['url'],site=req.GET['site'])
        dataObj.save()
        return HttpResponse("GET method")
    return HttpResponse("ok")

def removeItem(req):
    pid = req.GET['id']
    dataObj = Monitor.objects.get(id=pid)
    dataObj.delete()
    return HttpResponse("Remove")





def sendmail(req):
    global images_loaded
    uCount = len(User.objects.all())
    mProducts = Monitor.objects.all()
    mcount = len(mProducts)
    if not images_loaded:
        # when it loaded save the pie chart image and then send
        # get details from db -> websites count, prices
        sites = {
            "Amazon":0,
            "Flipkart":0,
            "Snapdeal":0
        }
        prices = []
        for item in mProducts:
            sites[item.site]+=1
            prices.append(item.current_price)
        # visulaize prices
        print(prices)
        plt.hist(prices,range=(200,40000),facecolor="#d35400")
        ax = plt.axes()
        ax.set_facecolor("#1abc9c")
        plt.title("Price Data of users",fontdict={"fontsize":"24"})
        plt.xlabel("Price ranges",fontdict={"fontsize":"18"})
        plt.ylabel("Count",fontdict={"fontsize":"18"})
        plt.ylim(0,10,1)
        plt.savefig("./static/hist",dpi=300)

        plt.pie(labels=["Amazon","Flipkart","Snapdeal"],x=list(sites.values()),autopct='%1.1f%%')
        plt.legend()
        plt.title("Monitoring sites",fontdict={"fontsize":"24"})
        plt.ylabel("")
        plt.xlabel("")
        plt.savefig("./static/pie",dpi=300)
        images_loaded = True
    

    return render(req,"monitor.html",{"uCount":uCount,"mCount":mcount})


def send(req):
    mProducts = Monitor.objects.all()
    productData = []
    pc = 0
    mc = 0
    # for product in mProducts:
    #     cSite = product.site
    #     cURL = product.url
    #     response = requests.get(cURL,headers=HEADERS).text
    #     soup = BeautifulSoup(response,features="html.parser")
    #     if(cSite=="Amazon"):
    #         deal_price = soup.find(id="priceblock_dealprice")
    #         if deal_price is not None:
    #             price_data = deal_price
    #         else:
    #             price_data = soup.find(id="priceblock_ourprice")
    #         try:
    #             price_data = price_data.text.strip()
    #             price = price_data
    #             price = price[1:len(price)-3].replace(",","").strip() #converting into a number
    #             price = int(price)
    #         except Exception as e:
    #             price = "err"

    #     elif(cSite=="Flipkart"):
    #         price_data = soup.find(class_="_3qQ9m1").text.strip()
    #         price = int(price_data.replace(",","").replace("₹","").strip())

    #     else:
    #         price = int(soup.find(class_="payBlkBig").text.strip())
    #     #compare prices
    #     if(price<product.current_price):
    #         sub = "Price Drop"
    #         m = True
    #         msg = "Price of the product {} on \"{}\" dropped from {} to {}.".format(product.title,cSite,product.current_price,price)
    #     elif(price>product.current_price):
    #         sub = "Price Increases"
    #         m = True
    #         msg = "Price of the product {} on \"{}\" raised from {} to {}.".format(product.title,cSite,product.current_price,price)
    #     else:
    #         m=False
    #     if(m):
    #         pc+=1
    #         mc+=1
       
        
    # if not pc:
    #     print("no chg")
    # else:
    #     print("chg")
    # #get data
    # #scrape url based on site
    if send_mail("Price Changes on Monitoring Product","Product Name: Samsung Galaxy M30S (Blue, 128 GB)  (4 GB RAM) \n Current Price: 17490","dileep8417@gmail.com",['vtu8816@veltechuniv.edu.in'],fail_silently=False):
        return JsonResponse([{"mc":mc,"pc":pc}],safe=False)