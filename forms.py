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
    """Checkout form - complete with all payment fields"""
    delivery_address = TextAreaField('Delivery Address', validators=[DataRequired(), Length(min=10, max=500)])
    delivery_instructions = TextAreaField('Delivery Instructions (Optional)', validators=[Optional(), Length(max=500)])
    payment_method = SelectField('Payment Method', choices=[
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking')
    ], validators=[DataRequired()])
    
    # Card details (only required if payment_method == 'card')
    card_number = StringField('Card Number', validators=[Optional(), Length(min=16, max=16, message='Card number must be 16 digits')])
    card_expiry = StringField('Expiry (MM/YY)', validators=[Optional(), Length(min=5, max=5, message='Use format MM/YY')])
    card_cvv = StringField('CVV', validators=[Optional(), Length(min=3, max=4, message='CVV must be 3 or 4 digits')])
    
    # UPI details (only required if payment_method == 'upi')
    upi_id = StringField('UPI ID', validators=[Optional(), Length(min=3, max=50)])
    
    # Net Banking details (only required if payment_method == 'netbanking')
    bank = SelectField('Select Bank', choices=[
        ('sbi', 'State Bank of India (SBI)'),
        ('hdfc', 'HDFC Bank'),
        ('icici', 'ICICI Bank'),
        ('axis', 'Axis Bank'),
        ('kotak', 'Kotak Mahindra Bank'),
        ('yes', 'Yes Bank')
    ], validators=[Optional()])
    
    # Custom validation to ensure payment details are provided when needed
    def validate(self, extra_validators=None):
        # Run standard validation first
        if not super(CheckoutForm, self).validate(extra_validators):
            return False
        
        # Additional conditional validation
        if self.payment_method.data == 'card':
            if not self.card_number.data or len(self.card_number.data.replace(' ', '')) != 16:
                self.card_number.errors.append('Valid card number is required')
                return False
            if not self.card_expiry.data or len(self.card_expiry.data) != 5:
                self.card_expiry.errors.append('Expiry date (MM/YY) is required')
                return False
            if not self.card_cvv.data or len(self.card_cvv.data) < 3:
                self.card_cvv.errors.append('Valid CVV is required')
                return False
        
        elif self.payment_method.data == 'upi':
            if not self.upi_id.data or '@' not in self.upi_id.data:
                self.upi_id.errors.append('Valid UPI ID (e.g., name@bank) is required')
                return False
        
        elif self.payment_method.data == 'netbanking':
            if not self.bank.data:
                self.bank.errors.append('Please select a bank')
                return False
        
        return True

class ReviewForm(FlaskForm):
    """Review form"""
    rating = SelectField('Rating', choices=[
        (5, '5 - Excellent'),
        (4, '4 - Very Good'),
        (3, '3 - Good'),
        (2, '2 - Fair'),
        (1, '1 - Poor')
    ], validators=[DataRequired()], coerce=int)
    comment = TextAreaField('Your Review', validators=[DataRequired(), Length(min=10, max=500)])

class SubscriptionForm(FlaskForm):
    """Subscription form"""
    tiffin_id = HiddenField('Tiffin ID', validators=[DataRequired()])
    days_per_week = SelectField('Days per Week', choices=[
        (1, '1 day/week'),
        (2, '2 days/week'),
        (3, '3 days/week'),
        (4, '4 days/week'),
        (5, '5 days/week'),
        (6, '6 days/week'),
        (7, '7 days/week')
    ], validators=[DataRequired()], coerce=int)
    duration_weeks = SelectField('Duration (Weeks)', choices=[
        (1, '1 week'),
        (2, '2 weeks'),
        (4, '1 month'),
        (8, '2 months'),
        (12, '3 months')
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
    