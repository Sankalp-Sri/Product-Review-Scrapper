from flask import Flask, render_template, request,jsonify
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from pymongo import MongoClient
from flask_cors import CORS,cross_origin

app = Flask(__name__) # initialising the flask app with the name 'app'

@app.route('/',methods = ['POST','GET'])  #Creating a route with allowed post adn get methods
def index():
    if request.method == "POST":
        searchString = request.form["content"].replace(' ','')
        try:

            #First try to see that if the reviews for the particular product already exist in the db or not.

            client = MongoClient('mongodb://localhost:27017/')
            db = client.Itemreviews  # connecting to the database called crawlerDB
            reviews = db[searchString].find({})  # searching the collection with the name same as the keyword
            if reviews.count() > 0: # if there is a collection with searched keyword and it has records in it
                return render_template('results.html',reviews=reviews)
            else:
                # Now if the review is not present in the database we will move on and scrap web pages to retrieve them

                #Scraping Flipkart.com

                # preparing the URL to search the product on Flipkart

                flipkart_url = "https://www.flipkart.com/search?q=" + searchString
                flipkartPage = requests.get(flipkart_url)

                # parsing the webpage as HTML
                flipkart_html = bs(flipkartPage.content, "html.parser")

                #Inspect the search page and find the tag containing the product href link adn extract it

                bigboxes = flipkart_html.find_all('div',{'class':'bhgxx2 col-12-12'})

                #Removing the div class with same name but having no product link in it
                del bigboxes[0:3]

                #Now choosing the first product result
                box = bigboxes[0]

                # extracting the actual product link
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']

                # getting the product page from server & parse it
                prodRes = requests.get(productLink)
                prod_html = bs(prodRes.text, "html.parser")


                #Review Page Scrapping
                all_review_link = prod_html.find('div', {'class': "swINJg _3nrCtb"})
                all_review_link = all_review_link.find_parent()
                review_link = "https://www.flipkart.com" + all_review_link['href']
                review_page = requests.get(review_link)
                review_html = bs(review_page.content, 'html.parser')
                boxes_comment = review_html.find_all('div', {'class': '_3gijNv col-12-12'})
                del boxes_comment[0:4]

                table = db[searchString]
                filename = searchString+'.csv'
                fw = open(filename,'w')
                headers = "Product, Customer Name, Rating, Likes, Dislikes, Heading, Comment\n"
                fw.write(headers)

                reviews = [] # initializing an empty list for reviews
                for commentbox in boxes_comment:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except:
                         name = "No Name"

                    try:
                        rating = commentbox.div.div.div.find_all('div',{'class': 'hGSR34 E_uFuv'})[0].text
                    except:
                        rating = "No Ratings"

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = "No Comment Heads"

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': 'qwjRop'})
                        custComment = comtag[0].div.text
                    except:
                        custComment = "No Comments"
                    try:
                        likes = commentbox.div.div.find_all('div', {'class': '_2ZibVB'})[0].text
                    except:
                        likes = "No Likes"

                    try:
                        dislikes = commentbox.div.div.find_all('div', {'class': '_2ZibVB _1FP7V7'})[0].text
                    except:
                        dislikes = 'No Dislikes'

                        #Writing the findings in csv file
                        fw.write(searchString+","+"")
                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment,
                              "Likes": likes, "Dislikes": dislikes}  # saving that detail to a dictionary
                    # x = table.insert_one(mydict) #insertig the dictionary containing the rview comments to the collection
                    reviews.append(mydict)  # appending the comments to the review list

                #Scrapping PAGE2
                box_next = boxes_comment[10].find('a', {'class': '_3fVaIS'})
                next_page_link = "https://www.flipkart.com" + box_next['href']
                next_page = requests.get(next_page_link)
                next_page_html = bs(next_page.content, 'html.parser')
                boxes_comment = next_page_html.find_all('div', {'class': '_3gijNv col-12-12'})
                del boxes_comment[0:4]

                for commentbox in boxes_comment:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except:
                        name = "No Name"

                    try:
                        rating = commentbox.div.div.div.find_all('div',{'class': 'hGSR34 E_uFuv'})[0].text
                    except:
                        rating = "No Ratings"

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = "No Comment Heads"

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': 'qwjRop'})
                        custComment = comtag[0].div.get_text()
                    except:
                        custComment = "No Comments"
                    try:
                        likes = commentbox.div.div.find_all('div', {'class': '_2ZibVB'})[0].text
                    except:
                        likes = "No Likes"

                    try:
                        dislikes = commentbox.div.div.find_all('div', {'class': '_2ZibVB _1FP7V7'})[0].text
                    except:
                        dislikes = 'No Dislikes'
                        # fw.write(searchString+","+"")
                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment,"Likes": likes, "Dislikes": dislikes}  # saving that detail to a dictionary
                    # x = table.insert_one(mydict) #insertig the dictionary containing the rview comments to the collection
                    reviews.append(mydict)  # appending the comments to the review list


                #Scrapping PAGE3
                box_next = boxes_comment[10].find('a', {'class': '_3fVaIS'})
                next_page_link = "https://www.flipkart.com" + box_next['href']
                next_page = requests.get(next_page_link)
                next_page_html = bs(next_page.content, 'html.parser')
                boxes_comment = next_page_html.find_all('div', {'class': '_3gijNv col-12-12'})
                del boxes_comment[0:4]

                for commentbox in boxes_comment:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    except:
                        name = "No Name"

                    try:
                        rating = commentbox.div.div.div.find_all('div',{'class': 'hGSR34 E_uFuv'})[0].text
                    except:
                        rating = "No Ratings"

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = "No Comment Heads"

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': 'qwjRop'})
                        custComment = comtag[0].div.get_text()
                    except:
                        custComment = "No Comments"
                    try:
                        likes = commentbox.div.div.find_all('div', {'class': '_2ZibVB'})[0].text
                    except:
                        likes = "No Likes"

                    try:
                        dislikes = commentbox.div.div.find_all('div', {'class': '_2ZibVB _1FP7V7'})[0].text
                    except:
                        dislikes = 'No Dislikes'
                        # fw.write(searchString+","+"")
                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment,
                              "Likes": likes, "Dislikes": dislikes}  # saving that detail to a dictionary
                    # x = table.insert_one(mydict) #insertig the dictionary containing the rview comments to the collection
                    reviews.append(mydict)  # appending the comments to the review list
                    fw.close()
                return render_template('results.html', reviews=reviews) # showing the review to the user
        except:
            return "Something is Wrong"
    else:
        return render_template('index.html')

if __name__== "__main__":
    app.run(port=8000, debug=True)
