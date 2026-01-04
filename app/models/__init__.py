from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='staff') # admin, staff, delivery
    orders = db.relationship('DeliveryOrder', backref='customer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50)) # Starter, Main, Dessert
    cost_per_unit = db.Column(db.Float)
    image_url = db.Column(db.String(500)) # URL for the food image
    logs = db.relationship('DailyLog', backref='item', lazy='dynamic')

    def __repr__(self):
        return '<FoodItem {}>'.format(self.name)

class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, default=datetime.utcnow)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'))
    prepared_qty = db.Column(db.Integer, default=0)
    sold_dine_in = db.Column(db.Integer, default=0)
    sold_delivery = db.Column(db.Integer, default=0)
    waste_qty = db.Column(db.Integer, default=0) # Can be calculated
    cost_impact = db.Column(db.Float, default=0.0)

    def calculate_waste_and_cost(self):
        sold_total = self.sold_dine_in + self.sold_delivery
        self.waste_qty = max(0, self.prepared_qty - sold_total)
        # Assuming cost impact is based on waste
        if self.item:
            self.cost_impact = self.waste_qty * self.item.cost_per_unit
class DeliveryOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    items_json = db.Column(db.Text, nullable=False) # Storing items as JSON string for simplicity: {"1": 2, "3": 1} (ItemID: Qty)
    address = db.Column(db.String(200), nullable=False)
    items_json = db.Column(db.Text, nullable=False) # Storing items as JSON string for simplicity: {"1": 2, "3": 1} (ItemID: Qty)
    status = db.Column(db.String(20), default='Pending') # Pending, Delivered, Cancelled
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<DeliveryOrder {}>'.format(self.id)
