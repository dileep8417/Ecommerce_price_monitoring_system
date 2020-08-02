class ProductValidation():
    def amazon_product_not_found(self,soup):
        search_msg = soup.find(class_="widgetId=messaging-messages-fkmr-message-builder-no-results")
        if search_msg is not  None:
            print("Amazon no product")
            return 0
        else:
            return 1

    def snapdeal_product_not_found(self,soup):
        try:
            search_mg = soup.find(class_="search-result-txt-section").span.text
            search_mg.find("Sorry")
            return 1
        except Exception:
            return 0

    def flipkart_product_not_found(self,soup):
        search_msg = soup.find(class_="DUFPUZ")
        if search_msg is not  None:
            print("Snapdeal no product")
            return 0
        else:
            return 1
