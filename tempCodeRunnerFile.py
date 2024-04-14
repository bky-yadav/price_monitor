

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
        dict['name']=prod_name
        dict['price']=prod_price
        return dict
    except:
        return dict


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

class users_session_logout(db.Model,UserMixin):
    sno=db.Column(db.Integer,primary_key=True)
    id=db.Column(db.Integer,db.ForeignKey(user_detail.id),nullable=False)
    user_name=db.Column(db.String(100),nullable=False)
    logout_time=db.Column(db.DateTime(timezone=True),default=db.func.now())
    total_time_spend=db.Column(db.DateTime(timezone=True),default=logout_time-users_session_login.login_time)

class amazon_list(db.Model):