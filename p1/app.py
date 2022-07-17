from email.mime import image
from pickle import GET
from sys import flags
from security import authenticate, identity
from flask_jwt import JWT
from security import authenticate, identity
from flask import Flask, render_template, url_for, request, session, redirect, flash, jsonify
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from pymongo import MongoClient
import gridfs
import codecs


app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://localhost:27017/ecommerce"
mongo = PyMongo(app)

api =Api(app)
jwt = JWT(app, authenticate, identity) #auth
client = MongoClient("mongodb://localhost:27017/ecommerce")
app.db = client.ecommerce 
app.secret_key = 'secretkey'
# mongo = mongo.db
col = app.db.users
products = app.db.products

@app.route('/home')
@app.route('/')
def home(): 
    prolist = app.db.products.find({})
    return render_template('home.html',firstname='name',prolist=prolist) 

@app.route('/category')
def category():
    category = request.args.get('productCategory')
    print(category)
    cpros = app.db.products.find({'productCategory':category}) 
    return render_template('category.html',prolist=cpros)

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('regname')
        password = request.form.get('regpass')
        signup_user = app.db.users.find_one({'email': username})
        if signup_user:
            flash(username + ' username is already exist')
            return redirect(url_for('signup'))
        print(username, password)
        hashed = password
        app.db.users.insert_one({'Name': name,'Address':request.form.get('address'), 'email': username, 'password': hashed})
        flash('SUCCESSFULLY')
    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    lattempt = 0
    if "username" in session:
        return redirect(url_for("home"))
    if request.method == 'POST':
        lattempt = 1
        username = request.form.get('userid')
        password = request.form.get('password')
        signin_user = app.db.users.find_one({'email':username})
        print(signin_user)
        if signin_user:
            if password == signin_user['password']:
                session['loggedIn'] = True 
                session['username'] = signin_user['Name']
                return redirect(url_for('home'))
                
        flash('Username and password combination is wrong')
        print('wrong credentails')
        return render_template('signin.html',lattempt=lattempt)
    return render_template('signin.html',lattempt=lattempt)

@app.route('/addproduct',methods=['GET', 'POST'])
def addproduct():
    if "username" not in session:
        return redirect(url_for('signin'))
    if session['username'] == 'soumya':
        if request.method == "POST":
            pname = request.form.get('pname')
            brand = request.form.get('brand')
            price = request.form.get('price')
            description = request.form.get('description')
            file = request.form.get('pimage')
            image = request.files.get('pimage')
            mongo.save_file(image.filename, image)
            products = app.db.products 
            products.insert_one({'productName':pname,'brand':brand,'price':price,'description': description,'image':image.filename,'imageURL':request.form.get('pimageURL'),'productId':request.form.get('productId'),'productCategory':request.form.get('productCategory')})
            return render_template('addproduct.html')
        return render_template('addproduct.html')
    else:
        return "you don't have access"


@app.route('/productDescription')
def prodDescription():
    productId = request.args.get('productId')
    print(productId)
    currProduct = products.find_one({'productId':productId})
    print(currProduct['productName'])
    return render_template('productDescription.html',currProduct=currProduct)

@app.route('/addToCart')
def addToCart():
    if "username" not in session:
        return redirect(url_for('signin'))
    else:
        productId = request.args.get('productId')
        currProduct = app.db.products.find_one({'productId':productId})
        app.db.Cart.insert_one({'user':session['username'],'productName':currProduct['productName'],'productId':productId,'productPrice':currProduct['price']})
        flash('proudct added to cart successfully')
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    global count
    if "username" not in session:
        return redirect(url_for('signin'))
    else:
        cart = app.db.Cart.find({})
        total = 0
        count = 0
        for i in cart:
            if i['user'] == session['username']:
                total = total + int(i['productPrice'])
                count += 1
        print(cart)
        cart.rewind()
        return render_template('cart.html',cart=cart,total=total,count=count)
    return redirect(url_for('home'))

@app.route('/removeItem')
def removeItem():
    productId = request.args.get('productId')
    app.db.Cart.delete_one({'productId':productId})
    return redirect(url_for('cart'))

@app.route('/buynow')
def buynow():
    if "username" not in session:
        return redirect(url_for('signin'))
    else:
        cart = app.db.Cart.find({})
        for i in cart:
            if i['user'] == session['username']:
                app.db.Orders.insert_one({'email':session['username'],'productName':i['productName'],'productId':i['productId'],'productPrice':i['productPrice']})
                app.db.Cart.delete_one({'productId':i['productId']})
                # count -= 1
        return render_template('orderSuccessful.html')

@app.route('/account/orders')
def orders():
    if "username" not in session:
        return redirect(url_for('signin'))
    else:
        orders = app.db.Orders.find({})
        print(orders)
        return render_template('orders.html',orders=orders)

@app.route('/account/profile')
def profile():
    user = app.db.users.find_one({"Name":session['username']})
    print(user)
    return render_template('profile.html',user=user)

@app.route('/logout')
def logout():
    session['loggedIn'] = False 
    session.pop('username', None)
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=3389)
