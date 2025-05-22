from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit, join_room
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'nikhil8995'  # Change this in production

# MySQL Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nikhil89",
    database="real_estate",
    port=3306
)
cursor = db.cursor(dictionary=True)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize SocketIO
socketio = SocketIO(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_type(user_id):
    cursor.execute("SELECT * FROM Buyer WHERE User_id = %s", (user_id,))
    if cursor.fetchone():
        return 'buyer'
    cursor.execute("SELECT * FROM Seller WHERE User_id = %s", (user_id,))
    if cursor.fetchone():
        return 'seller'
    return None

def get_user_name(user_id):
    cursor.execute("SELECT First_name, Last_name FROM User WHERE User_id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return f"{user['First_name']} {user['Last_name']}"
    return "User"

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash("Please provide both email and password.", "danger")
            return render_template('login.html')
        cursor.execute("SELECT * FROM User WHERE Email = %s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['Password'], password):
            session['user_id'] = user['User_id']
            session['user_type'] = get_user_type(user['User_id'])
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        hashed_password = generate_password_hash(password)
        try:
            cursor.execute("INSERT INTO User (First_name, Last_name, Email, Password) VALUES (%s, %s, %s, %s)",
                           (first_name, last_name, email, hashed_password))
            user_id = cursor.lastrowid
            db.commit()
            if user_type == 'buyer':
                cursor.execute("INSERT INTO Buyer (User_id, Budget) VALUES (%s, %s)", (user_id, 0))
            elif user_type == 'seller':
                cursor.execute("INSERT INTO Seller (User_id, Acc_Status, Avg_prop_rating) VALUES (%s, %s, %s)", 
                               (user_id, 'Active', 0))
            db.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("Email already exists. Please use a different email.", "danger")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('homepage'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))
    user_type = session['user_type']
    if user_type == 'buyer':
        return redirect(url_for('buyer_dashboard'))
    elif user_type == 'seller':
        return redirect(url_for('seller_dashboard'))
    else:
        flash("Invalid user type.", "danger")
        return redirect(url_for('homepage'))

@app.route('/buyer_dashboard', methods=['GET'])
def buyer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'buyer':
        flash("Please log in as a buyer to access this page.", "danger")
        return redirect(url_for('login'))
    filter_status = request.args.get('filter', 'For Sale')
    if filter_status == 'All':
        cursor.execute("SELECT * FROM Property WHERE status IN ('For Sale', 'For Rent')")
    else:
        cursor.execute("SELECT * FROM Property WHERE status = %s", (filter_status,))
    properties = cursor.fetchall()
    user_name = get_user_name(session['user_id'])
    return render_template('buyer.html', properties=properties, filter_status=filter_status, user_name=user_name)

@app.route('/seller_dashboard')
def seller_dashboard():
    if 'user_id' not in session or session['user_type'] != 'seller':
        flash("Please log in as a seller to access this page.", "danger")
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM Property WHERE User_id = %s", (session['user_id'],))
    properties = cursor.fetchall()
    user_name = get_user_name(session['user_id'])
    return render_template('seller.html', properties=properties, user_name=user_name)

@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if 'user_id' not in session or session['user_type'] != 'seller':
        flash("Please log in as a seller to add a property.", "danger")
        return redirect(url_for('login'))
    if request.method == 'POST':
        prop_type = request.form['type']
        size = request.form['size']
        price = request.form['price']
        location = request.form['location']
        amenities = request.form['amenities']
        status = request.form['status']
        image_filename = None

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        cursor.execute("""
        INSERT INTO Property (type, size, price, location, amenities, status, User_id, image)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (prop_type, size, price, location, amenities, status, session['user_id'], image_filename))
        db.commit()
        flash("Property added successfully!", "success")
        return redirect(url_for('seller_dashboard'))
    user_name = get_user_name(session['user_id'])
    return render_template('add_property.html', user_name=user_name)

@app.route('/property/<int:prop_id>')
def property_detail(prop_id):
    cursor.execute("SELECT * FROM Property WHERE Prop_id = %s", (prop_id,))
    prop = cursor.fetchone()
    user_name = get_user_name(session['user_id']) if 'user_id' in session else "User"
    if not prop:
        flash("Property not found.", "danger")
        return redirect(url_for('buyer_dashboard'))
    return render_template('property_detail.html', prop=prop, user_name=user_name)

@app.route('/confirm_buy/<int:prop_id>', methods=['GET', 'POST'])
def confirm_buy(prop_id):
    if 'user_id' not in session or session['user_type'] != 'buyer':
        flash("Please log in as a buyer to buy properties.", "danger")
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM Property WHERE Prop_id = %s", (prop_id,))
    prop = cursor.fetchone()
    if not prop or prop['status'] != 'For Sale':
        flash("Property not available for sale.", "danger")
        return redirect(url_for('buyer_dashboard'))
    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO Transactions (Prop_id, User_id, Sale_Price, mode)
            VALUES (%s, %s, %s, %s)
        """, (prop_id, session['user_id'], prop['price'], 'Online'))
        db.commit()
        cursor.execute("UPDATE Property SET status = 'Sold' WHERE Prop_id = %s", (prop_id,))
        db.commit()
        flash("Payment successful! You have bought the property.", "success")
        return redirect(url_for('buyer_dashboard'))
    return render_template('confirm_buy.html', prop=prop)

@app.route('/confirm_rent/<int:prop_id>', methods=['GET', 'POST'])
def confirm_rent(prop_id):
    if 'user_id' not in session or session['user_type'] != 'buyer':
        flash("Please log in as a buyer to rent properties.", "danger")
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM Property WHERE Prop_id = %s", (prop_id,))
    prop = cursor.fetchone()
    if not prop or prop['status'] != 'For Rent':
        flash("Property not available for rent.", "danger")
        return redirect(url_for('buyer_dashboard'))
    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO Transactions (Prop_id, User_id, Sale_Price, mode)
            VALUES (%s, %s, %s, %s)
        """, (prop_id, session['user_id'], prop['price'], 'Rent'))
        db.commit()
        cursor.execute("UPDATE Property SET status = 'Rented' WHERE Prop_id = %s", (prop_id,))
        db.commit()
        flash("Payment successful! You have rented the property.", "success")
        return redirect(url_for('buyer_dashboard'))
    return render_template('confirm_rent.html', prop=prop)

# --- All Chats WhatsApp-like Interface ---
@app.route('/all_chats')
def all_chats():
    if 'user_id' not in session:
        flash("Please log in to view chats.", "danger")
        return redirect(url_for('login'))
    user_id = session['user_id']
    user_type = session['user_type']
    user_name = get_user_name(user_id)

    if user_type == 'buyer':
        cursor.execute("""
            SELECT 
                cm.property_id,
                cm.receiver_id AS other_user_id,
                u.First_name AS other_first_name,
                u.Last_name AS other_last_name,
                p.type AS property_type,
                p.location AS property_location,
                MAX(cm.timestamp) AS last_message_time,
                SUBSTRING_INDEX(GROUP_CONCAT(cm.message ORDER BY cm.timestamp DESC), ',', 1) AS last_message
            FROM ChatMessage cm
            JOIN Property p ON cm.property_id = p.Prop_id
            JOIN User u ON cm.receiver_id = u.User_id
            WHERE cm.sender_id = %s OR cm.receiver_id = %s
            GROUP BY cm.property_id, cm.receiver_id
            ORDER BY last_message_time DESC
        """, (user_id, user_id))
    else:  # seller
        cursor.execute("""
            SELECT 
                cm.property_id,
                cm.sender_id AS other_user_id,
                u.First_name AS other_first_name,
                u.Last_name AS other_last_name,
                p.type AS property_type,
                p.location AS property_location,
                MAX(cm.timestamp) AS last_message_time,
                SUBSTRING_INDEX(GROUP_CONCAT(cm.message ORDER BY cm.timestamp DESC), ',', 1) AS last_message
            FROM ChatMessage cm
            JOIN Property p ON cm.property_id = p.Prop_id
            JOIN User u ON cm.sender_id = u.User_id
            WHERE p.User_id = %s OR cm.sender_id = %s
            GROUP BY cm.property_id, cm.sender_id
            ORDER BY last_message_time DESC
        """, (user_id, user_id))
    chat_threads = cursor.fetchall()
    return render_template('all_chats.html', chat_threads=chat_threads, user_name=user_name, user_type=user_type)

# --- Real-time Chat Feature using Flask-SocketIO ---
@app.route('/chat/<int:other_user_id>/<int:property_id>')
def chat(other_user_id, property_id):
    if 'user_id' not in session:
        flash("Please log in to use chat.", "danger")
        return redirect(url_for('login'))
    user_id = session['user_id']
    cursor.execute("SELECT * FROM User WHERE User_id = %s", (other_user_id,))
    other_user = cursor.fetchone()
    return render_template('chat.html', other_user=other_user, property_id=property_id)

@app.route('/api/chat/<int:other_user_id>/<int:property_id>')
def api_get_chat(other_user_id, property_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user_id = session['user_id']
    cursor.execute("""
        SELECT * FROM ChatMessage
        WHERE ((sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s))
          AND property_id = %s
        ORDER BY timestamp ASC
    """, (user_id, other_user_id, other_user_id, user_id, property_id))
    messages = cursor.fetchall()
    for msg in messages:
        msg['timestamp'] = msg['timestamp'].strftime('%Y-%m-%d %H:%M')
    return jsonify(messages)

@app.route('/api/chat/send', methods=['POST'])
def api_send_chat():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    data = request.get_json()
    sender_id = session['user_id']
    other_user_id = data.get('other_user_id')
    property_id = data.get('property_id')
    message = data.get('message')
    if not (sender_id and other_user_id and property_id and message):
        return jsonify({'success': False, 'error': 'Missing data'}), 400
    try:
        cursor.execute("""
            INSERT INTO ChatMessage (sender_id, receiver_id, property_id, message)
            VALUES (%s, %s, %s, %s)
        """, (sender_id, other_user_id, property_id, message))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@socketio.on('join_room')
def handle_join(data):
    join_room(data['room'])

@socketio.on('send_message')
def handle_send_message(data):
    cursor.execute("""
        INSERT INTO ChatMessage (sender_id, receiver_id, property_id, message)
        VALUES (%s, %s, %s, %s)
    """, (data['sender_id'], data['receiver_id'], data['property_id'], data['message']))
    db.commit()
    emit('receive_message', data, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
