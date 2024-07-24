from extensions import db
from datetime import datetime, timedelta
from random import randint, choice
from app import app  # Adjust this import based on your actual app module
from models import User, Purchase, Sale, Stock  # Adjust the import based on your project structure

app.app_context().push()

# Define product categories and vendors
categories = ['Electronics', 'Clothing', 'Home Appliances', 'Books', 'Toys', 'Cosmetics']
vendors = ['Vendor A', 'Vendor B', 'Vendor C', 'Vendor D']
payment_modes = ['Cash', 'Credit Card', 'Debit Card', 'Online Payment']

# Function to generate a random date between 2022 and 2024
def random_date(start_year=2022, end_year=2024):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Generate dummy users
users = [
    User(username='john_doe', email='john.doe@example.com', password='password'),
    User(username='jane_smith', email='jane.smith@example.com', password='password'),
    User(username='bob_jones', email='bob.jones@example.com', password='password')
]

# Add users to the session
for user in users:
    db.session.add(user)
db.session.commit()

# Generate dummy purchases
for _ in range(2000):
    product_name = choice(categories)
    unit = 'unit'
    quantity = randint(1, 1000)
    purchase_date = random_date()
    vendor = choice(vendors)
    per_unit_price = randint(10, 1000) + randint(0, 99) / 100.0
    purchase_price = per_unit_price * quantity
    payment_mode = choice(payment_modes)

    # Record purchase
    purchase = Purchase(
        product_name=product_name,
        unit=unit,
        quantity=quantity,
        purchase_date=purchase_date,
        vendor=vendor,
        per_unit_price=per_unit_price,
        purchase_price=purchase_price,
        payment_mode=payment_mode,
        user_id=choice([user.id for user in users])
    )
    db.session.add(purchase)

    # Update or create stock record
    stock = Stock.query.filter_by(product_name=product_name, unit=unit).first()
    if stock:
        stock.quantity += quantity
    else:
        stock = Stock(
            product_name=product_name,
            unit=unit,
            quantity=quantity
        )
        db.session.add(stock)

db.session.commit()

# Generate dummy sales
for _ in range(2000):
    product_name = choice(categories)
    unit_price = randint(10, 1000) + randint(0, 99) / 100.0
    quantity = randint(1, 10)
    total_price = unit_price * quantity

    # Check if there is sufficient stock available
    stock = Stock.query.filter_by(product_name=product_name, unit='unit').first()
    if stock and stock.quantity >= quantity:
        # Record the sale
        sale = Sale(
            product_name=product_name,
            unit='unit',
            quantity=quantity,
            sale_date=random_date(),
            unit_price=unit_price,
            total_price=total_price,
            payment_mode=choice(payment_modes),
            user_id=choice([user.id for user in users])
        )
        db.session.add(sale)

        # Update stock after the sale
        stock.quantity -= quantity
        if stock.quantity < 0:
            stock.quantity = 0  # Ensure stock never goes negative

    else:
        print(f"Not enough stock for {product_name}. Skipping sale.")

    db.session.add(stock)  # Update the stock record after each sale

db.session.commit()

print("Dummy data (purchases and sales) inserted successfully!")
