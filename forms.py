from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, StringField, PasswordField, SubmitField, EmailField, IntegerField, DateField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError , Optional, NumberRange
from models import User  # Adjust the import based on your project structure

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
from datetime import date

class PurchaseForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    unit = SelectField('Unit', choices=[('unit', 'Unit'), ('kg', 'Kg'), ('liter', 'Liter'), ('pieces', 'Pieces'), ('custom', 'Custom')], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    vendor = StringField('Vendor', validators=[DataRequired()])
    purchase_price = FloatField('Total Purchase Price', validators=[DataRequired(), NumberRange(min=0.01)])
    per_unit_price = FloatField('Per Unit Price', render_kw={'readonly': True})
    payment_mode = SelectField('Payment Mode', choices=[
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    purchase_date = StringField('Purchase Date', default=date.today().strftime('%Y-%m-%d'), render_kw={'readonly': True})
    is_bulk = BooleanField('Bulk Purchase')
    conversion_factor = IntegerField('Conversion Factor', default=1, validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Record Purchase')

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import date

class SalesForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    unit = SelectField('Unit', choices=[('unit', 'Unit'), ('kg', 'Kg'), ('liter', 'Liter'), ('pieces', 'Pieces'), ('custom', 'Custom')], validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.01)])
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0.01)])
    is_bulk = BooleanField('Bulk Sale')
    conversion_factor = FloatField('Conversion Factor', default=1, validators=[DataRequired(), NumberRange(min=0.01)])
    total_price = FloatField('Total Sales Price', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_mode = SelectField('Payment Mode', choices=[
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    sale_date = DateField('Sale Date', default=date.today, validators=[DataRequired()])
    submit = SubmitField('Record Sale')

    def validate_product_name(self, product_name):
        if product_name.data and product_name.data[0].isdigit():
            raise ValidationError('Product name cannot begin with a number.')

    def validate_quantity(self, quantity):
        if quantity.data <= 0:
            raise ValidationError('Quantity must be greater than zero.')

    def validate_unit_price(self, unit_price):
        if unit_price.data <= 0:
            raise ValidationError('Unit price must be greater than zero.')

    def validate_conversion_factor(self, conversion_factor):
        if conversion_factor.data <= 0:
            raise ValidationError('Conversion factor must be greater than zero.')

    def validate_total_price(self, total_price):
        calculated_total = self.quantity.data * self.unit_price.data * self.conversion_factor.data
        if abs(total_price.data - calculated_total) > 0.01:  # Allow for small float precision errors
            raise ValidationError('Total price does not match quantity * unit price * conversion factor.')

class StockForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired(), Length(min=1, max=100)])
    unit = StringField('Unit', validators=[DataRequired(), Length(min=1, max=50)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Stock')

    def validate_product_name(self, product_name):
        if product_name.data[0].isdigit():
            raise ValidationError('Product name cannot begin with a number.')

    def validate_quantity(self, quantity):
        if quantity.data < 0:
            raise ValidationError('Quantity cannot be negative.')
