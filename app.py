from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user
from sqlalchemy import Select
from flask_bcrypt import Bcrypt
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import mysql.connector
import smtplib
from email.message import EmailMessage
from flask_executor import Executor


app = Flask(__name__)
bcrypt=Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/users_for_dbms_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
executor=Executor(app)

#headers are required to make our request more genuine by impersonating our request as request send by the browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Accept-Language': 'da, en-gb, en',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
    }

amazon_links={
    'phone':"https://www.amazon.in/s?k=phones&crid=1SR7PYNI8L36G&sprefix=phones%2Caps%2C218&ref=nb_sb_noss_1",
    'iphone':"https://www.amazon.in/s?k=iphone&crid=159EZA5FZKRY1&sprefix=iphone%2Caps%2C219&ref=nb_sb_noss_1",
    'ipad':"https://www.amazon.in/s?k=ipad&crid=23T6ZHSIDN7VX&sprefix=ipad%2Caps%2C217&ref=nb_sb_noss_1",
    'laptop':"https://www.amazon.in/s?k=laptop&crid=2Q1645SHINA51&sprefix=laptop%2Caps%2C232&ref=nb_sb_noss_1"
    }
flipkart_links={
    'phone':"https://www.flipkart.com/search?q=phones&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off",
    'iphone':"https://www.flipkart.com/search?q=iphone&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off",
    'ipad':"https://www.flipkart.com/search?q=apple%20ipad&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off",
    'laptop':"https://www.flipkart.com/search?q=laptop&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
}

def send_email(str,user_email):
        smtp_server = 'smtp.gmail.com'  
        smtp_port = 587  

        msg = EmailMessage()
        msg.set_content(str)

        msg['Subject'] = 'regarding price update'
        msg['From'] = 'sender_email@gmail.com'
        msg['To'] = user_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login('sender_email@gmail.com', 'app_password')
            server.send_message(msg)


def get_info(url):
    try:
        page=requests.get(url,headers=headers)
        return page.text
    except:
        return None


def amazon_scraper_particular_prod(amazon_link):
    dict={'name':'',
          'price':''
          }
    try:
        amazon_doc=get_info(amazon_link)
        soup=BeautifulSoup(amazon_doc,'html.parser')
        prod_price=soup.find(class_='a-price-whole').get_text()
        prod_name=soup.find(class_="a-size-large product-title-word-break").get_text()
        dict['name']=prod_name.strip()
        dict['price']=price_processing(prod_price)
        return dict
    except:
        return dict


def amazon_scraper(url):
    dict={}
    i=0
    main_amazon_doc=get_info(url)
    soup=BeautifulSoup(main_amazon_doc,'html.parser')
    product=soup.find_all('div',class_='puis-card-container s-card-container s-overflow-hidden aok-relative puis-include-content-margin puis puis-v3tr261jy6r3e12l60q293r7wsa s-latency-cf-section puis-card-border')
    for prod in product:
        title_html=prod.find('span',class_='a-size-medium a-color-base a-text-normal')
        if title_html:
            title=title_html.text
        else:
            title=None
        dict[i]=dict.get(i,[title])
        rating_element=prod.find('span',class_='a-icon-alt')
            
        if rating_element:
            rating=rating_element.text.replace(" out of 5 stars","/5.0")
        else:
            rating=None
        dict[i].append(rating)
        price_html=prod.find('span',class_='a-price-whole')
        if price_html:
            price=price_processing(price_html.text)
            
        else:
            price=0
        dict[i].append(price)
        product_link_a=prod.find('a',class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')
        if product_link_a:
            product_link=product_link_a.get('href')
            full_url=urljoin(url,product_link)
            product_link_final=full_url
        else:
            product_link_final=None
        dict[i].append(product_link_final)
        images_url=prod.find('img',class_='s-image')
        if images_url:
            images_link=images_url['src']
        else:
            images_link=None
        dict[i].append(images_link)
        i=i+1
    return dict

def flipkart_scraper(url):
    i=0
    dict={}
    flipkart_doc=get_info(url)
    soup=BeautifulSoup(flipkart_doc,'html.parser')
    products=soup.find_all('div',class_='_2kHMtA')
    for prod in products:
        title_html=prod.find('div',class_='_4rR01T')
        if title_html:
            title=title_html.text
            title=title.strip()
        else:
            title=None
        dict[i]=dict.get(i,[title.strip()])
        attributes=prod.find_all('li',class_='rgWa7D')
        features=[]
        for att in attributes:
            features.append((att.text).strip())
        features_str="_".join(features)
        dict[i].append(features_str)
        
        price_html=prod.find('div',class_='_30jeq3 _1_WHN1')
        price=price_html.text
        price=price_processing_flipkart(price)
        dict[i].append(price)
        product_link=prod.find('a',class_='_1fQZEK')
        product_link=product_link.get('href')
        product_link=urljoin(url,product_link)
        dict[i].append(product_link)
        prod_img=prod.find('img',class_='_396cs4')
        prod_img=prod_img['src']
        dict[i].append(prod_img)
        i=i+1
    return dict






def flipkart_scraper_particular_product(flipkart_link):
    dict={'name':'',
          'price':''
          }
    try:
        flipkart_doc=get_info(flipkart_link)
        soup=BeautifulSoup(flipkart_doc,'html.parser')
        prod_name=soup.find(class_='B_NuCI').get_text()
        prod_price=soup.find(class_='_30jeq3 _16Jk6d').get_text()
        prod_price=price_processing_flipkart(prod_price)
        dict['name']=prod_name.strip()
        dict['price']=prod_price
        return dict
    except:
        return dict

#getting the price in int from string of amazon website
def price_processing(price):
    p1=list(price.split('.'))
    p2=''.join(p1[0].split(','))
    return int(p2)

def price_processing_flipkart(price):
    p1=list(price.split(','))
    p2=[p1[0][1:]]
    p1.remove(p1[0])
    return int("".join(p2+p1))




login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_usesr(user_id):
    return user_detail.query.get(id)

#tables of database
class user_detail(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    user_name=db.Column(db.String(100),nullable=False)
    user_email=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    confirm_password=db.Column(db.String(100))
    db.CheckConstraint("password = confirm_password", name="password_match")


class users_session_login(db.Model,UserMixin):
    sno=db.Column(db.Integer,primary_key=True)
    id=db.Column(db.Integer,db.ForeignKey(user_detail.id),nullable=False)
    user_name=db.Column(db.String(100),nullable=False)
    login_time=db.Column(db.DateTime(timezone=True),default=db.func.now())

class amazon_list(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    product_type=db.Column(db.String(20),nullable=False)
    product_title=db.Column(db.String(1000),nullable=False)
    product_review=db.Column(db.String(50),nullable=True)
    product_price=db.Column(db.Integer,nullable=False)
    product_link=db.Column(db.String(1000))
    product_image=db.Column(db.String(1000))
    user_email=db.Column(db.String(30),nullable=False)

class flipkart_list(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    product_type=db.Column(db.String(20),nullable=False)
    product_title=db.Column(db.String(1000),nullable=False)
    product_attributes=db.Column(db.String(1000),nullable=False)
    product_price=db.Column(db.Integer,nullable=False)
    product_link=db.Column(db.String(1000))
    product_image=db.Column(db.String(1000))
    user_email=db.Column(db.String(30),nullable=False)

class amazon_particular_prod(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    product_title=db.Column(db.String(1000),nullable=False)
    product_price_current=db.Column(db.Integer,nullable=False)
    product_price_initial=db.Column(db.Integer,default=9999999)
    user_email=db.Column(db.String(30),nullable=False)

class flipkart_particular_prod(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    product_title=db.Column(db.String(1000),nullable=False)
    product_price_current=db.Column(db.Integer,nullable=False)
    product_price_initial=db.Column(db.Integer,default=9999999)
    user_email=db.Column(db.String(30),nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")

@app.route("/login_page",methods=["GET","POST"])
def login_page():
    db.session.query(amazon_list).delete()
    db.session.commit()
    db.session.query(flipkart_list).delete()
    db.session.commit()
    db.session.query(amazon_particular_prod).delete()
    db.session.commit()
    db.session.query(flipkart_particular_prod).delete()
    db.session.commit()
    error=""
    if request.method=="POST":
        user_name1=request.form['username']
        passwords=request.form['password']
        user_data=user_detail.query.filter_by(user_name=user_name1).first()
        if user_data:
            if bcrypt.check_password_hash(user_data.password,passwords):
                session_detail=users_session_login(user_name=user_name1,id=Select(user_detail.id).where(user_detail.user_name==user_name1 and user_detail.password==passwords))
                db.session.add(session_detail)
                db.session.commit()
                error=""
                db.session.query(amazon_list).delete()
                db.session.commit()

                db.session.query(flipkart_list).delete()
                db.session.commit()

                db.session.query(amazon_particular_prod).delete()
                db.session.commit()
                db.session.query(flipkart_particular_prod).delete()
                db.session.commit()
                return redirect("/mainpage")
            else:
                error="incorrect password"
        else:
            error="username not found"
    return render_template("login_page.html",error=error)

@app.route("/signup_page",methods=['GET','POST'])
def signup_page():
    flag=0
    error_message=""
    if request.method=='POST':
        user_name=request.form['username']
        email=request.form['email']
        pw=request.form['password']
        cpw=request.form['confirm-password']
        user_details=user_detail(user_name=user_name,user_email=email,password=bcrypt.generate_password_hash(pw).decode('utf-8'),confirm_password=bcrypt.generate_password_hash(cpw).decode('utf-8'))
        check_for_duplicate=user_detail.query.filter_by(user_name=user_name).first()
        if not check_for_duplicate:
            if len(pw)<6:
                error_message="length of password must be greater than 6"
            else:
                if pw!=cpw:
                    error_message="please enter passwords correctly"
                else:
                    error_message=""
                    db.session.add(user_details)
                    db.session.commit()
                    db.session.query(amazon_list).delete()
                    db.session.commit()
                    db.session.query(amazon_list).delete()
                    db.session.commit()
                    return redirect("/login_page")
        else:
            error_message="username already taken"
    return render_template("signup_page.html",error=error_message)

@login_required
@app.route("/mainpage",methods=["GET","POST"])
def mainpage():
    try:
        executor.submit(amazon_continuous_price_monitor)
        items=''
        if request.method=="POST":
            db.session.query(amazon_list).delete()
            db.session.commit()
            db.session.query(flipkart_list).delete()
            db.session.commit()
            db.session.query(amazon_particular_prod).delete()
            db.session.commit()
            db.session.query(flipkart_particular_prod).delete()
            db.session.commit()
            user_email=request.form['Email']
            item=request.form['item']
            flipkart_dict=flipkart_scraper(flipkart_links[item])
            dict=amazon_scraper(amazon_links[item])
            for i in dict.keys():
                title=dict[i][0]
                ratings=dict[i][1]
                price=dict[i][2]
                product_link=dict[i][3]
                product_img=dict[i][4]
                amazon_list_obj=amazon_list(product_type=item,product_title=title,product_review=ratings,product_price=price,product_link=product_link,product_image=product_img,user_email=user_email)
                db.session.add(amazon_list_obj)
                db.session.commit()
            for i in flipkart_dict.keys():
                title=flipkart_dict[i][0]
                attribute=flipkart_dict[i][1]
                price=flipkart_dict[i][2]
                product_link=flipkart_dict[i][3]
                product_img=flipkart_dict[i][4]
                flipkart_list_obj=flipkart_list(product_type=item,product_title=title,product_attributes=attribute,product_price=price,product_link=product_link,product_image=product_img,user_email=user_email)
                db.session.add(flipkart_list_obj)
                db.session.commit() 
        amazon_prod_info=db.session.query(amazon_list).order_by(amazon_list.product_price).all()
        flipkart_prod_info=db.session.query(flipkart_list).order_by(flipkart_list.product_price).all()
        particular_prod=flipkart_particular_prod.query.all()
        amazon_particular_product=amazon_particular_prod.query.all()

        return render_template("main_page.html",amazon_prod_info=amazon_prod_info,flipkart_prod_info=flipkart_prod_info,amazon_particular_product=amazon_particular_product,flipkart_particular_product=particular_prod)
    except Exception:
        print(Exception)
        return "error loading page please refresh"
    

@app.route("/add_amazon/<int:sno>")
def add_amazon(sno):
    amazon_prod_data=db.session.query(amazon_list).filter_by(sno=sno).first()
    amazon_dict=amazon_scraper_particular_prod(amazon_prod_data.product_link)
    obj1=amazon_particular_prod(product_title=amazon_dict['name'],product_price_current=amazon_dict['price'],product_price_initial=amazon_dict['price'],user_email=amazon_prod_data.user_email)
    db.session.add(obj1)
    db.session.commit()
    amazon_particular_product=amazon_particular_prod.query.all()
    particular_prod=flipkart_particular_prod.query.all()
    amazon_prod_info=db.session.query(amazon_list).order_by(amazon_list.product_price).all()
    flipkart_prod_info=db.session.query(flipkart_list).order_by(flipkart_list.product_price).all()
    return render_template("main_page.html",amazon_prod_info=amazon_prod_info,flipkart_prod_info=flipkart_prod_info,amazon_particular_product=amazon_particular_product,flipkart_particular_product=particular_prod)


@app.route("/add_flipkart/<int:sno>")
def add_flipkart(sno):
    flipkart_prod_data=db.session.query(flipkart_list).filter_by(sno=sno).first()
    flipkart_dict=flipkart_scraper_particular_product(flipkart_prod_data.product_link)
    obj2=flipkart_particular_prod(product_title=flipkart_dict['name'],product_price_current=flipkart_dict['price'],product_price_initial=flipkart_dict['price'],user_email=flipkart_prod_data.user_email)
    db.session.add(obj2)
    db.session.commit()
    particular_prod=flipkart_particular_prod.query.all()
    amazon_particular_product=amazon_particular_prod.query.all()
    amazon_prod_info=db.session.query(amazon_list).order_by(amazon_list.product_price).all()
    flipkart_prod_info=db.session.query(flipkart_list).order_by(flipkart_list.product_price).all()
    return render_template("main_page.html",amazon_prod_info=amazon_prod_info,flipkart_prod_info=flipkart_prod_info,flipkart_particular_product=particular_prod,amazon_particular_product=amazon_particular_product)

@app.route("/remove_amazon/<int:sno>")
def remove_amazon(sno):
        amazon_prod_data=db.session.query(amazon_particular_prod).filter_by(sno=sno).first()
        db.session.delete(amazon_prod_data)
        db.session.commit()
        return redirect('/mainpage')


@app.route("/remove_flipkart/<int:sno>")
def remove_flipkart(sno):
        flipkart_prod_data=db.session.query(flipkart_particular_prod).filter_by(sno=sno).first()
        db.session.delete(flipkart_prod_data)
        db.session.commit()
        return redirect('/mainpage')
@app.route("/logout")
def logout():
    db.session.query(amazon_list).delete()
    db.session.commit()
    db.session.query(flipkart_list).delete()
    db.session.commit()
    db.session.query(amazon_particular_prod).delete()
    db.session.commit()
    db.session.query(flipkart_particular_prod).delete()
    db.session.commit()
    return redirect('/mainpage')

def amazon_continuous_price_monitor():
    while True:
        db_config = {
        "host": "localhost",
        "user": "root",
        "passwd": "password",
        "database": "users_for_dbms_project"  
        }
        my_db = mysql.connector.connect(**db_config)
        my_cursor=my_db.cursor()
        my_cursor.execute("SELECT * FROM amazon_particular_prod")
        result = my_cursor.fetchall()
        print(result)
        if result:
            for i in result:
                if i[2]==i[3]:
                    email_msg=f'dear user,on amazon the price of the product titled {i[1]} remained same which is {i[2]} we will inform we if it changes again'
                    send_email(email_msg,i[4])
                    print("sent successfull for amazon")
        my_cursor.execute("SELECT * FROM flipkart_particular_prod")
        result = my_cursor.fetchall()
        print(result)
        if result:
            for i in result:
                  if i[2]==i[3]:
                    email_msg=f'dear user,on flipkart the price of the product titled {i[1]} remained same which is {i[2]} we will inform we if it changes again'
                    send_email(email_msg,i[4])
                    print("sent successfully for flipkart")
        time.sleep(100)


if __name__=="__main__":
    app.run(debug=True)

    