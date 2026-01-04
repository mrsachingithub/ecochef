import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from app.models import DailyLog, FoodItem

def predict_demand(food_item_id):
    """
    Predicts demand for the next day based on historical sales data.
    Uses Linear Regression on the last 30 days of data.
    """
    # Fetch last 30 days of logs for this item
    cutoff = datetime.utcnow().date() - timedelta(days=30)
    logs = DailyLog.query.filter(
        DailyLog.food_item_id == food_item_id,
        DailyLog.date >= cutoff
    ).order_by(DailyLog.date).all()

    if len(logs) < 3:
        # Not enough data, return a safe default (e.g., average or encoded default)
        # For this project, we'll return 0 or a base value if no data
        return 0

    df = pd.DataFrame([{
        'ordinal': log.date.toordinal(),
        'sold': log.sold_dine_in + log.sold_delivery
    } for log in logs])

    X = df[['ordinal']]
    y = df['sold']

    model = LinearRegression()
    model.fit(X, y)

    tomorrow = (datetime.utcnow().date() + timedelta(days=1)).toordinal()
    prediction = model.predict([[tomorrow]])
    
    return max(0, int(prediction[0]))

def predict_total_demand_tomorrow():
    """Sum of predictions for all food items"""
    items = FoodItem.query.all()
    total = 0
    for item in items:
        total += predict_demand(item.id)
    return total
