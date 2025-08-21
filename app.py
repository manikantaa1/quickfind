from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId

app = Flask(__name__)import os
app.secret_key = os.environ.get("SECRET_KEY", "default_secret")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

ADMIN_USER = {
    "id": "admin",
    "password": "adminpassword"  # Change as needed
}

@login_manager.user_loader
def load_user(user_id):
    if user_id == ADMIN_USER["id"]:
        return User(user_id)
    return None

@app.route('/')
def dashboard():
    products = list(mongo.db.products.find())
    return render_template('dashboard.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form.get('username')
        pw = request.form.get('password')
        if userid == ADMIN_USER['id'] and pw == ADMIN_USER['password']:
            user = User(userid)
            login_user(user)
            return redirect(url_for('add_product'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    products = list(mongo.db.products.find())
    if request.method == 'POST':
        data = {
            "name": request.form['name'],
            "category": request.form['category'],
            "description": request.form['description'],
            "image": request.form['image'],
            "price": int(request.form['price']),
            "trendingScore": int(request.form['trendingScore']),
            "amazon": request.form['amazon'],
            "meesho": request.form['meesho']
        }
        mongo.db.products.insert_one(data)
        flash("Product added successfully!", "success")
        return redirect(url_for('add_product'))
    return render_template('add_product.html', products=products)

@app.route('/delete_product/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    mongo.db.products.delete_one({'_id': ObjectId(product_id)})
    flash("Product deleted!", "info")
    return redirect(url_for('add_product'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

