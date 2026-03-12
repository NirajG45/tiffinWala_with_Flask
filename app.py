from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from models import db, User, TiffinService, Category, Order, OrderItem, Cart, CartItem, Subscription, Review, Payment
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
    """Custom unauthorized handler to ensure correct login URL"""
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login', next=request.path))

# Add context processor for templates
@app.context_processor
def utility_processor():
    return dict(now=datetime.now)

# Create tables
with app.app_context():
    db.create_all()
    
    # Create default categories if they don't exist
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
        
        # Create sample tiffin services
        sample_tiffins = [
            TiffinService(
                name='Maa Ki Rasoi',
                description='Traditional home-style vegetarian meals with love and care passed down through generations.',
                price=180.00,
                category_id=1,
                image_url='https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&h=300&fit=crop',
                rating=4.8,
                total_reviews=245,
                delivery_time='7:00 AM - 9:00 AM',
                min_order_days=7,
                is_veg=True,
                is_available=True,
                address='Sitamarhi, Bihar',
                phone='+919876543210',
                email='maakirasoi@example.com',
                opening_time='07:00',
                closing_time='21:00',
                sample_menu=[
                    {"name": "Dal Makhani", "price": 120},
                    {"name": "Paneer Butter Masala", "price": 150},
                    {"name": "Jeera Rice", "price": 80},
                    {"name": "Roti", "price": 10}
                ]
            ),
            TiffinService(
                name='Healthy Bites',
                description='Calorie-counted diet meals with nutrition tracking for weight management and healthy living.',
                price=250.00,
                category_id=4,
                image_url='https://images.unsplash.com/photo-1490818387583-1baba5e638af?w=400&h=300&fit=crop',
                rating=4.7,
                total_reviews=189,
                delivery_time='8:00 AM - 10:00 AM',
                min_order_days=5,
                is_veg=True,
                is_available=True,
                address='Patna, Bihar',
                phone='+919876543211',
                email='healthybites@example.com',
                opening_time='08:00',
                closing_time='22:00',
                sample_menu=[
                    {"name": "Grilled Chicken Salad", "price": 180},
                    {"name": "Quinoa Bowl", "price": 160},
                    {"name": "Steamed Vegetables", "price": 120},
                    {"name": "Protein Shake", "price": 150}
                ]
            ),
            TiffinService(
                name='Royal Non-Veg',
                description='Premium non-vegetarian delicacies with authentic recipes using fresh ingredients.',
                price=300.00,
                category_id=2,
                image_url='https://images.unsplash.com/photo-1600891964092-4316c288032e?w=400&h=300&fit=crop',
                rating=4.9,
                total_reviews=312,
                delivery_time='7:30 AM - 9:30 AM',
                min_order_days=7,
                is_veg=False,
                is_available=True,
                address='Muzaffarpur, Bihar',
                phone='+919876543212',
                email='royalnonveg@example.com',
                opening_time='07:30',
                closing_time='21:30',
                sample_menu=[
                    {"name": "Chicken Biryani", "price": 220},
                    {"name": "Butter Chicken", "price": 250},
                    {"name": "Tandoori Roti", "price": 15},
                    {"name": "Raita", "price": 40}
                ]
            )
        ]
        db.session.add_all(sample_tiffins)
        db.session.commit()

# Redirect routes for .html URLs (to handle any stray requests)
@app.route('/login.html')
def login_html_redirect():
    """Redirect old login.html URLs to the proper login route"""
    next_url = request.args.get('redirect') or request.args.get('next')
    if next_url:
        return redirect(url_for('login', next=next_url))
    return redirect(url_for('login'))

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

# Routes
@app.route('/')
def index():
    """Home page"""
    featured_tiffins = TiffinService.query.filter_by(is_available=True).limit(6).all()
    categories = Category.query.all()
    return render_template('index.html', tiffins=featured_tiffins, categories=categories)

@app.route('/tiffins')
def tiffins():
    """Tiffin services listing page with search and filters"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search_query = request.args.get('search', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    food_type = request.args.get('food_type', '')
    sort_by = request.args.get('sort_by', 'rating_desc')
    
    query = TiffinService.query.filter_by(is_available=True)
    
    # Apply filters
    if category:
        query = query.join(Category).filter(Category.name.ilike(f'%{category}%'))
    if search_query:
        query = query.filter(
            db.or_(
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
    
    # Apply sorting
    if sort_by == 'price_asc':
        query = query.order_by(TiffinService.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(TiffinService.price.desc())
    elif sort_by == 'rating_desc':
        query = query.order_by(TiffinService.rating.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(TiffinService.name.asc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=9, error_out=False)
    tiffins = pagination.items
    
    categories = Category.query.all()
    form = TiffinSearchForm()
    
    return render_template(
        'tiffins.html',
        tiffins=tiffins,
        pagination=pagination,
        categories=categories,
        form=form,
        current_filters={
            'category': category,
            'search': search_query,
            'min_price': min_price,
            'max_price': max_price,
            'food_type': food_type,
            'sort_by': sort_by
        }
    )

@app.route('/tiffin/<int:tiffin_id>')
def tiffin_detail(tiffin_id):
    """Tiffin service detail page"""
    tiffin = TiffinService.query.get_or_404(tiffin_id)
    reviews = Review.query.filter_by(tiffin_id=tiffin_id).order_by(Review.created_at.desc()).limit(10).all()
    
    # Get similar tiffins (same category)
    similar_tiffins = TiffinService.query.filter(
        TiffinService.category_id == tiffin.category_id,
        TiffinService.id != tiffin_id,
        TiffinService.is_available == True
    ).limit(3).all()
    
    review_form = ReviewForm()
    
    return render_template(
        'tiffin_detail.html',
        tiffin=tiffin,
        reviews=reviews,
        similar_tiffins=similar_tiffins,
        review_form=review_form,
        now=datetime.now
    )

@app.route('/tiffin/<int:tiffin_id>/review', methods=['POST'])
@login_required
def add_review(tiffin_id):
    """Add a review for a tiffin service"""
    tiffin = TiffinService.query.get_or_404(tiffin_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Check if user already reviewed this tiffin
        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            tiffin_id=tiffin_id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this tiffin service.', 'warning')
            return redirect(url_for('tiffin_detail', tiffin_id=tiffin_id))
        
        review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=current_user.id,
            tiffin_id=tiffin_id
        )
        db.session.add(review)
        
        # Update tiffin rating
        reviews = Review.query.filter_by(tiffin_id=tiffin_id).all()
        total_rating = sum(r.rating for r in reviews) + review.rating
        tiffin.rating = total_rating / (len(reviews) + 1)
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
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user exists
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        
        # Create new user
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Create cart for new user
        cart = Cart(user_id=new_user.id)
        db.session.add(cart)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            # Transfer session cart to user cart
            if 'cart' in session:
                cart = user.cart
                if not cart:
                    cart = Cart(user_id=user.id)
                    db.session.add(cart)
                    db.session.commit()
                
                for item in session['cart']:
                    # Check if item already in cart
                    existing_item = CartItem.query.filter_by(
                        cart_id=cart.id,
                        tiffin_id=item['tiffin_id']
                    ).first()
                    
                    if existing_item:
                        existing_item.quantity += item['quantity']
                    else:
                        cart_item = CartItem(
                            cart_id=cart.id,
                            tiffin_id=item['tiffin_id'],
                            quantity=item['quantity'],
                            price=item['price']
                        )
                        db.session.add(cart_item)
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
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
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
    
    # Get user's orders
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    
    # Get user's subscriptions
    subscriptions = Subscription.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    return render_template(
        'profile.html',
        form=form,
        orders=orders,
        subscriptions=subscriptions
    )

@app.route('/cart')
def cart():
    """Shopping cart page"""
    if current_user.is_authenticated:
        # Get user's cart from database
        cart = current_user.cart
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        subtotal = sum(item.price * item.quantity for item in cart_items)
    else:
        # Get cart from session
        cart_items = []
        subtotal = 0
        if 'cart' in session:
            for item in session['cart']:
                tiffin = TiffinService.query.get(item['tiffin_id'])
                if tiffin:
                    cart_items.append({
                        'id': item['tiffin_id'],
                        'name': tiffin.name,
                        'price': tiffin.price,
                        'quantity': item['quantity'],
                        'image_url': tiffin.image_url
                    })
                    subtotal += tiffin.price * item['quantity']
    
    delivery_charge = 0 if subtotal >= 500 else 40
    total = subtotal + delivery_charge
    
    return render_template(
        'cart.html', 
        cart_items=cart_items, 
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        total=total
    )

@app.route('/cart/add/<int:tiffin_id>', methods=['POST'])
def add_to_cart(tiffin_id):
    """Add item to cart"""
    tiffin = TiffinService.query.get_or_404(tiffin_id)
    quantity = int(request.form.get('quantity', 1))
    
    if current_user.is_authenticated:
        # Add to database cart
        cart = current_user.cart
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(
            cart_id=cart.id,
            tiffin_id=tiffin_id
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                tiffin_id=tiffin_id,
                quantity=quantity,
                price=tiffin.price
            )
            db.session.add(cart_item)
        
        db.session.commit()
    else:
        # Add to session cart
        if 'cart' not in session:
            session['cart'] = []
        
        # Check if item already in session cart
        found = False
        for item in session['cart']:
            if item['tiffin_id'] == tiffin_id:
                item['quantity'] += quantity
                found = True
                break
        
        if not found:
            session['cart'].append({
                'tiffin_id': tiffin_id,
                'quantity': quantity,
                'price': float(tiffin.price)
            })
        
        session.modified = True
    
    # Get updated cart count
    count = get_cart_count()
    
    return jsonify({'success': True, 'count': count, 'message': f'{tiffin.name} added to cart!'})

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    """Update cart item quantity"""
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Ensure item belongs to current user
    if cart_item.cart.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    quantity = int(request.form.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
    else:
        db.session.delete(cart_item)
    
    db.session.commit()
    
    # Get updated cart total
    cart_total = sum(item.price * item.quantity for item in cart_item.cart.items)
    
    return jsonify({
        'success': True,
        'message': 'Cart updated!',
        'cart_total': cart_total,
        'count': get_cart_count()
    })

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Ensure item belongs to current user
    if cart_item.cart.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Item removed from cart!',
        'count': get_cart_count()
    })

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Clear entire cart"""
    if current_user.is_authenticated:
        # Clear database cart
        cart = current_user.cart
        if cart:
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
    else:
        # Clear session cart
        if 'cart' in session:
            session.pop('cart')
    
    return jsonify({'success': True, 'message': 'Cart cleared!'})

@app.route('/cart/count')
def cart_count():
    """Get cart item count"""
    count = get_cart_count()
    return jsonify({'count': count})

def get_cart_count():
    """Helper function to get cart count"""
    if current_user.is_authenticated:
        cart = current_user.cart
        if cart:
            return db.session.query(db.func.sum(CartItem.quantity)).filter_by(cart_id=cart.id).scalar() or 0
        return 0
    else:
        if 'cart' in session:
            return sum(item['quantity'] for item in session['cart'])
        return 0

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    cart = current_user.cart
    if not cart or not cart.items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))
    
    form = CheckoutForm()
    
    if form.validate_on_submit():
        # Create order
        total_amount = sum(item.price * item.quantity for item in cart.items)
        
        order = Order(
            order_number=f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}',
            user_id=current_user.id,
            total_amount=total_amount,
            delivery_address=form.delivery_address.data,
            delivery_instructions=form.delivery_instructions.data,
            payment_method=form.payment_method.data,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()
        
        # Add order items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                tiffin_id=cart_item.tiffin_id,
                quantity=cart_item.quantity,
                price=cart_item.price,
                subtotal=cart_item.price * cart_item.quantity
            )
            db.session.add(order_item)
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            amount=total_amount,
            payment_method=form.payment_method.data,
            status='pending'
        )
        db.session.add(payment)
        
        # Clear cart
        CartItem.query.filter_by(cart_id=cart.id).delete()
        
        db.session.commit()
        
        flash(f'Order placed successfully! Order number: {order.order_number}', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    # Pre-fill form with user data
    if request.method == 'GET':
        form.delivery_address.data = current_user.address
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in cart.items)
    delivery_charge = 0 if subtotal >= 500 else 40
    total = subtotal + delivery_charge
    
    return render_template(
        'checkout.html',
        form=form,
        cart_items=cart.items,
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        total=total
    )

@app.route('/order/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """Order confirmation page"""
    order = Order.query.get_or_404(order_id)
    
    # Ensure order belongs to current user
    if order.user_id != current_user.id:
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('order_confirmation.html', order=order)

@app.route('/orders')
@login_required
def orders():
    """User orders page"""
    from models import FoodOrder
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'newest')
    
    # Customer orders
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
    
    # Seller orders (from social posts)
    seller_orders = []
    if current_user.is_seller:
        seller_orders = FoodOrder.query.filter_by(seller_id=current_user.id).order_by(FoodOrder.created_at.desc()).all()
    
    return render_template(
        'orders.html', 
        orders=orders,
        seller_orders=seller_orders
    )

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """Order detail page"""
    order = Order.query.get_or_404(order_id)
    
    # Ensure order belongs to current user
    if order.user_id != current_user.id:
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('order_detail.html', order=order)

@app.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel an order"""
    order = Order.query.get_or_404(order_id)
    
    # Ensure order belongs to current user and can be cancelled
    if order.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if order.status not in ['pending', 'confirmed']:
        return jsonify({'success': False, 'message': 'Order cannot be cancelled at this stage'}), 400
    
    order.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Order cancelled successfully!'})

@app.route('/subscriptions')
@login_required
def subscriptions():
    """User subscriptions page"""
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).order_by(
        Subscription.created_at.desc()
    ).all()
    
    return render_template('subscriptions.html', subscriptions=subscriptions)

@app.route('/subscription/create', methods=['POST'])
@login_required
def create_subscription():
    """Create a new subscription"""
    tiffin_id = request.form.get('tiffin_id', type=int)
    days_per_week = request.form.get('days_per_week', type=int)
    duration_weeks = request.form.get('duration_weeks', type=int)
    delivery_time = request.form.get('delivery_time')
    start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
    
    tiffin = TiffinService.query.get_or_404(tiffin_id)
    
    # Calculate subscription price (10% discount)
    total_meals = days_per_week * duration_weeks
    original_price = tiffin.price * total_meals
    discounted_price = original_price * 0.9
    
    subscription = Subscription(
        user_id=current_user.id,
        tiffin_id=tiffin_id,
        days_per_week=days_per_week,
        duration_weeks=duration_weeks,
        total_meals=total_meals,
        price=discounted_price,
        delivery_time=delivery_time,
        start_date=start_date,
        end_date=start_date + timedelta(weeks=duration_weeks)
    )
    
    db.session.add(subscription)
    db.session.commit()
    
    flash('Subscription created successfully!', 'success')
    return redirect(url_for('subscriptions'))

@app.route('/subscription/<int:sub_id>/cancel', methods=['POST'])
@login_required
def cancel_subscription(sub_id):
    """Cancel a subscription"""
    subscription = Subscription.query.get_or_404(sub_id)
    
    # Ensure subscription belongs to current user
    if subscription.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    subscription.is_active = False
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Subscription cancelled successfully!'})

@app.route('/api/tiffins/search')
def api_search_tiffins():
    """API endpoint for live search"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    tiffins = TiffinService.query.filter(
        TiffinService.name.ilike(f'%{query}%'),
        TiffinService.is_available == True
    ).limit(5).all()
    
    results = [{
        'id': t.id,
        'name': t.name,
        'price': t.price,
        'image': t.image_url,
        'rating': t.rating,
        'category': t.category.name if t.category else ''
    } for t in tiffins]
    
    return jsonify(results)

@app.route('/api/tiffins/filter')
def api_filter_tiffins():
    """API endpoint for filtering tiffins"""
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    veg_only = request.args.get('veg_only', type=bool)
    
    query = TiffinService.query.filter_by(is_available=True)
    
    if category:
        query = query.join(Category).filter(Category.name == category)
    if min_price:
        query = query.filter(TiffinService.price >= min_price)
    if max_price:
        query = query.filter(TiffinService.price <= max_price)
    if veg_only:
        query = query.filter_by(is_veg=True)
    
    tiffins = query.limit(10).all()
    
    results = [{
        'id': t.id,
        'name': t.name,
        'price': t.price,
        'image': t.image_url,
        'rating': t.rating,
        'category': t.category.name if t.category else ''
    } for t in tiffins]
    
    return jsonify(results)



# Add these routes to your app.py

@app.route('/api/user/stats')
@login_required
def get_user_stats():
    """Get user statistics for profile"""
    from models import FoodPost, Follower
    
    posts_count = FoodPost.query.filter_by(user_id=current_user.id).count()
    followers_count = Follower.query.filter_by(followed_id=current_user.id).count()
    following_count = Follower.query.filter_by(follower_id=current_user.id).count()
    
    return jsonify({
        'posts': posts_count,
        'followers': followers_count,
        'following': following_count
    })

@app.route('/api/posts/create', methods=['POST'])
@login_required
def create_post():
    """Create a new food post"""
    from models import FoodPost
    from werkzeug.utils import secure_filename
    import os
    import uuid
    
    try:
        # Get form data
        caption = request.form.get('caption', '')
        price = request.form.get('price', type=float)
        quantity = request.form.get('quantity', type=int, default=0)
        location = request.form.get('location', current_user.address or '')
        post_type = request.form.get('post_type', 'photo')
        availability = request.form.get('availability', 'available')
        is_available = availability == 'available'
        
        # Handle file upload
        if 'media' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['media']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Save file
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(app.root_path, 'static/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        media_url = url_for('static', filename=f'uploads/{filename}')
        
        # Determine media type
        media_type = 'video' if ext in {'mp4', 'mov', 'avi'} else 'image'
        
        # Create post
        post = FoodPost(
            user_id=current_user.id,
            media_type=media_type,
            media_url=media_url,
            caption=caption,
            price=price,
            quantity_available=quantity,
            location=location,
            post_type=post_type,
            availability_status=availability,
            is_available=is_available
        )
        
        db.session.add(post)
        
        # Update user's post count
        current_user.posts_count = (current_user.posts_count or 0) + 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post created successfully!',
            'post': {
                'id': post.id,
                'media_url': post.media_url,
                'media_type': post.media_type,
                'caption': post.caption
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/order/<string:order_number>/json')
@login_required
def get_order_json(order_number):
    """Get order details as JSON"""
    from models import Order
    
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    
    # Check if user has permission
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
        'items': [{
            'name': item.tiffin.name,
            'quantity': item.quantity,
            'price': f"{item.price:.0f}"
        } for item in order.items]
    })
    
    

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)