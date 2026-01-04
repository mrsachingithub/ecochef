from app import create_app, db
from app.models import User, FoodItem

app = create_app()

with app.app_context():
    print("Seeding data...")
    
    # Create Admin Code
    if not User.query.filter_by(username='admin').first():
        u = User(username='admin', email='admin@example.com', role='admin')
        u.set_password('password')
        db.session.add(u)
        print("Admin user created.")

    # Rename Choco Lava Cake to Egg Curry if exists
    choco = FoodItem.query.filter_by(name='Choco Lava Cake').first()
    if choco:
        choco.name = 'Egg Curry'
        choco.category = 'Main Course' 
        choco.cost_per_unit = 100.0
        db.session.commit()
        print("Renamed Choco Lava Cake to Egg Curry")

    # Rename Pasta Alpha to Pasta if exists
    pasta = FoodItem.query.filter_by(name='Pasta Alpha').first()
    if pasta:
        pasta.name = 'Pasta'
        db.session.commit()
        print("Renamed Pasta Alpha to Pasta")

    # Rename Rice Bowl to Paneer Fried Rice if exists
    rice = FoodItem.query.filter_by(name='Rice Bowl').first()
    if rice:
        rice.name = 'Paneer Fried Rice'
        rice.cost_per_unit = 120.0
        db.session.commit()
        print("Renamed Rice Bowl to Paneer Fried Rice")

    # Create Food Items
    # Expanded Menu as per request
    items = [
        # Fast Food
        ('Veg Burger', 'Fast Food', 40.0, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80'),
        ('Manchurian', 'Fast Food', 70.0, '/static/images/manchurian.jpg'),
        ('Cheese Pizza', 'Fast Food', 120.0, 'https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80'),
        ('Pasta', 'Fast Food', 80.0, '/static/images/pasta.jpg'),
        ('Momos', 'Fast Food', 50.0, '/static/images/momo.jpg'),
        ('Samosa', 'Snacks', 20.0, 'https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80'),
        ('Aloo Patties', 'Snacks', 25.0, '/static/images/aloo_patties.png'),
        ('Pav Bhaji', 'Fast Food', 90.0, '/static/images/pav_bhaji.jpg'),
        ('Chhole Bhature', 'Main Course', 100.0, '/static/images/chhole_bhature.jpg'),
        
        # South Indian
        ('Idly Sambar', 'South Indian', 40.0, '/static/images/idly_sambar.jpg'),
        ('Masala Dosa', 'South Indian', 80.0, '/static/images/masala_dosa.jpg'), # Using similar placeholder if specific one not found easily
        
        # Main Course
        ('Paneer Fried Rice', 'Main Course', 120.0, '/static/images/paneer_fried_rice.jpg'),
        ('Aloo Paratha', 'Main Course', 60.0, '/static/images/aloo_paratha.jpg'),
        ('Fried Chicken', 'Main Course', 180.0, '/static/images/fried_chicken.jpg'),
        ('Veg Thali', 'Main Course', 150.0, 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80'),
        ('Roti', 'Main Course', 10.0, '/static/images/roti.jpg'), 
        
        # New Additions
        ('Chicken Pizza', 'Fast Food', 200.0, 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80'),
        ('Corn Pizza', 'Fast Food', 150.0, 'https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80'),
        ('Chicken Momos', 'Fast Food', 80.0, '/static/images/chicken_momos.jpg'),
        ('Fried Momos', 'Fast Food', 90.0, '/static/images/fried_momos.jpg'),
        ('Veg Burger', 'Fast Food', 60.0, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80'),
        ('Chicken Burger', 'Fast Food', 100.0, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80'),
        ('Gulab Jamun', 'Dessert', 50.0, 'https://images.unsplash.com/photo-1589119908995-c6837fa14848?auto=format&fit=crop&w=800&q=80'),
        ('Ice Cream', 'Dessert', 60.0, 'https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?auto=format&fit=crop&w=800&q=80'),
        ('Brownie', 'Dessert', 90.0, '/static/images/brownie.jpg'),
        ('Coke', 'Snacks', 40.0, 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80'),
        ('French Fries', 'Snacks', 70.0, '/static/images/french_fries.jpg'),
        
        # Others
        ('Green Salad', 'Starter', 30.0, 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80'),
        ('Egg Curry', 'Main Course', 100.0, '/static/images/egg_curry.jpg')
    ]

    for name, cat, cost, img in items:
        existing = FoodItem.query.filter_by(name=name).first()
        if not existing:
            item = FoodItem(name=name, category=cat, cost_per_unit=cost, image_url=img)
            db.session.add(item)
            print(f"Added {name}")

        else:
            # Update image if exists
            existing.image_url = img
            existing.category = cat
            print(f"Updated {name}")
    
    db.session.commit()
    print("Seeding complete.")
