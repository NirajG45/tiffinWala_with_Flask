from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import uuid
from sqlalchemy import or_

# Import all models
from models import (
    db, User, TiffinService, Category, Order, OrderItem,
    Cart, CartItem, Subscription, Review, Payment,
    FoodPost, Follower, FoodOrder, Notification, Comment,
    PostLike
)

# Import forms
from forms import LoginForm, RegistrationForm, TiffinSearchForm, CheckoutForm, ReviewForm, ProfileForm

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiffinwala.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login', next=request.path))

# Context processor
@app.context_processor
def utility_processor():
    return dict(now=datetime.now)

# ---------- Helper function ----------
def get_cart_count():
    """Get cart item count for current user or session"""
    if current_user.is_authenticated:
        cart = current_user.cart
        if cart:
            return db.session.query(db.func.sum(CartItem.quantity)).filter_by(cart_id=cart.id).scalar() or 0
        return 0
    else:
        if 'cart' in session:
            return sum(item['quantity'] for item in session['cart'])
        return 0

# ---------- Create tables and seed data ----------
with app.app_context():
    db.create_all()
    
    # Create default categories if none exist
    if Category.query.count() == 0:
        categories = [
            Category(name='Vegetarian', icon='fas fa-leaf', description='Pure vegetarian meals'),
            Category(name='Non-Vegetarian', icon='fas fa-drumstick-bite', description='Delicious non-veg dishes'),
            Category(name='Jain', icon='fas fa-peace', description='Jain food without onion/garlic'),
            Category(name='Diet', icon='fas fa-apple-alt', description='Calorie-controlled healthy meals'),
            Category(name='Kids Special', icon='fas fa-child', description='Kid-friendly meals'),
            Category(name='Diabetic', icon='fas fa-heartbeat', description='Sugar-free diabetic meals'),
            Category(name='High Protein', icon='fas fa-dumbbell', description='Protein-rich meals'),
            Category(name='Keto', icon='fas fa-bacon', description='Low-carb keto meals')
        ]
        db.session.add_all(categories)
        db.session.commit()
        
        # Sample tiffin services
        sample_tiffins = [
            TiffinService(
                name='Maa Ki Rasoi',
                description='Traditional home-style vegetarian meals with love and care.',
                price=180.00, category_id=1,
                image_url='https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&h=300&fit=crop',
                rating=4.8, total_reviews=245, delivery_time='7:00 AM - 9:00 AM',
                min_order_days=7, is_veg=True, is_available=True,
                address='Sitamarhi, Bihar', phone='+919876543210',
                email='maakirasoi@example.com',
                opening_time='07:00', closing_time='21:00',
                sample_menu=[{"name": "Dal Makhani", "price": 120}, {"name": "Paneer Butter Masala", "price": 150}]
            ),
            TiffinService(
                name='Healthy Bites',
                description='Calorie-counted diet meals for weight management.',
                price=250.00, category_id=4,
                image_url='https://images.unsplash.com/photo-1490818387583-1baba5e638af?w=400&h=300&fit=crop',
                rating=4.7, total_reviews=189, delivery_time='8:00 AM - 10:00 AM',
                min_order_days=5, is_veg=True, is_available=True,
                address='Patna, Bihar', phone='+919876543211', email='healthybites@example.com',
                opening_time='08:00', closing_time='22:00',
                sample_menu=[{"name": "Grilled Chicken Salad", "price": 180}]
            ),
            TiffinService(
                name='Royal Non-Veg',
                description='Premium non-vegetarian delicacies.',
                price=300.00, category_id=2,
                image_url='https://images.unsplash.com/photo-1600891964092-4316c288032e?w=400&h=300&fit=crop',
                rating=4.9, total_reviews=312, delivery_time='7:30 AM - 9:30 AM',
                min_order_days=7, is_veg=False, is_available=True,
                address='Muzaffarpur, Bihar', phone='+919876543212', email='royalnonveg@example.com',
                opening_time='07:30', closing_time='21:30',
                sample_menu=[{"name": "Chicken Biryani", "price": 220}]
            )
        ]
        db.session.add_all(sample_tiffins)
        db.session.commit()

# ---------- Redirect routes for .html URLs ----------
@app.route('/login.html')
def login_html_redirect():
    return redirect(url_for('login', next=request.args.get('next')))

@app.route('/register.html')
def register_html_redirect():
    return redirect(url_for('register'))

@app.route('/profile.html')
def profile_html_redirect():
    return redirect(url_for('profile'))

@app.route('/orders.html')
def orders_html_redirect():
    return redirect(url_for('orders'))

@app.route('/subscriptions.html')
def subscriptions_html_redirect():
    return redirect(url_for('subscriptions'))

@app.route('/cart.html')
def cart_html_redirect():
    return redirect(url_for('cart'))

@app.route('/checkout.html')
def checkout_html_redirect():
    return redirect(url_for('checkout'))

@app.route('/tiffins.html')
def tiffins_html_redirect():
    return redirect(url_for('tiffins'))

# ---------- Main routes ----------
@app.route('/')
def index():
    """Home page with featured tiffins and community posts (all users)"""
    featured_tiffins = TiffinService.query.filter_by(is_available=True).limit(6).all()
    categories = Category.query.all()
    food_posts = FoodPost.query.filter(
        FoodPost.media_url.isnot(None)
    ).order_by(FoodPost.created_at.desc()).limit(9).all()
    return render_template('index.html', 
                           tiffins=featured_tiffins, 
                           categories=categories,
                           food_posts=food_posts)

@app.route('/tiffins')
def tiffins():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search_query = request.args.get('search', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    food_type = request.args.get('food_type', '')
    sort_by = request.args.get('sort_by', 'rating_desc')
    
    query = TiffinService.query.filter_by(is_available=True)
    
    if category:
        query = query.join(Category).filter(Category.name.ilike(f'%{category}%'))
    if search_query:
        query = query.filter(
            or_(
                TiffinService.name.ilike(f'%{search_query}%'),
                TiffinService.description.ilike(f'%{search_query}%'),
                TiffinService.address.ilike(f'%{search_query}%')
            )
        )
    if min_price is not None:
        query = query.filter(TiffinService.price >= min_price)
    if max_price is not None:
        query = query.filter(TiffinService.price <= max_price)
    if food_type == 'veg':
        query = query.filter_by(is_veg=True)
    elif food_type == 'nonveg':
        query = query.filter_by(is_veg=False)
    
    if sort_by == 'price_asc':
        query = query.order_by(TiffinService.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(TiffinService.price.desc())
    elif sort_by == 'rating_desc':
        query = query.order_by(TiffinService.rating.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(TiffinService.name.asc())
    
    pagination = query.paginate(page=page, per_page=9, error_out=False)
    tiffins = pagination.items
    categories = Category.query.all()
    form = TiffinSearchForm()
    
    # Get seller-uploaded posts (approved sellers, with price, available)
    seller_posts = FoodPost.query.filter(
        FoodPost.user.has(is_seller=True),
        FoodPost.price.isnot(None),
        FoodPost.is_available == True
    ).order_by(FoodPost.created_at.desc()).limit(6).all()
    
    return render_template('tiffins.html',
                           tiffins=tiffins,
                           pagination=pagination,
                           categories=categories,
                           form=form,
                           seller_posts=seller_posts,
                           current_filters={'category': category, 'search': search_query,
                                             'min_price': min_price, 'max_price': max_price,
                                             'food_type': food_type, 'sort_by': sort_by})

@app.route('/tiffin/<int:tiffin_id>')
def tiffin_detail(tiffin_id):
    tiffin = TiffinService.query.get_or_404(tiffin_id)
    reviews = Review.query.filter_by(tiffin_id=tiffin_id).order_by(Review.created_at.desc()).limit(10).all()
    similar_tiffins = TiffinService.query.filter(
        TiffinService.category_id == tiffin.category_id,
        TiffinService.id != tiffin_id,
        TiffinService.is_available == True
    ).limit(3).all()
    review_form = ReviewForm()
    return render_template('tiffin_detail.html', tiffin=tiffin, reviews=reviews,
                           similar_tiffins=similar_tiffins, review_form=review_form,
                           now=datetime.now)

@app.route('/tiffin/<int:tiffin_id>/review', methods=['POST'])
@login_required
def add_review(tiffin_id):
    tiffin = TiffinService.query.get_or_404(tiffin_id)
    form = ReviewForm()
    if form.validate_on_submit():
        existing_review = Review.query.filter_by(user_id=current_user.id, tiffin_id=tiffin_id).first()
        if existing_review:
            flash('You have already reviewed this tiffin service.', 'warning')
            return redirect(url_for('tiffin_detail', tiffin_id=tiffin_id))
        
        review = Review(rating=form.rating.data, comment=form.comment.data,
                        user_id=current_user.id, tiffin_id=tiffin_id)
        db.session.add(review)
        
        reviews = Review.query.filter_by(tiffin_id=tiffin_id).all()
        tiffin.rating = (sum(r.rating for r in reviews) + review.rating) / (len(reviews) + 1)
        tiffin.total_reviews += 1
        db.session.commit()
        flash('Thank you for your review!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    return redirect(url_for('tiffin_detail', tiffin_id=tiffin_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        new_user = User(
            username=form.username.data, email=form.email.data,
            phone=form.phone.data, address=form.address.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
        cart = Cart(user_id=new_user.id)
        db.session.add(cart)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if 'cart' in session:
                cart = user.cart
                if not cart:
                    cart = Cart(user_id=user.id)
                    db.session.add(cart)
                    db.session.commit()
                for item in session['cart']:
                    existing = CartItem.query.filter_by(cart_id=cart.id, tiffin_id=item['tiffin_id']).first()
                    if existing:
                        existing.quantity += item['quantity']
                    else:
                        db.session.add(CartItem(cart_id=cart.id, tiffin_id=item['tiffin_id'],
                                                quantity=item['quantity'], price=item['price']))
                db.session.commit()
                session.pop('cart')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        if form.password.data:
            current_user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    posts = FoodPost.query.filter_by(user_id=current_user.id).order_by(FoodPost.created_at.desc()).all()
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    subscriptions = Subscription.query.filter_by(user_id=current_user.id, is_active=True).all()
    posts_count = FoodPost.query.filter_by(user_id=current_user.id).count()
    followers_count = Follower.query.filter_by(followed_id=current_user.id).count()
    following_count = Follower.query.filter_by(follower_id=current_user.id).count()
    
    seller_orders = []
    if current_user.is_seller:
        seller_orders = FoodOrder.query.filter_by(seller_id=current_user.id).order_by(FoodOrder.created_at.desc()).all()
    
    return render_template('profile.html', form=form, orders=orders, subscriptions=subscriptions,
                           posts=posts, posts_count=posts_count,
                           followers_count=followers_count, following_count=following_count,
                           seller_orders=seller_orders)

# ---------- Cart routes ----------
@app.route('/cart')
def cart():
    if current_user.is_authenticated:
        cart = current_user.cart
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        subtotal = sum(item.price * item.quantity for item in cart_items)
    else:
        cart_items = []
        subtotal = 0
        if 'cart' in session:
            for item in session['cart']:
                tiffin = TiffinService.query.get(item['tiffin_id'])
                if tiffin:
                    cart_items.append({'id': item['tiffin_id'], 'name': tiffin.name,
                                       'price': tiffin.price, 'quantity': item['quantity'],
                                       'image_url': tiffin.image_url})
                    subtotal += tiffin.price * item['quantity']
    delivery_charge = 0 if subtotal >= 500 else 40
    total = subtotal + delivery_charge
    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal,
                           delivery_charge=delivery_charge, total=total)

@app.route('/cart/add/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    # For now, only allow adding regular tiffin services (not seller posts)
    tiffin = TiffinService.query.get(item_id)
    if not tiffin:
        return jsonify({'success': False, 'message': 'This item is not available for ordering yet.'}), 400
    
    quantity = int(request.form.get('quantity', 1))
    if current_user.is_authenticated:
        cart = current_user.cart
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        cart_item = CartItem.query.filter_by(cart_id=cart.id, tiffin_id=item_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, tiffin_id=item_id, quantity=quantity, price=tiffin.price)
            db.session.add(cart_item)
        db.session.commit()
    else:
        if 'cart' not in session:
            session['cart'] = []
        found = False
        for item in session['cart']:
            if item['tiffin_id'] == item_id:
                item['quantity'] += quantity
                found = True
                break
        if not found:
            session['cart'].append({'tiffin_id': item_id, 'quantity': quantity, 'price': float(tiffin.price)})
        session.modified = True
    count = get_cart_count()
    return jsonify({'success': True, 'count': count, 'message': f'{tiffin.name} added to cart!'})

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    quantity = int(request.form.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
    else:
        db.session.delete(cart_item)
    db.session.commit()
    cart_total = sum(item.price * item.quantity for item in cart_item.cart.items)
    return jsonify({'success': True, 'message': 'Cart updated!', 'cart_total': cart_total,
                    'count': get_cart_count()})

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item removed from cart!', 'count': get_cart_count()})

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    if current_user.is_authenticated:
        cart = current_user.cart
        if cart:
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
    else:
        if 'cart' in session:
            session.pop('cart')
    return jsonify({'success': True, 'message': 'Cart cleared!'})

@app.route('/cart/count')
def cart_count():
    return jsonify({'count': get_cart_count()})

# ---------- Checkout & Orders ----------
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = current_user.cart
    if not cart or not cart.items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))
    form = CheckoutForm()
    if form.validate_on_submit():
        total_amount = sum(item.price * item.quantity for item in cart.items)
        order = Order(
            order_number=f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}',
            user_id=current_user.id, total_amount=total_amount,
            delivery_address=form.delivery_address.data,
            delivery_instructions=form.delivery_instructions.data,
            payment_method=form.payment_method.data, status='pending'
        )
        db.session.add(order)
        db.session.flush()
        for cart_item in cart.items:
            order_item = OrderItem(order_id=order.id, tiffin_id=cart_item.tiffin_id,
                                   quantity=cart_item.quantity, price=cart_item.price,
                                   subtotal=cart_item.price * cart_item.quantity)
            db.session.add(order_item)
        payment = Payment(order_id=order.id, amount=total_amount,
                          payment_method=form.payment_method.data, status='pending')
        db.session.add(payment)
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        flash(f'Order placed! Order number: {order.order_number}', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    if request.method == 'GET':
        form.delivery_address.data = current_user.address
    subtotal = sum(item.price * item.quantity for item in cart.items)
    delivery_charge = 0 if subtotal >= 500 else 40
    total = subtotal + delivery_charge
    return render_template('checkout.html', form=form, cart_items=cart.items,
                           subtotal=subtotal, delivery_charge=delivery_charge, total=total)

@app.route('/order/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('index'))
    return render_template('order_confirmation.html', order=order)

@app.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'newest')
    query = Order.query.filter_by(user_id=current_user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if sort_by == 'newest':
        query = query.order_by(Order.created_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Order.created_at.asc())
    elif sort_by == 'highest':
        query = query.order_by(Order.total_amount.desc())
    elif sort_by == 'lowest':
        query = query.order_by(Order.total_amount.asc())
    orders = query.paginate(page=page, per_page=10, error_out=False)
    seller_orders = []
    if current_user.is_seller:
        seller_orders = FoodOrder.query.filter_by(seller_id=current_user.id).order_by(FoodOrder.created_at.desc()).all()
    return render_template('orders.html', orders=orders, seller_orders=seller_orders)

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('index'))
    return render_template('order_detail.html', order=order)

@app.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('orders'))
    if order.status not in ['pending', 'confirmed']:
        flash('This order cannot be cancelled at this stage.', 'warning')
        return redirect(url_for('order_detail', order_id=order.id))
    order.status = 'cancelled'
    db.session.commit()
    flash(f'Order #{order.order_number} has been cancelled successfully.', 'success')
    return redirect(url_for('orders'))

@app.route('/cancel-order/<int:order_id>')
@login_required
def cancel_order_page(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('orders'))
    return render_template('cancel_order.html', order=order)

# ---------- Subscriptions ----------
@app.route('/subscriptions')
@login_required
def subscriptions():
    subs = Subscription.query.filter_by(user_id=current_user.id).order_by(Subscription.created_at.desc()).all()
    return render_template('subscriptions.html', subscriptions=subs)

@app.route('/subscription/create', methods=['POST'])
@login_required
def create_subscription():
    tiffin_id = request.form.get('tiffin_id', type=int)
    days_per_week = request.form.get('days_per_week', type=int)
    duration_weeks = request.form.get('duration_weeks', type=int)
    delivery_time = request.form.get('delivery_time')
    start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
    tiffin = TiffinService.query.get_or_404(tiffin_id)
    total_meals = days_per_week * duration_weeks
    discounted_price = tiffin.price * total_meals * 0.9
    subscription = Subscription(
        user_id=current_user.id, tiffin_id=tiffin_id,
        days_per_week=days_per_week, duration_weeks=duration_weeks,
        total_meals=total_meals, price=discounted_price,
        delivery_time=delivery_time, start_date=start_date,
        end_date=start_date + timedelta(weeks=duration_weeks)
    )
    db.session.add(subscription)
    db.session.commit()
    flash('Subscription created!', 'success')
    return redirect(url_for('subscriptions'))

@app.route('/subscription/<int:sub_id>/cancel', methods=['POST'])
@login_required
def cancel_subscription(sub_id):
    sub = Subscription.query.get_or_404(sub_id)
    if sub.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    sub.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Subscription cancelled'})

# ---------- API endpoints ----------
@app.route('/api/user/stats')
@login_required
def get_user_stats():
    posts_count = FoodPost.query.filter_by(user_id=current_user.id).count()
    followers_count = Follower.query.filter_by(followed_id=current_user.id).count()
    following_count = Follower.query.filter_by(follower_id=current_user.id).count()
    return jsonify({'posts': posts_count, 'followers': followers_count, 'following': following_count})

@app.route('/api/seller/request', methods=['POST'])
@login_required
def request_seller_approval():
    if current_user.is_seller:
        return jsonify({'success': False, 'message': 'You are already a verified seller.'})
    if current_user.seller_request == 'pending':
        return jsonify({'success': False, 'message': 'Your request is already pending admin approval.'})
    current_user.seller_request = 'pending'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Seller request sent to admin. You will be notified once approved.'})

@app.route('/api/posts/create', methods=['POST'])
@login_required
def create_post():
    try:
        caption = request.form.get('caption', '')
        price = request.form.get('price', type=float)
        quantity = request.form.get('quantity', type=int, default=0)
        location = request.form.get('location', current_user.address or '')
        post_type = request.form.get('post_type', 'photo')
        availability = request.form.get('availability', 'available')
        
        if not current_user.is_seller:
            price = None
            quantity = 0
            is_available = False
            availability = 'share'
        else:
            is_available = (availability == 'available')
        
        if 'media' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        file = request.files['media']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        allowed = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
        if ext not in allowed:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = os.path.join(app.root_path, 'static/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))
        media_url = url_for('static', filename=f'uploads/{filename}')
        media_type = 'video' if ext in {'mp4', 'mov', 'avi'} else 'image'
        
        post = FoodPost(
            user_id=current_user.id, media_type=media_type, media_url=media_url,
            caption=caption, price=price, quantity_available=quantity,
            location=location, post_type=post_type,
            availability_status=availability, is_available=is_available
        )
        db.session.add(post)
        current_user.posts_count = (current_user.posts_count or 0) + 1
        db.session.commit()
        
        if current_user.is_seller:
            msg = 'Dish uploaded and available for sale!'
        else:
            msg = 'Post shared! (To sell dishes, please apply for seller approval.)'
        return jsonify({'success': True, 'message': msg, 'post': {'id': post.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/upload/avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Empty filename'}), 400
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in {'png', 'jpg', 'jpeg', 'gif'}:
        return jsonify({'success': False, 'message': 'Invalid image format'}), 400
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(app.root_path, 'static/uploads/avatars')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    avatar_url = url_for('static', filename=f'uploads/avatars/{filename}')
    current_user.avatar_url = avatar_url
    db.session.commit()
    return jsonify({'success': True, 'avatar_url': avatar_url})

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = FoodPost.query.get_or_404(post_id)
    existing_like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        new_like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        liked = True
        if post.user_id != current_user.id:
            db.session.add(Notification(user_id=post.user_id, type='like',
                                        message=f'{current_user.username} liked your post',
                                        related_id=post_id))
    db.session.commit()
    likes_count = PostLike.query.filter_by(post_id=post_id).count()
    return jsonify({'success': True, 'liked': liked, 'likes_count': likes_count})

@app.route('/api/posts/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_on_post(post_id):
    data = request.get_json()
    comment_text = data.get('comment', '').strip()
    if not comment_text:
        return jsonify({'success': False, 'message': 'Comment empty'}), 400
    post = FoodPost.query.get_or_404(post_id)
    comment = Comment(content=comment_text, user_id=current_user.id, post_id=post_id)
    db.session.add(comment)
    if post.user_id != current_user.id:
        db.session.add(Notification(user_id=post.user_id, type='comment',
                                    message=f'{current_user.username} commented on your post',
                                    related_id=post_id))
    db.session.commit()
    comments_count = Comment.query.filter_by(post_id=post_id).count()
    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'username': current_user.username,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        },
        'comments_count': comments_count
    })

@app.route('/api/seller/orders/<int:order_id>')
@login_required
def get_seller_order(order_id):
    order = FoodOrder.query.get_or_404(order_id)
    if order.seller_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({
        'id': order.id,
        'order_number': order.order_number,
        'customer': order.customer.username,
        'items': f"{order.quantity} x {order.post.caption if order.post else 'Food item'}",
        'total_amount': f"{order.total_amount:.2f}",
        'delivery_address': order.delivery_address,
        'payment_method': order.payment_method,
        'status': order.status,
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M')
    })

@app.route('/api/seller/orders/<int:order_id>/update', methods=['POST'])
@login_required
def update_seller_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status')
    valid = ['confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled']
    if new_status not in valid:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    order = FoodOrder.query.get_or_404(order_id)
    if order.seller_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    order.status = new_status
    db.session.add(Notification(user_id=order.customer_id, type='order_update',
                                message=f'Your order #{order.order_number} is now {new_status}',
                                related_id=order.id))
    db.session.commit()
    return jsonify({'success': True, 'message': f'Order status updated to {new_status}'})

@app.route('/order/<string:order_number>/json')
@login_required
def get_order_json(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.user_id != current_user.id and not current_user.is_seller:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({
        'order_number': order.order_number,
        'created_at': order.created_at.strftime('%d %b %Y, %I:%M %p'),
        'total_amount': f"{order.total_amount:.0f}",
        'delivery_address': order.delivery_address,
        'delivery_instructions': order.delivery_instructions,
        'payment_method': order.payment_method,
        'payment_status': order.payment.status if order.payment else 'pending',
        'status': order.status,
        'items': [{'name': item.tiffin.name, 'quantity': item.quantity, 'price': f"{item.price:.0f}"} for item in order.items]
    })

# ---------- Error handlers ----------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ---------- ADMIN PANEL ----------
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_sellers = User.query.filter_by(is_seller=True).count()
    pending_sellers = User.query.filter_by(seller_request='pending').count()
    total_tiffins = TiffinService.query.count()
    total_orders = Order.query.count()
    total_food_orders = FoodOrder.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    total_food_revenue = db.session.query(db.func.sum(FoodOrder.total_amount)).scalar() or 0
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    recent_food_orders = FoodOrder.query.order_by(FoodOrder.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_sellers=total_sellers,
                          pending_sellers=pending_sellers,
                          total_tiffins=total_tiffins,
                          total_orders=total_orders,
                          total_food_orders=total_food_orders,
                          total_revenue=total_revenue + total_food_revenue,
                          recent_orders=recent_orders,
                          recent_food_orders=recent_food_orders)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def admin_toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own admin status.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Admin status for {user.username} updated.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/toggle-seller', methods=['POST'])
@login_required
@admin_required
def admin_toggle_seller(user_id):
    user = User.query.get_or_404(user_id)
    user.is_seller = not user.is_seller
    if user.is_seller:
        user.seller_request = 'approved'
    else:
        user.seller_request = None
    db.session.commit()
    flash(f'Seller status for {user.username} updated.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} deleted.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/seller-requests')
@login_required
@admin_required
def admin_seller_requests():
    pending = User.query.filter_by(seller_request='pending').all()
    return render_template('admin/seller_requests.html', pending=pending)

@app.route('/admin/seller-request/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def admin_approve_seller(user_id):
    user = User.query.get_or_404(user_id)
    user.seller_request = 'approved'
    user.is_seller = True
    db.session.commit()
    flash(f'{user.username} is now a verified seller.', 'success')
    return redirect(url_for('admin_seller_requests'))

@app.route('/admin/seller-request/<int:user_id>/reject', methods=['POST'])
@login_required
@admin_required
def admin_reject_seller(user_id):
    user = User.query.get_or_404(user_id)
    user.seller_request = 'rejected'
    db.session.commit()
    flash(f'{user.username}\'s seller request rejected.', 'warning')
    return redirect(url_for('admin_seller_requests'))

@app.route('/admin/tiffins')
@login_required
@admin_required
def admin_tiffins():
    tiffins = TiffinService.query.all()
    categories = Category.query.all()
    return render_template('admin/tiffins.html', tiffins=tiffins, categories=categories)

@app.route('/admin/tiffin/create', methods=['POST'])
@login_required
@admin_required
def admin_create_tiffin():
    name = request.form.get('name')
    description = request.form.get('description')
    price = float(request.form.get('price'))
    category_id = int(request.form.get('category_id'))
    image_url = request.form.get('image_url')
    is_veg = request.form.get('is_veg') == 'on'
    delivery_time = request.form.get('delivery_time')
    min_order_days = int(request.form.get('min_order_days', 1))
    address = request.form.get('address')
    phone = request.form.get('phone')
    email = request.form.get('email')
    
    tiffin = TiffinService(
        name=name, description=description, price=price, category_id=category_id,
        image_url=image_url, is_veg=is_veg, delivery_time=delivery_time,
        min_order_days=min_order_days, address=address, phone=phone, email=email,
        is_available=True
    )
    db.session.add(tiffin)
    db.session.commit()
    flash('Tiffin service created.', 'success')
    return redirect(url_for('admin_tiffins'))

@app.route('/admin/tiffin/<int:tiffin_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_tiffin(tiffin_id):
    tiffin = TiffinService.query.get_or_404(tiffin_id)
    tiffin.name = request.form.get('name')
    tiffin.description = request.form.get('description')
    tiffin.price = float(request.form.get('price'))
    tiffin.category_id = int(request.form.get('category_id'))
    tiffin.image_url = request.form.get('image_url')
    tiffin.is_veg = request.form.get('is_veg') == 'on'
    tiffin.delivery_time = request.form.get('delivery_time')
    tiffin.min_order_days = int(request.form.get('min_order_days', 1))
    tiffin.address = request.form.get('address')
    tiffin.phone = request.form.get('phone')
    tiffin.email = request.form.get('email')
    db.session.commit()
    flash('Tiffin service updated.', 'success')
    return redirect(url_for('admin_tiffins'))

@app.route('/admin/tiffin/<int:tiffin_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_tiffin(tiffin_id):
    tiffin = TiffinService.query.get_or_404(tiffin_id)
    db.session.delete(tiffin)
    db.session.commit()
    flash('Tiffin service deleted.', 'success')
    return redirect(url_for('admin_tiffins'))

@app.route('/admin/categories')
@login_required
@admin_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/category/create', methods=['POST'])
@login_required
@admin_required
def admin_create_category():
    name = request.form.get('name')
    icon = request.form.get('icon', 'fas fa-utensils')
    description = request.form.get('description')
    category = Category(name=name, icon=icon, description=description)
    db.session.add(category)
    db.session.commit()
    flash('Category created.', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/category/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    if category.tiffins:
        flash('Cannot delete category that has tiffin services. Remove them first.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted.', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    food_orders = FoodOrder.query.order_by(FoodOrder.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders, food_orders=food_orders)

@app.route('/admin/food-posts')
@login_required
@admin_required
def admin_food_posts():
    posts = FoodPost.query.order_by(FoodPost.created_at.desc()).all()
    return render_template('admin/food_posts.html', posts=posts)

@app.route('/admin/food-post/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_food_post(post_id):
    post = FoodPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Food post deleted.', 'success')
    return redirect(url_for('admin_food_posts'))

@app.route('/admin/food-post/<int:post_id>/toggle-available', methods=['POST'])
@login_required
@admin_required
def admin_toggle_food_post(post_id):
    post = FoodPost.query.get_or_404(post_id)
    post.is_available = not post.is_available
    post.availability_status = 'available' if post.is_available else 'unavailable'
    db.session.commit()
    flash('Post availability toggled.', 'success')
    return redirect(url_for('admin_food_posts'))

if __name__ == '__main__':
    app.run(debug=True)