from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, FoodItem, DailyLog
from app.services.prediction_service import predict_demand
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

from app.services.prediction_service import predict_total_demand_tomorrow
from sqlalchemy import func

@bp.route('/')
def index():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.delivery_menu'))

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    today = datetime.now().date()
    
    # 1. Today's Aggregates
    stats = db.session.query(
        func.sum(DailyLog.prepared_qty).label('prepared'),
        func.sum(DailyLog.sold_dine_in + DailyLog.sold_delivery).label('sold'),
        func.sum(DailyLog.waste_qty).label('waste')
    ).filter(DailyLog.date == today).first()
    
    prepared_today = stats.prepared or 0
    sold_today = stats.sold or 0
    waste_today = stats.waste or 0
    predicted_tomorrow = predict_total_demand_tomorrow()

    # 2. Chart Data (Last 7 Days)
    week_ago = today - timedelta(days=7)
    weekly_logs = db.session.query(
        DailyLog.date,
        func.sum(DailyLog.sold_dine_in + DailyLog.sold_delivery).label('sold'),
        func.sum(DailyLog.waste_qty).label('waste'),
        func.sum((DailyLog.sold_dine_in + DailyLog.sold_delivery) * FoodItem.cost_per_unit).label('revenue') # Approximate Revenue
    ).join(FoodItem).filter(DailyLog.date >= week_ago).group_by(DailyLog.date).order_by(DailyLog.date).all()
    
    dates = [log.date.strftime('%Y-%m-%d') for log in weekly_logs]
    sales_data = [log.sold for log in weekly_logs]
    waste_data = [log.waste for log in weekly_logs]
    revenue_data = [log.revenue for log in weekly_logs]

    # 3. Top Wasted Items (All time or last month)
    top_waste = db.session.query(
        FoodItem.name,
        func.sum(DailyLog.waste_qty).label('total_waste')
    ).join(DailyLog).group_by(FoodItem.name).order_by(func.sum(DailyLog.waste_qty).desc()).limit(5).all()
    
    waste_labels = [item.name for item in top_waste]
    waste_values = [item.total_waste for item in top_waste]

    return render_template('dashboard.html', 
                           title='Dashboard',
                           prepared_today=prepared_today,
                           sold_today=sold_today,
                           waste_today=waste_today,
                           predicted_tomorrow=predicted_tomorrow,
                           dates=dates,
                           sales_data=sales_data,
                           revenue_data=revenue_data,
                           waste_data_chart=waste_data,
                           waste_labels=waste_labels,
                           waste_values=waste_values)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user)
        '''
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
        '''
        return redirect(url_for('main.dashboard'))
    return render_template('login.html', title='Sign In')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/entry', methods=['GET', 'POST'])
@login_required
def entry():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        try:
            food_id = int(request.form['food_item_id'])
            prepared = int(request.form['prepared_qty'])
            dine_in = int(request.form['sold_dine_in'])
            delivery = int(request.form['sold_delivery'])
            date_str = request.form['date']
            
            # Simple validation
            if prepared < (dine_in + delivery):
                flash('Error: Sold quantity cannot be greater than prepared quantity!')
                return redirect(url_for('main.entry'))

            log = DailyLog(
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                food_item_id=food_id,
                prepared_qty=prepared,
                sold_dine_in=dine_in,
                sold_delivery=delivery
            )
            log.calculate_waste_and_cost()
            db.session.add(log)
            db.session.commit()
            flash('Daily entry submitted successfully!')
            return redirect(url_for('main.dashboard'))
        except ValueError:
            flash('Invalid input data')
            return redirect(url_for('main.entry'))

    food_items = FoodItem.query.all()
    return render_template('entry.html', title='Daily Entry', today=datetime.today().strftime('%Y-%m-%d'), food_items=food_items)

@bp.route('/reports')
@login_required
def reports():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('reports.html', title='Reports')
from flask import jsonify
import json
from app.models import DeliveryOrder

@bp.route('/delivery')
def delivery_menu():
    import random
    food_items = FoodItem.query.all()
    # Inject random data for display (temporary attributes)
    for item in food_items:
        item.discount = random.choice([0, 5, 10, 15, 20, 25, 30])
        item.rating = round(random.uniform(3.5, 5.0), 1)
        item.review_count = random.randint(25, 500)
        item.free_delivery = random.choice([True, False, False, False]) # 25% chance
        
    return render_template('delivery_menu.html', title='Order Food', food_items=food_items)

@bp.route('/api/order', methods=['POST'])
def place_order():
    data = request.get_json()
    name = data.get('name')
    address = data.get('address')
    cart = data.get('cart') # {'1': {'qty':1}, ...}

    if not cart:
        return jsonify({'success': False, 'message': 'Empty cart'})

    # Simple JSON structure: {"Item Name": Qty} for display simplicity in kitchen
    # In real app, we might store IDs.
    items_summary = {}
    for pid, info in cart.items():
        items_summary[info['name']] = info['qty']

    order = DeliveryOrder(
        customer_name=name,
        address=address,
        items_json=json.dumps(items_summary)
    )
    if current_user.is_authenticated:
        order.user_id = current_user.id
    db.session.add(order)
    
    # Automate Data Connection: Update DailyLog
    today = datetime.now().date()
    # We need to map item names back to IDs to update logs
    # Optimization: Loading all food items to a dict for quick lookup
    all_food_items = {item.name.lower(): item for item in FoodItem.query.all()}
    
    for item_name_raw, qty in items_summary.items():
        # item_name might not match exactly if case differs, but we used .lower() in data attrs?
        # Actually in HTML we did {{ item.name | lower }} for data-name, but displayed {{ item.name }}
        # The addToCart JS uses name from data-name? No wait. 
        # In delivery_menu.html: data-name="{{ item.name }}" (line 71).
        # So it should be exact match. But let's be safe.
        food_item = all_food_items.get(item_name_raw.lower())
        
        # If found, update log
        if food_item:
            daily_log = DailyLog.query.filter_by(date=today, food_item_id=food_item.id).first()
            if not daily_log:
                daily_log = DailyLog(date=today, food_item_id=food_item.id, prepared_qty=0, sold_dine_in=0, sold_delivery=0)
                db.session.add(daily_log)
            
            daily_log.sold_delivery += int(qty)
            # Re-calculate waste (if prepared was entered previously)
            daily_log.calculate_waste_and_cost()
            
    db.session.commit()
    return jsonify({'success': True, 'order_id': order.id})

@bp.route('/delivery/kitchen')
@login_required
def delivery_kitchen():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    orders = DeliveryOrder.query.order_by(DeliveryOrder.timestamp.desc()).all()
    # Parse JSON for template
    for o in orders:
        o.items_dict = json.loads(o.items_json)
    return render_template('delivery_kitchen.html', title='Kitchen Orders', orders=orders)

@bp.route('/delivery/update/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = DeliveryOrder.query.get_or_404(order_id)
    order.status = 'Delivered'
    db.session.commit()
    # Log into DailyLog automatically? For now just track status.
    flash(f'Order #{order_id} marked as delivered.')
    return redirect(url_for('main.delivery_kitchen'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']
        
        if password != confirm:
            flash('Passwords do not match')
            return redirect(url_for('main.signup'))
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('main.signup'))
        
        # Default role is staff/customer for new signups
        new_user = User(username=username, email=email, role='customer')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('main.login'))
    return render_template('signup.html', title='Sign Up')

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('forgot_password.html', title='Reset Password')

@bp.route('/about')
def about():
    return render_template('about.html', title='About Us')

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='My Profile')
@bp.route('/add_food', methods=['GET', 'POST'])
@login_required
def add_food():
    if current_user.role != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        cost = float(request.form.get('cost'))
        image_url = request.form.get('image_url')

        if not image_url:
            image_url = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c' # Default image

        new_item = FoodItem(name=name, category=category, cost_per_unit=cost, image_url=image_url)
        db.session.add(new_item)
        db.session.commit()
        flash(f'{name} added to menu successfully!', 'success')
        return redirect(url_for('main.delivery_menu'))

    return render_template('add_food.html', title='Add Food Item')

@bp.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.profile'))
    
    users = User.query.all()
    return render_template('users.html', title='Manage Users', users=users)
