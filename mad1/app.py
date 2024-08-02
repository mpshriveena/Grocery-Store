from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Secret Key'
db = SQLAlchemy(app)
 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60))
    password = db.Column(db.String(60))
    email = db.Column(db.String(60))
 
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryid = db.Column(db.Integer, db.ForeignKey('category.id'))
    productname = db.Column(db.String(150), unique=True)
    unit = db.Column(db.String(150))
    price = db.Column(db.Float)
    manudate = db.Column(db.Date)
    stock = db.Column(db.Boolean)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryname = db.Column(db.String(150), unique=True)

    product = db.relationship('Product', backref='category', lazy=True)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    productid = db.Column(db.Integer, db.ForeignKey('product.id'))
    categoryname = db.Column(db.String(150))
    productname = db.Column(db.String(150))
    unit = db.Column(db.String(150))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    
class Buy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    productid = db.Column(db.Integer, db.ForeignKey('product.id'))
    categoryname = db.Column(db.String(150))
    productname = db.Column(db.String(150))
    unit = db.Column(db.String(150))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    

with app.app_context():
    db.create_all()
 
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/summary', methods=['GET','POST'] )
def summary():
    product_list = db.session.query(Buy).all()
    return render_template("summary.html", product_list=product_list)

@app.route('/userlogin', methods=['GET','POST'])
def userlogin():
    if request.method =='POST':
        username = request.form.get('username')
        password = request.form.get('password1')
        user = User.query.filter_by(username=username).first()
        if not user:
            return redirect(url_for('userlogin'))
        if (password != user.password):
            return redirect(url_for('userlogin'))
        session['userid'] = user.id
        return redirect(url_for('user', user = User.query.get(session['userid'])))
    return render_template("userlogin.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method =='POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password1')
        newuser = User(email=email, username=username, password=password)
        db.session.add(newuser)
        db.session.commit()
        return redirect(url_for('userlogin'))
    return render_template("register.html")

@app.route('/managerlogin', methods=['GET','POST'])
def managerlogin():
    if request.method =='POST':
        managername = request.form.get('managername')
        password2 = request.form.get('password2')
        if managername == 'Admin' and password2 == "12345":
            return redirect(url_for('manager'))
        else:
            return render_template("managerlogin.html")
    return render_template("managerlogin.html")

@app.route('/user', methods=['GET','POST'])
def user():
    categories = db.session.query(Category).all()
    if request.method == 'POST':
        field = request.form.get('field')
        search = request.form.get('search')
        if field=='categoryname':
            categories = Category.query.filter(Category.categoryname.like('%'+search+'%')).all()
            return render_template("user.html", categories=categories, user = User.query.get(session['userid']))
        if field=='productname':
            categories = Category.query.all()
            return render_template("user.html", categories=categories, pname=search, user = User.query.get(session['userid']))
    return render_template("user.html", categories=categories, user = User.query.get(session['userid']))


@app.route('/manager')
def manager():
    category_list = db.session.query(Category).all()
    return render_template("manager.html", category_list=category_list)

@app.route('/opencategory/<int:id>', methods=['GET','POST'])
def open(id):
    category = Category.query.get(id)
   
    return render_template("open.html", category=category)
 
@app.route("/addcart/<int:productid>", methods=['GET','POST'])
def addcart(productid):
    user = User.query.get(session['userid'])
    userid = user.id
    product = Product.query.get(productid)
    quantity = request.form.get('quantity')
    categoryid = product.categoryid
    category = Category.query.get(categoryid)
    categoryname = category.categoryname
    productid = product.id
    productname = product.productname
    unit = product.unit
    price = product.price
    newcart = Cart(userid=userid, productid=productid, categoryname=categoryname, productname=productname, unit=unit, price=price, quantity = quantity)
    db.session.add(newcart)
    db.session.commit()
    return redirect(url_for("cart"))


@app.route('/cart', methods=['GET','POST'] )
def cart():
    user = User.query.get(session['userid'])
    product_list = Cart.query.filter_by(userid=user.id)
    total=0
    for product in product_list:
        multiply = (product.price)*(product.quantity)
        total = total+multiply
    return render_template("cart.html", product_list=product_list, total=total)

@app.route('/purchased' )
def purchased():
    user = User.query.get(session['userid'])
    buy_list = Buy.query.filter_by(userid=user.id)
    return render_template("buy.html", buy_list=buy_list)


@app.route('/purchase', methods=['GET','POST'] )
def purchase():
    user = User.query.get(session['userid'])
    cart_list = Cart.query.filter_by(userid=user.id)
    buy_list = Buy.query.filter_by(userid=user.id)
    for product in cart_list:
        newbuy = Buy(userid=product.userid, productid=product.productid, categoryname=product.categoryname, productname=product.productname, unit=product.unit, price=product.price, quantity=product.quantity)
        db.session.add(newbuy)
        db.session.delete(product)
        db.session.commit()
    return render_template("buy.html", buy_list=buy_list)

@app.route("/category/add", methods=["POST"])
def addcategory():
    categoryname = request.form.get("categoryname")
    newcategory = Category(categoryname=categoryname)
    db.session.add(newcategory)
    db.session.commit()
    return redirect(url_for("manager"))

@app.route("/product/add", methods=["POST"])
def addproduct():
    productname = request.form.get("productname")
    category = request.form.get("category")
    unit = request.form.get("unit")
    price = request.form.get("price")
    manudate = request.form.get("manudate")
    stock = request.form.get("stock")
    if stock == '1':
        stock=True
    else:
        stock=False
    category = Category.query.get(category)
    try:
        manudate = datetime.strptime(manudate, '%Y-%m-%d')
    except ValueError:
        return "Value Error"
    newproduct = Product(productname=productname, category=category, unit=unit, price=price, manudate=manudate, stock=stock)
    db.session.add(newproduct)
    db.session.commit()
    return redirect(url_for("open", id=category.id))


@app.route('/category/add')
def addcategorybutton():
    return render_template("addcategory.html")


@app.route('/product/add')
def addproductbutton():
    categoryid = -1
    args = request.args
    if 'categoryid' in args:
        if Category.query.get(int(args.get('categoryid'))):
            categoryid = int(args.get('categoryid'))
    return render_template("addproduct.html",categoryid=categoryid, nowstring=datetime.now().strftime("%Y-%m-%d"), categories=Category.query.all())


 
    
@app.route("/updatecategory/<int:id>", methods=['GET','POST'])
def updatecategory(id):
    edit = Category.query.get(id)
    if request.method =="POST":
        edit.categoryname = request.form['categoryname']
        db.session.commit()
        return redirect('/manager')
    return render_template('updatecategory.html', edit=edit)
    
@app.route("/updateproduct/<int:id>", methods=['GET','POST'])
def updateproduct(id):
    edit = Product.query.get(id)
    if request.method =="POST":
        productname = request.form['productname']
        category = request.form['category']
        unit = request.form['unit']
        price = request.form['price']
        manudate = request.form['manudate']
        stock = request.form['stock']
        if stock == '1':
            stock=True
        else:
            stock=False
        category = Category.query.get(category)
        manudate = datetime.strptime(manudate, '%Y-%m-%d')
        edit.productname = productname
        edit.category = category
        edit.unit = unit
        edit.price = price
        edit.manudate = manudate
        edit.stock = stock
        db.session.commit()
        return redirect(url_for("open", id=category.id))
    return render_template('updateproduct.html', edit=edit, categories = Category.query.all(), nowstring=datetime.now().strftime("%Y-%m-%d"), manudate = edit.manudate.strftime("%Y-%m-%d"))


@app.route("/deletecategory/<int:category_id>")
def deletecategory(category_id):
    category = db.session.query(Category).filter(Category.id == category_id).first()
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for("manager"))

@app.route("/deleteproduct/<int:product_id>")
def deleteproduct(product_id):
    product = db.session.query(Product).filter(Product.id == product_id).first()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("open", id=product.categoryid))


@app.route("/deletecart/<int:product_id>")
def deletecart(product_id):
    cart = db.session.query(Cart).filter(Cart.id == product_id).first()
    db.session.delete(cart)
    db.session.commit()
    return redirect(url_for("cart"))
    
if __name__ == '__main__':
    app.run(debug=True)