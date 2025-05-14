from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
{"type": "service_account",
  "project_id": "placeholderid",
  "private_key_id": "privatekey1234567890abcdefghijklmnopqr",
  "private_key": "-----BEGIN PRIVATE KEY-----\n-----END PRIVATE KEY-----\n",
  "client_email": "client@email.com",
  "client_id": "123456789069782724271",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-nr6bv%40aspiredatabasewebsite.iam.gserviceaccount.com"
}
# Initialize the Firebase Admin SDK
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Get a reference to the Firestore database
db = firestore.client()

# Define the function to be triggered
def my_function(request):
    # importing dependencies 
    import pandas as pd
    import numpy as np
    import selenium
    from selenium import webdriver
    from datetime import date as d
    import firebase_admin
    from firebase_admin import firestore
    from firebase_admin import credentials
    # Import database module.
    from selenium.webdriver.chrome.options import Options
    from ASPIRE_Dates import ArticleDate
    from Firestore_Init import Firestore_Init

    class ArticleScraper():
        
        def __init__(self):
            #load in csv 
            self.companies = pd.read_csv('Selenium_Function_Inputs.csv')
            print(self.companies.head())

        def get_dataframe(self):
            return self.companies


        def scrape(
            self, db, company, start_url, get_urls, get_title, get_body, cookie=None, get_meta=None, get_date=None
        ):
            #making the driver headless
            options = Options()
            options.add_argument("--headless=new")
            #instantiating a driver
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(10) 
            records = []
            # Navigate to webpage, and click yes for cookies
            driver.get(start_url)
            # cookies
            if isinstance(cookie, str):
                try:
                    driver.find_element('xpath', cookie).click()
                except Exception as e:
                    print(f"CookieError: {e}, Website: {start_url}")


            # Find all of the anchor tags on the webpage
            links = driver.find_elements('xpath', get_urls)

            # Extract the URLs from the anchor tags
            urls = [link.get_attribute("href") for link in links]

            # scraping body text and title
            for url in urls:
                # need to do this. (check url, if there, ignore it)
                if url is None:
                    continue

                try:
                    driver.get(url)
                    record = {'url': url}
                except selenium.common.exceptions.TimeoutException as e:
                    print(e)
                    continue
                
                if isinstance(get_title, str):
                    try:
                        title = driver.find_element('xpath',get_title).get_attribute('innerText')
                        record['title'] = title
                    except selenium.common.exceptions.NoSuchElementException as e:
                        print(e)
                        record['title'] = 'None'
                        continue
                else:
                    continue    
                
                if isinstance(get_body, str):
                    try:
                        body = driver.find_element('xpath', get_body).get_attribute('innerText')
                        record['body'] = body
                    except:
                        record['body'] = None
                        pass
                else:
                    body = None    
                    
                if isinstance(get_meta, str):
                    try:
                        description = driver.find_element('xpath', get_meta).get_attribute('innerText')
                        record['description'] = description
                    except Exception as e:
                        print(f"GetDescriptionError: {e}, URL: {url}")
                else:
                    description = None

            # if isinstance(get_date, str):
                try:
                    date = driver.find_element('xpath', get_date).get_attribute('innerText')
                    date = str(date)
                    date_formatted = ArticleDate(date)
                    record['date'] = date_formatted
                except Exception as e:
                    print(f"GetDescriptionError: {e}, URL: {url}")
                    #setting default first date so that the date will be easy to find next time
                    record['date'] = 'None'
                    # print(date_formatted) 
                    
                records.append(record) 
                
                        #NEED TO ADD THIS IN AGAIN
                company_name = company
                article_title = record['title']
                
                #creating a unique articleID 
                article_ID = company_name + "_" + str(article_title) + "_" + str(record['date'])
                
                try:
                    doc_ref = db.collection('ASPIRE_ARTICLES').document(article_ID)
                    doc = doc_ref.get()
                    if doc.exists:
                        break
                except Exception as e:
                    print(record['title'], e)
                    print("error retrieving document id, should continue.")

            #closing driver after finished.
            self.quit_driver(driver)  
            return records

            #rows = df.iloc[37:,:]

        def get_articles(self, companies):
            #initializing dictionary to hold all articles
            db = Firestore_Init()
            
            company_articles = {}
            #going through every single company
            
            for index, row in companies.iterrows():
                # going through to get all the information
                all_articles = self.scrape(db, row['company'],row['start_URL'], row['get_urls'], 
                                                                row['get_title'], row['get_body'], 
                                                                row['cookie'], row['get_meta'], row['get_date'])
                scraped_articles = {}
                for i in range(len(all_articles)):
                    scraped_articles[i] = all_articles[i]
                
                i = 1
                publish_date = []
                for key in scraped_articles:
                    article = scraped_articles[key]
                    print(article)
                    
                    #adding in company name to each article
                    company_name = row['company']     
                    #checking to see if the article has a date
                    if article['date'] == 'None':
                        #checking to see if we need a starter date
                        if i == 1:
                            #setting default first date so that the date will be easy to find next time
                            date = d.today()
                            date_formatted = ArticleDate(date)
                            # print(date_formatted)
                        else:
                            #keep the dates more or less how they should be if there aren't dates
                            date_formatted = publish_date[-1]
                        i += 1

                    else:
                        date_formatted = article['date']    

                    if 'description' not in article:
                        #checking to see if there is no description
                        article['description'] = None

                    if article['title'] == "None":
                        #checking to see if there is no description
                        article['title'] = None   

                    if 'body' not in article:
                        #checking to see if there is no description
                        article['body'] = None                                  
                    
                    article_date = date_formatted
                    article['date'] = article_date
                
                    publish_date.append(article_date)
                    article['company_name'] = company_name
                    
                    #creating a unique articleID
                    article_ID = company_name + "_" + str(article['title']) + "_" + str(date_formatted)
                    
                    #adding articleID to the dictionary of articles
                    article['article_id'] = article_ID

                    self.insert_article(article, db)

                    #adding the whole json to a dictionary that we will use to insert everything into.
                    company_articles[article_ID] = article    
            return company_articles
            
        def insert_article(self, article, db):
            
            data = {
                u'company_name': str(article['company_name']),
                u'article_title': str(article['title']),
                u'article_url': str(article['url']),
                u'article_description': str(article['description']),
                u'article_date': article['date'],
                u'article_body': str(article['body'])
            }
            print(article['article_id'])
            print(data)
            
            try:
                db.collection(u'ASPIRE_ARTICLES').document(article['article_id']).set(data)  
            except:
                print("article unable to be added to the database")      

        def quit_driver(self, driver):
            # Close the browser
            driver.quit()           


    def Selenium_MainScraper():
        company_articles = ArticleScraper()  
        companies = company_articles.get_dataframe()
        articles = company_articles.get_articles(companies)
        # print(articles)
    Selenium_MainScraper()           

# Export the function as a cloud function
def create_time_triggered_function(request):
    # Create a new Firestore document with the cron job expression
    cron_expression = "0 0 * * *"  # Trigger at midnight every day
    doc_ref = db.collection(u'cron_jobs').add({u'expression': cron_expression})

    # Set up the cloud function trigger with the Firestore document ID
    return my_function, doc_ref.id
