from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FloatField, IntegerField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from models import User

class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    """Registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    address = TextAreaField('Delivery Address', validators=[DataRequired(), Length(min=10, max=500)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class ProfileForm(FlaskForm):
    """Profile update form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    address = TextAreaField('Delivery Address', validators=[DataRequired(), Length(min=10, max=500)])
    password = PasswordField('New Password (leave blank to keep current)')
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('password')])

class TiffinSearchForm(FlaskForm):
    """Tiffin search form"""
    search = StringField('Search', validators=[Optional()])
    category = SelectField('Category', choices=[('', 'All Categories')], validators=[Optional()])
    min_price = FloatField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Max Price', validators=[Optional(), NumberRange(min=0)])
    food_type = SelectField('Food Type', choices=[
        ('', 'All'),
        ('veg', 'Vegetarian Only'),
        ('nonveg', 'Non-Vegetarian')
    ], validators=[Optional()])
    sort_by = SelectField('Sort By', choices=[
        ('rating_desc', 'Top Rated'),
        ('price_asc', 'Price: Low to High'),
        ('price_desc', 'Price: High to Low'),
        ('name_asc', 'Name: A to Z')
    ], validators=[Optional()])

class CheckoutForm(FlaskForm):
    """Checkout form"""
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired(), Length(min=10, max=500)])
    delivery_instructions = TextAreaField('Delivery Instructions (Optional)', validators=[Optional(), Length(max=500)])
    payment_method = SelectField('Payment Method', choices=[
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking')
    ], validators=[DataRequired()])
    
    # Card details (if card payment selected)
    card_number = StringField('Card Number', validators=[Optional(), Length(min=16, max=16)])
    card_expiry = StringField('Expiry (MM/YY)', validators=[Optional(), Length(min=5, max=5)])
    card_cvv = StringField('CVV', validators=[Optional(), Length(min=3, max=4)])
    
    # UPI details
    upi_id = StringField('UPI ID', validators=[Optional()])

class ReviewForm(FlaskForm):
    """Review form"""
    rating = SelectField('Rating', choices=[
        ('5', '5 - Excellent'),
        ('4', '4 - Very Good'),
        ('3', '3 - Good'),
        ('2', '2 - Fair'),
        ('1', '1 - Poor')
    ], validators=[DataRequired()], coerce=int)
    comment = TextAreaField('Your Review', validators=[DataRequired(), Length(min=10, max=500)])

class SubscriptionForm(FlaskForm):
    """Subscription form"""
    tiffin_id = HiddenField('Tiffin ID', validators=[DataRequired()])
    days_per_week = SelectField('Days per Week', choices=[
        ('1', '1 day/week'),
        ('2', '2 days/week'),
        ('3', '3 days/week'),
        ('4', '4 days/week'),
        ('5', '5 days/week'),
        ('6', '6 days/week'),
        ('7', '7 days/week')
    ], validators=[DataRequired()], coerce=int)
    duration_weeks = SelectField('Duration (Weeks)', choices=[
        ('1', '1 week'),
        ('2', '2 weeks'),
        ('4', '1 month'),
        ('8', '2 months'),
        ('12', '3 months')
    ], validators=[DataRequired()], coerce=int)
    delivery_time = SelectField('Preferred Delivery Time', choices=[
        ('07:00-08:00', '7:00 AM - 8:00 AM'),
        ('08:00-09:00', '8:00 AM - 9:00 AM'),
        ('09:00-10:00', '9:00 AM - 10:00 AM'),
        ('12:00-13:00', '12:00 PM - 1:00 PM'),
        ('18:00-19:00', '6:00 PM - 7:00 PM'),
        ('19:00-20:00', '7:00 PM - 8:00 PM')
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])