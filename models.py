from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # New fields for social features
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    location = db.Column(db.String(200))
    is_seller = db.Column(db.Boolean, default=False)
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    
    # Existing relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    cart = db.relationship('Cart', backref='user', uselist=False, lazy=True)
    reviews = db.relationship('Review', backref='author', lazy=True)
    subscriptions = db.relationship('Subscription', backref='subscriber', lazy=True)
    
    # New relationships for social features
    food_posts = db.relationship('FoodPost', back_populates='user', lazy=True)
    
    sent_messages = db.relationship('Message', 
                                   foreign_keys='Message.sender_id', 
                                   back_populates='sender', 
                                   lazy=True)
    
    received_messages = db.relationship('Message', 
                                       foreign_keys='Message.receiver_id', 
                                       back_populates='receiver', 
                                       lazy=True)
    
    customer_orders = db.relationship('FoodOrder', 
                                     foreign_keys='FoodOrder.customer_id', 
                                     back_populates='customer', 
                                     lazy=True)
    
    seller_orders = db.relationship('FoodOrder', 
                                   foreign_keys='FoodOrder.seller_id', 
                                   back_populates='seller', 
                                   lazy=True)
    
    # Relationships for likes and comments
    post_likes = db.relationship('PostLike', 
                                back_populates='user', 
                                lazy=True, 
                                cascade='all, delete-orphan')
    
    post_comments = db.relationship('PostComment', 
                                   back_populates='user', 
                                   lazy=True, 
                                   cascade='all, delete-orphan')
    
    # FOLLOWERS - Corrected relationships with proper back_populates
    following_relationships = db.relationship('Follower', 
                                             foreign_keys='Follower.follower_id',
                                             back_populates='follower',
                                             lazy='dynamic',
                                             cascade='all, delete-orphan')
    
    follower_relationships = db.relationship('Follower', 
                                            foreign_keys='Follower.followed_id',
                                            back_populates='followed',
                                            lazy='dynamic',
                                            cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """Food category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    # Relationships
    tiffins = db.relationship('TiffinService', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'


class TiffinService(db.Model):
    """Tiffin service model"""
    __tablename__ = 'tiffin_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    delivery_time = db.Column(db.String(100))
    min_order_days = db.Column(db.Integer, default=1)
    is_veg = db.Column(db.Boolean, default=True)
    is_available = db.Column(db.Boolean, default=True)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    opening_time = db.Column(db.String(5))
    closing_time = db.Column(db.String(5))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sample_menu = db.Column(db.JSON)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='tiffin', lazy=True)
    cart_items = db.relationship('CartItem', backref='tiffin', lazy=True)
    reviews = db.relationship('Review', backref='tiffin_service', lazy=True)
    subscriptions = db.relationship('Subscription', backref='tiffin_service', lazy=True)
    
    def __repr__(self):
        return f'<TiffinService {self.name}>'


class Order(db.Model):
    """Order model"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_instructions = db.Column(db.Text)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    """Order item model"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    tiffin_id = db.Column(db.Integer, db.ForeignKey('tiffin_services.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'


class Cart(db.Model):
    """Shopping cart model"""
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Cart {self.id}>'


class CartItem(db.Model):
    """Cart item model"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    tiffin_id = db.Column(db.Integer, db.ForeignKey('tiffin_services.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CartItem {self.id}>'


class Subscription(db.Model):
    """Subscription model for recurring orders"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tiffin_id = db.Column(db.Integer, db.ForeignKey('tiffin_services.id'), nullable=False)
    days_per_week = db.Column(db.Integer, nullable=False)
    duration_weeks = db.Column(db.Integer, nullable=False)
    total_meals = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_time = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Subscription {self.id}>'


class Review(db.Model):
    """Review model for tiffin services"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tiffin_id = db.Column(db.Integer, db.ForeignKey('tiffin_services.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id}>'


class Payment(db.Model):
    """Payment model"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(100))
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id}>'


# ==================== NEW MODELS FOR SOCIAL FEATURES ====================

class FoodPost(db.Model):
    """Food post model for Instagram-style posts"""
    __tablename__ = 'food_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_type = db.Column(db.String(10))
    media_url = db.Column(db.String(500))
    caption = db.Column(db.Text)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, nullable=True)
    quantity_available = db.Column(db.Integer, default=0)
    location = db.Column(db.String(200))
    post_type = db.Column(db.String(20))
    availability_status = db.Column(db.String(20), default='available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='food_posts')
    likes = db.relationship('PostLike', back_populates='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('PostComment', back_populates='post', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('FoodOrder', back_populates='post', lazy=True)


class PostLike(db.Model):
    """Post likes model"""
    __tablename__ = 'post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('food_posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
    
    # Relationships
    user = db.relationship('User', back_populates='post_likes')
    post = db.relationship('FoodPost', back_populates='likes')


class PostComment(db.Model):
    """Post comments model"""
    __tablename__ = 'post_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('food_posts.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='post_comments')
    post = db.relationship('FoodPost', back_populates='comments')


class FoodOrder(db.Model):
    """Food orders from social posts"""
    __tablename__ = 'food_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('food_posts.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_instructions = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], back_populates='customer_orders')
    seller = db.relationship('User', foreign_keys=[seller_id], back_populates='seller_orders')
    post = db.relationship('FoodPost', back_populates='orders')


class Follower(db.Model):
    """Follower relationship model - FIXED VERSION"""
    __tablename__ = 'followers'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)
    
    # Relationships - Properly linked to User model
    follower = db.relationship('User', 
                              foreign_keys=[follower_id], 
                              back_populates='following_relationships',
                              lazy=True)
    
    followed = db.relationship('User', 
                              foreign_keys=[followed_id], 
                              back_populates='follower_relationships',
                              lazy=True)


class Message(db.Model):
    """Messaging model for seller-buyer communication"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')