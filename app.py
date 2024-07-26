
from flask import Flask, logging, render_template, redirect, url_for, flash, request, session, jsonify, Response
from pymysql import OperationalError
from extensions import db
from sqlalchemy import func
from forms import RegistrationForm, LoginForm, PurchaseForm, SalesForm
from models import User, Purchase, Sale, Stock, Conversion
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_migrate import Migrate
import pandas as pd
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy
import csv
from io import StringIO
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    return app
app = create_app()
migrate = Migrate(app, db)

from functools import wraps
from flask import session, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function




@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        new_user = User(username=username, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
        finally:
            db.session.remove()
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

from flask import render_template, redirect, url_for, flash, session
from forms import PurchaseForm
from models import Purchase
from datetime import datetime

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = PurchaseForm()
    if form.validate_on_submit():
        product_name = form.product_name.data
        unit = form.unit.data
        is_bulk = form.is_bulk.data
        conversion_factor = 1

        if is_bulk:
            conversion = Conversion.query.filter_by(product_name=product_name).first()
            if conversion:
                if conversion.conversion_factor != form.conversion_factor.data:
                    conversion.conversion_factor = form.conversion_factor.data
                    db.session.commit()
                conversion_factor = conversion.conversion_factor
            else:
                conversion_factor = form.conversion_factor.data
                new_conversion = Conversion(product_name=product_name, conversion_factor=conversion_factor)
                db.session.add(new_conversion)
                db.session.commit()
        else:
            conversion_factor = 1

        quantity_in_units = form.quantity.data * conversion_factor

        new_purchase = Purchase(
            product_name=product_name,
            unit=unit,
            quantity=quantity_in_units,
            purchase_date=datetime.strptime(form.purchase_date.data, '%Y-%m-%d'),
            vendor=form.vendor.data,
            per_unit_price=form.per_unit_price.data,
            purchase_price=form.purchase_price.data,
            payment_mode=form.payment_mode.data,
            user_id=session['user_id']
        )
        try:
            db.session.add(new_purchase)

            stock = Stock.query.filter_by(product_name=product_name, unit=unit).first()
            if stock:
                stock.quantity += quantity_in_units
            else:
                stock = Stock(
                    product_name=product_name,
                    unit=unit,
                    quantity=quantity_in_units
                )
                db.session.add(stock)

            db.session.commit()
            flash('Purchase recorded successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('purchase.html', form=form)





@app.route('/get_conversion_factor/<product_name>', methods=['GET'])
def get_conversion_factor(product_name):
    conversion = Conversion.query.filter_by(product_name=product_name).first()
    if conversion:
        return jsonify({'conversion_factor': conversion.conversion_factor})
    return jsonify({'conversion_factor': 1})



from flask import flash


from flask import render_template, redirect, url_for, flash, session, request, jsonify
from forms import SalesForm
from models import Sale, Purchase
from datetime import datetime

# Routes
@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if 'user_id' not in session: 
        return redirect(url_for('login'))

    form = SalesForm()
    if form.validate_on_submit():
        product_name = form.product_name.data
        unit = form.unit.data
        is_bulk = form.is_bulk.data
        conversion_factor = 1

        if is_bulk:
            conversion = Conversion.query.filter_by(product_name=product_name).first()
            if conversion:
                if conversion.conversion_factor != form.conversion_factor.data:
                    conversion.conversion_factor = form.conversion_factor.data
                    db.session.commit()
                conversion_factor = conversion.conversion_factor
            else:
                conversion_factor = form.conversion_factor.data
                new_conversion = Conversion(product_name=product_name, conversion_factor=conversion_factor)
                db.session.add(new_conversion)
                db.session.commit()
        else:
            conversion_factor = 1

        quantity_in_units = form.quantity.data * conversion_factor

        stock = Stock.query.filter_by(product_name=product_name, unit=unit).first()

        if not stock or stock.quantity < quantity_in_units:
            flash(f'Not enough stock available for {product_name}. Current stock: {stock.quantity if stock else 0}', 'danger')
        else:
            new_sale = Sale(
                product_name=product_name,
                unit=unit,
                sale_date=form.sale_date.data,
                quantity=quantity_in_units,
                unit_price=form.unit_price.data,
                total_price=form.total_price.data,
                payment_mode=form.payment_mode.data,
                user_id=session['user_id']
            )
            try:
                db.session.add(new_sale)
                stock.quantity -= quantity_in_units
                db.session.commit()
                flash('Sale recorded successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('sales.html', form=form)

@app.route('/api/check_stock', methods=['GET'])
def check_stock():
    product_name = request.args.get('product_name')

    if not product_name:
        return jsonify({'error': 'Product name is required.'}), 400

    current_stock = get_current_stock(product_name)
    return jsonify({'current_stock': current_stock})

def get_current_stock(product_name):
    try:
        stock_item = Stock.query.filter_by(product_name=product_name).first()
        if stock_item:
            return stock_item.quantity
        return 0
    except OperationalError as e:
        logging.error(f"Database error: {e}")
        return 0
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 0
# Setup logging for error tracking
# logging.basicConfig(level=logging.ERROR)

# @app.route('/api/product_suggestions', methods=['GET'])
# def product_suggestions():
#     query = request.args.get('query', '').lower()
#     products = db.session.query(Purchase.product_name, Purchase.unit).distinct().all()
#     print(f"Products in DB: {products}")  # Debugging line
#     suggestions = []
#     for product_name, unit in products:
#         if query in product_name.lower():
#             current_stock = get_current_stock(product_name)
#             suggestions.append({
#                 'name': product_name,
#                 'unit': unit,
#                 'in_stock': current_stock > 0
#             })
#     print(f"Suggestions: {suggestions}")  # Debugging line
#     return jsonify(suggestions)

# def get_current_stock(product_name):
#     try:
#         stock_item = Stock.query.filter_by(product_name=product_name).first()
#         if stock_item:
#             print(f"Stock Item Found: {stock_item.product_name} - Quantity: {stock_item.quantity}")
#             return stock_item.quantity
#         print(f"No Stock Item Found for: {product_name}")
#         return 0
#     except OperationalError as e:
#         logging.error(f"Database error: {e}")
#         return 0
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#         return 0




from collections import defaultdict
from datetime import datetime

from flask import request, jsonify, Response
from sqlalchemy import desc
import csv
from io import StringIO
from datetime import datetime
@app.route('/stock')
def stock():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('stock.html')

@app.route('/api/stock')
def get_stock():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'product_name')
    order = request.args.get('order', 'asc')
    stock_level = request.args.get('stock_level', '')

    query = Stock.query

    if search:
        query = query.filter(Stock.product_name.ilike(f'%{search}%'))

    if stock_level:
        if stock_level == 'Low':
            query = query.filter(Stock.quantity < 100)
        elif stock_level == 'Medium':
            query = query.filter(Stock.quantity.between(100, 499))
        elif stock_level == 'High':
            query = query.filter(Stock.quantity >= 500)

    if order == 'desc':
        query = query.order_by(desc(getattr(Stock, sort)))
    else:
        query = query.order_by(getattr(Stock, sort))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    stock_items = pagination.items

    return jsonify({
        'items': [item.to_dict() for item in stock_items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })

@app.route('/export-stock-csv')
def export_stock_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    stock_items = Stock.query.all()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Product Name', 'Unit', 'Quantity', 'Stock Level', 'Last Updated'])
    
    for item in stock_items:
        if item.quantity < 100:
            stock_level = 'Low'
        elif item.quantity < 500:
            stock_level = 'Medium'
        else:
            stock_level = 'High'
        cw.writerow([item.product_name, item.unit, item.quantity, stock_level, item.last_updated.strftime('%Y-%m-%d %H:%M:%S')])

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=stock_report.csv"}
    )
# @app.route('/stock')
# def stock():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     stock_items = calculate_current_stock()
#     return render_template('stock.html', stock_items=stock_items)

# def calculate_current_stock():
#     purchases = Purchase.query.order_by(Purchase.purchase_date).all()
#     sales = Sale.query.order_by(Sale.sale_date).all()
#     stock = defaultdict(lambda: {'quantity': 0, 'last_purchase_date': None, 'last_sale_date': None})
    
#     for purchase in purchases:
#         key = (purchase.product_name, purchase.unit)
#         stock[key]['quantity'] += purchase.quantity
#         stock[key]['last_purchase_date'] = purchase.purchase_date

#     for sale in sales:
#         key = (sale.product_name, sale.unit)
#         if key in stock and stock[key]['quantity'] >= sale.quantity:
#             stock[key]['quantity'] -= sale.quantity
#             stock[key]['last_sale_date'] = sale.sale_date
#         else:
#             print(f"Warning: Attempted to sell more {key} than available in stock")

#     stock_items = [
#         {
#             'product_name': k[0],
#             'unit': k[1],
#             'quantity': v['quantity'],
#             'last_purchase_date': v['last_purchase_date'],
#             'last_sale_date': v['last_sale_date'],
#             'days_since_last_purchase': (datetime.now() - v['last_purchase_date']).days if v['last_purchase_date'] else None,
#             'days_since_last_sale': (datetime.now() - v['last_sale_date']).days if v['last_sale_date'] else None
#         }
#         for k, v in stock.items()
#     ]

#     return stock_items
from datetime import datetime
from collections import defaultdict

from flask import request, jsonify

def get_purchase_sales_details(page=1, per_page=10, search=''):
    purchases = Purchase.query.order_by(Purchase.purchase_date).all()
    sales = Sale.query.order_by(Sale.sale_date).all()
    details_dict = defaultdict(lambda: {'purchases': [], 'sales': [], 'current_stock': 0})

    for purchase in purchases:
        key = (purchase.product_name, purchase.unit)
        details_dict[key]['purchases'].append(purchase)
        details_dict[key]['current_stock'] += purchase.quantity

    for sale in sales:
        key = (sale.product_name, sale.unit)
        if key in details_dict and details_dict[key]['current_stock'] >= sale.quantity:
            details_dict[key]['sales'].append(sale)
            details_dict[key]['current_stock'] -= sale.quantity
        else:
            print(f"Warning: Attempted to sell more {key} than available in stock")

    # Filter details by search term
    if search:
        details_dict = {k: v for k, v in details_dict.items() if search.lower() in k[0].lower()}

    details = [
        {
            'product_name': k[0],
            'unit': k[1],
            'purchase_date': v['purchases'][0].purchase_date if v['purchases'] else None,
            'first_sale_date': v['sales'][0].sale_date if v['sales'] else None,
            'days_diff': (v['sales'][0].sale_date - v['purchases'][0].purchase_date).days if v['purchases'] and v['sales'] else None,
            'sales': v['sales']
        }
        for k, v in details_dict.items()
    ]

    # Pagination
    total_items = len(details)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_details = details[start:end]

    total_pages = (total_items + per_page - 1) // per_page

    return {
        'items': paginated_details,
        'total_items': total_items,
        'total_pages': total_pages,
        'current_page': page
    }





from flask import send_file
import io
import csv

@app.route('/details')
def details():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if export parameter is present
    if request.args.get('export') == 'csv':
        details = get_purchase_sales_details()  # Fetch the data
        return export_to_csv(details)  # Export to CSV
    
    # Handle pagination and search
    page = int(request.args.get('page', 1))
    search = request.args.get('search', '')

    details = get_purchase_sales_details(page=page, search=search)  # Fetch paginated data

    # Debugging: Print details to verify data
    for d in details['items']:
        print(f"Product: {d['product_name']}, Sales: {d['sales']}, Days Diff: {d['days_diff']}")
    
    return render_template('details.html', details=details['items'], current_page=details['current_page'], total_pages=details['total_pages'], search=search)




from io import StringIO
import csv
from flask import Response

def export_to_csv(details):
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Product Name', 'Purchase Date', 'Sales Date', 'Days to Sale'])
    
    for detail in details['items']:
        cw.writerow([
            detail['product_name'],
            detail['purchase_date'].strftime('%Y-%m-%d') if detail['purchase_date'] else 'N/A',
            detail['first_sale_date'].strftime('%Y-%m-%d') if detail['first_sale_date'] else 'No Sales Yet',
            detail['days_diff'] if detail['days_diff'] is not None else '-'
        ])
    
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=details_report.csv"}
    )










def get_purchases_data():
    # Query the purchases data
    purchases = Purchase.query.all()
    labels = [purchase.product_name for purchase in purchases]
    values = [purchase.purchase_price for purchase in purchases]
    return {'labels': labels, 'values': values}

def get_stock_data():
    # Query the stock data
    purchases = Purchase.query.all()
    stock = {}
    for purchase in purchases:
        if purchase.product_name in stock:
            stock[purchase.product_name] += purchase.quantity
        else:
            stock[purchase.product_name] = purchase.quantity

    labels = list(stock.keys())
    values = list(stock.values())
    return {'labels': labels, 'values': values}

# @app.route('/api/summary')
# def api_summary():
#     if 'user_id' not in session:
#         return jsonify({'error': 'Unauthorized'}), 401

#     total_sales = db.session.query(db.func.sum(Sale.total_price)).scalar() or 0
#     total_purchases = db.session.query(db.func.sum(Purchase.purchase_price)).scalar() or 0

#     purchases = Purchase.query.all()
#     sales = Sale.query.all()
#     stock = {}

#     for purchase in purchases:
#         key = (purchase.product_name, purchase.unit)
#         if key not in stock:
#             stock[key] = purchase.quantity
#         else:
#             stock[key] += purchase.quantity

#     for sale in sales:
#         key = (sale.product_name, sale.unit)
#         if key in stock:
#             stock[key] -= sale.quantity

#     current_stock = sum(quantity for quantity in stock.values() if quantity > 0)

#     return jsonify({
#         'total_sales': total_sales,
#         'total_purchases': total_purchases,
#         'current_stock': current_stock
#     })

from datetime import datetime, timedelta
from flask import jsonify, request, session

from datetime import datetime, timedelta
from flask import jsonify, request, session

from datetime import datetime, timedelta
from flask import jsonify, request, session
@app.route('/api/products', methods=['GET'])
def get_products():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        products = db.session.query(Purchase.product_name).distinct().all()
        product_list = [product[0] for product in products]
        return jsonify({'products': product_list})
    except OperationalError as e:
        logging.error(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred.'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    
@app.route('/api/vendors', methods=['GET'])
def get_vendors():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        vendors = db.session.query(Purchase.vendor).distinct().all()
        vendor_list = [vendor[0] for vendor in vendors]
        return jsonify({'vendors': vendor_list})
    except OperationalError as e:
        logging.error(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred.'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

from sqlalchemy import cast, Date
from sqlalchemy import func, cast, Date, text
from datetime import datetime, timedelta
from flask import jsonify, request, session
from sqlalchemy import func, text


@app.route('/api/chart-data')
def chart_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    filter = request.args.get('filter', 'all')
    product = request.args.get('product')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    today = datetime.now()
    if filter == 'today':
        start_date = (today - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)

        end_date = (today + timedelta(days=1)).replace(hour=0, minute=0, second=1, microsecond=0)

    elif filter == 'custom' and start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    elif filter == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    elif filter == 'month':
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif filter == 'year':
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:  # 'all' or any other case
        start_date = datetime(2000, 1, 1)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)


    sales_data = get_sales_data(start_date, end_date, product)
    purchases_data = get_purchases_data(start_date, end_date, product)
    top_selling_data = get_top_selling_data(start_date, end_date, product)
    current_stock = get_current_stock(end_date, product)

 
    

    data = {
        'sales': sales_data,
        'purchases': purchases_data,
        'topSelling': top_selling_data,
        'totalSales': sum(sales_data['values']),
        'totalPurchases': sum(purchases_data['values']),
        'currentStock': current_stock
    }
    
    return jsonify(data)
from datetime import datetime, timedelta

def get_sales_data(start_date, end_date, product=None):
    # Convert datetime objects to strings in ISO format
    start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    query = db.session.query(
        func.date(Sale.sale_date).label('date'),
        func.sum(Sale.total_price).label('total')
    ).filter(
        Sale.sale_date.between(start_str, end_str)
    )
    if product:
        query = query.filter(Sale.product_name == product)
    
    sales = query.group_by(
        func.date(Sale.sale_date)
    ).order_by(
        func.date(Sale.sale_date)
    ).all()

    labels = []
    values = []
    for sale in sales:
        labels.append(str(sale.date))
        values.append(float(sale.total))

    return {'labels': labels, 'values': values}

def get_purchases_data(start_date, end_date, product=None):
    # Convert datetime objects to strings in ISO format
    start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    query = db.session.query(
        func.date(Purchase.purchase_date).label('date'),
        func.sum(Purchase.purchase_price).label('total')
    ).filter(
        Purchase.purchase_date.between(start_str, end_str)
    )
    if product:
        query = query.filter(Purchase.product_name == product)

    purchases = query.group_by(
        func.date(Purchase.purchase_date)
    ).order_by(
        func.date(Purchase.purchase_date)
    ).all()


    labels = []
    values = []
    for purchase in purchases:
        labels.append(str(purchase.date))
        values.append(float(purchase.total))

    return {'labels': labels, 'values': values}
def get_top_selling_data(start_date, end_date, product=None):
    query = db.session.query(
        Sale.product_name,
        func.sum(Sale.quantity).label('total_quantity')
    ).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    )
    if product:
        query = query.filter(Sale.product_name == product)
    
    top_selling = query.group_by(
        Sale.product_name
    ).order_by(
        func.sum(Sale.quantity).desc()
    ).limit(5).all()


    labels = [item.product_name for item in top_selling]
    values = [item.total_quantity for item in top_selling]

    return {'labels': labels, 'values': values}

def get_current_stock(end_date, product=None):
    purchases = Purchase.query.filter(Purchase.purchase_date <= end_date)
    sales = Sale.query.filter(Sale.sale_date <= end_date)
    
    if product:
        purchases = purchases.filter(Purchase.product_name == product)
        sales = sales.filter(Sale.product_name == product)

    stock = {}

    for purchase in purchases:
        key = (purchase.product_name, purchase.unit)
        if key not in stock:
            stock[key] = purchase.quantity
        else:
            stock[key] += purchase.quantity

    for sale in sales:
        key = (sale.product_name, sale.unit)
        if key in stock:
            stock[key] -= sale.quantity

    current_stock = sum(quantity for quantity in stock.values() if quantity > 0)



    return current_stock

@app.route('/data')
@login_required
def data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return render_template('data.html')

@app.route('/view_by_purchase')
@login_required
def view_by_purchase():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).all()
    columns = ['Product Name', 'Unit', 'Quantity', 'Purchase Date', 'Vendor', 'Per Unit Price', 'Purchase Price', 'Payment Mode']
    records = [[p.product_name, p.unit, p.quantity, p.purchase_date, p.vendor, p.per_unit_price, p.purchase_price, p.payment_mode] for p in purchases]
    return render_template('data.html', columns=columns, records=records, download_data_type='purchases')

@app.route('/view_by_sales')
@login_required
def view_by_sales():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    columns = ['Product Name', 'Unit', 'Quantity', 'Sale Date', 'Unit Price', 'Total Price']
    records = [[s.product_name, s.unit, s.quantity, s.sale_date, s.unit_price, s.total_price] for s in sales]
    return render_template('data.html', columns=columns, records=records, download_data_type='sales')


@app.route('/view_by_transaction_modes')
@login_required
def view_by_transaction_modes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    mode = request.args.get('mode')
    if mode:
        sales_data = Sale.query.filter_by(payment_mode=mode).all()
    else:
        sales_data = Sale.query.all()
    columns = ['Product Name', 'Unit', 'Quantity', 'Sale Date', 'Unit Price', 'Total Price', 'Payment Mode']
    records = [[s.product_name, s.unit, s.quantity, s.sale_date, s.unit_price, s.total_price, s.payment_mode] for s in sales_data]
    return render_template('data.html', columns=columns, records=records)

@app.route('/download_csv')
@login_required
def download_csv():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data_type = request.args.get('data_type', 'default')
    
    if data_type == 'purchases':
        data = Purchase.query.all()
        columns = ['Product Name', 'Unit', 'Quantity', 'Purchase Date', 'Vendor', 'Per Unit Price', 'Purchase Price', 'Payment Mode']
        file_name = 'purchases.csv'
    elif data_type == 'sales':
        data = Sale.query.all()
        columns = ['Product Name', 'Unit', 'Quantity', 'Sale Date', 'Unit Price', 'Total Price', 'Payment Mode']
        file_name = 'sales.csv'
    elif data_type == 'transaction_modes':
        mode = request.args.get('mode', '')
        if mode:
            data = Sale.query.filter_by(payment_mode=mode).all()
        else:
            data = Sale.query.all()
        columns = ['Product Name', 'Unit', 'Quantity', 'Sale Date', 'Unit Price', 'Total Price', 'Payment Mode']
        file_name = 'transaction_modes.csv'
    else:
        data = []
        columns = []
        file_name = 'data.csv'

    # Generate CSV
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(columns)
    
    for item in data:
        row = [getattr(item, col.lower().replace(' ', '_'), '') for col in columns]
        cw.writerow(row)
    
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={file_name}"}
    )


@app.route('/download_excel')
@login_required
def download_excel():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data_type = request.args.get('data_type', 'default')
    
    if data_type == 'purchases':
        data = Purchase.query.all()
        columns = ['Product Name', 'Unit', 'Quantity', 'Purchase Date', 'Vendor', 'Per Unit Price', 'Purchase Price', 'Payment Mode']
        file_name = 'purchases.xlsx'
    elif data_type == 'sales':
        data = Sale.query.all()
        columns = ['Product Name', 'Unit', 'Quantity', 'Sale Date', 'Unit Price', 'Total Price', 'Payment Mode']
        file_name = 'sales.xlsx'
    elif data_type == 'transaction_modes':
        mode = request.args.get('mode', '')
        if mode:
            data = Sale.query.filter_by(payment_mode=mode).all()
        else:
            data = Sale.query.all()
        columns = ['Product Name', 'Unit', 'Quantity', 'Sale Date', 'Unit Price', 'Total Price', 'Payment Mode']
        file_name = 'transaction_modes.xlsx'
    else:
        data = []
        columns = []
        file_name = 'data.xlsx'

    # Generate Excel
    df = pd.DataFrame([{col: getattr(item, col.lower().replace(' ', '_'), '') for col in columns} for item in data], columns=columns)
    excel_output = BytesIO()
    df.to_excel(excel_output, index=False)
    excel_output.seek(0)
    
    return Response(
        excel_output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-disposition": f"attachment; filename={file_name}"}
    )



if __name__ == '__main__':
    app.run(debug=True)
