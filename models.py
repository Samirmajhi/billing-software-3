from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    sales = db.relationship('Sale', backref='user', lazy=True)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    vendor = db.Column(db.String(100), nullable=False)
    per_unit_price = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    payment_mode = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f'<Purchase {self.product_name} ({self.purchase_date}): {self.purchase_price}>'
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    payment_mode = db.Column(db.String(100), nullable=False)  # Add this line
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f'<Sale {self.product_name} ({self.sale_date}): {self.total_price}>'
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    __table_args__ = (db.UniqueConstraint('product_name', 'unit', name='uix_stock_product_unit'),)

    def __repr__(self):
        return f'<Stock {self.product_name} ({self.unit}): {self.quantity}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'unit': self.unit,
            'quantity': self.quantity,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }
    

class Conversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False, unique=True)
    conversion_factor = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Conversion {self.product_name}: {self.conversion_factor}>'
