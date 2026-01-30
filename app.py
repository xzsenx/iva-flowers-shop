from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  price INTEGER NOT NULL,
                  image_url TEXT,
                  category TEXT,
                  colors TEXT,
                  characteristics TEXT,
                  delivery_type TEXT,
                  description TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_name TEXT,
                  customer_phone TEXT,
                  customer_address TEXT,
                  items TEXT,
                  total_price INTEGER,
                  status TEXT DEFAULT 'new',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# API Routes

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return render_template_string(ADMIN_TEMPLATE)

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    
    # Get filter parameters
    category = request.args.get('category')
    color = request.args.get('color')
    characteristic = request.args.get('characteristic')
    
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category and category != 'Все':
        query += " AND category = ?"
        params.append(category)
    
    if color:
        query += " AND colors LIKE ?"
        params.append(f'%{color}%')
    
    if characteristic:
        query += " AND characteristics LIKE ?"
        params.append(f'%{characteristic}%')
    
    c.execute(query, params)
    products = []
    for row in c.fetchall():
        products.append({
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'image_url': row[3],
            'category': row[4],
            'colors': row[5],
            'characteristics': row[6],
            'delivery_type': row[7],
            'description': row[8]
        })
    
    conn.close()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO products 
                 (name, price, image_url, category, colors, characteristics, delivery_type, description)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['name'], data['price'], data['image_url'], data['category'],
               data.get('colors', ''), data.get('characteristics', ''),
               data.get('delivery_type', 'today'), data.get('description', '')))
    
    conn.commit()
    product_id = c.lastrowid
    conn.close()
    
    return jsonify({'id': product_id, 'message': 'Product added successfully'})

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    
    c.execute('''UPDATE products 
                 SET name=?, price=?, image_url=?, category=?, colors=?, 
                     characteristics=?, delivery_type=?, description=?
                 WHERE id=?''',
              (data['name'], data['price'], data['image_url'], data['category'],
               data.get('colors', ''), data.get('characteristics', ''),
               data.get('delivery_type', 'today'), data.get('description', ''),
               product_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id=?', (product_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO orders 
                 (customer_name, customer_phone, customer_address, items, total_price)
                 VALUES (?, ?, ?, ?, ?)''',
              (data['customer_name'], data['customer_phone'], data['customer_address'],
               json.dumps(data['items']), data['total_price']))
    
    conn.commit()
    order_id = c.lastrowid
    conn.close()
    
    return jsonify({'id': order_id, 'message': 'Order created successfully'})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = sqlite3.connect('flowers.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders ORDER BY created_at DESC')
    
    orders = []
    for row in c.fetchall():
        orders.append({
            'id': row[0],
            'customer_name': row[1],
            'customer_phone': row[2],
            'customer_address': row[3],
            'items': json.loads(row[4]),
            'total_price': row[5],
            'status': row[6],
            'created_at': row[7]
        })
    
    conn.close()
    return jsonify(orders)

# Admin template
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Админ панель - Ива</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            color: #4a5c5e;
            margin-bottom: 30px;
            font-size: 32px;
        }
        .section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h2 {
            color: #4a5c5e;
            margin-bottom: 20px;
            font-size: 24px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        button {
            background: #c4a57b;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #b39569;
        }
        .products-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .product-card {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }
        .product-card img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .product-card h3 {
            font-size: 16px;
            margin-bottom: 8px;
            color: #333;
        }
        .product-card .price {
            color: #c4a57b;
            font-weight: 700;
            font-size: 18px;
            margin-bottom: 10px;
        }
        .product-actions {
            display: flex;
            gap: 10px;
        }
        .product-actions button {
            flex: 1;
            padding: 8px;
            font-size: 14px;
        }
        .delete-btn {
            background: #d9534f;
        }
        .delete-btn:hover {
            background: #c9302c;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        .orders-list {
            margin-top: 20px;
        }
        .order-card {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 2px solid #e0e0e0;
        }
        .order-card h3 {
            color: #4a5c5e;
            margin-bottom: 10px;
        }
        .order-info {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 10px;
        }
        .order-items {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Админ панель - Ива</h1>
        
        <div id="success-message" class="success"></div>
        
        <!-- Add Product Form -->
        <div class="section">
            <h2>Добавить товар</h2>
            <form id="add-product-form">
                <div class="form-group">
                    <label>Название</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Цена (₽)</label>
                    <input type="number" name="price" required>
                </div>
                <div class="form-group">
                    <label>URL изображения</label>
                    <input type="url" name="image_url" placeholder="https://..." required>
                </div>
                <div class="form-group">
                    <label>Категория</label>
                    <select name="category">
                        <option>Экзотика</option>
                        <option>Сети</option>
                        <option>Ветки</option>
                        <option>Ранункулюсы</option>
                        <option>Зелень</option>
                        <option>Гвоздики</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Цвета (через запятую)</label>
                    <input type="text" name="colors" placeholder="Белые, Красные">
                </div>
                <div class="form-group">
                    <label>Характеристики (через запятую)</label>
                    <input type="text" name="characteristics" placeholder="Высокие, Ароматные">
                </div>
                <div class="form-group">
                    <label>Доставка</label>
                    <select name="delivery_type">
                        <option value="today">Доставим сегодня</option>
                        <option value="tomorrow">Доставим завтра</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Описание</label>
                    <textarea name="description"></textarea>
                </div>
                <button type="submit">Добавить товар</button>
            </form>
        </div>
        
        <!-- Products List -->
        <div class="section">
            <h2>Все товары</h2>
            <div id="products-list" class="products-list"></div>
        </div>
        
        <!-- Orders List -->
        <div class="section">
            <h2>Заказы</h2>
            <div id="orders-list" class="orders-list"></div>
        </div>
    </div>
    
    <script>
        const API_URL = '/api';
        
        // Load products
        async function loadProducts() {
            const response = await fetch(`${API_URL}/products`);
            const products = await response.json();
            
            const container = document.getElementById('products-list');
            container.innerHTML = products.map(p => `
                <div class="product-card">
                    <img src="${p.image_url}" alt="${p.name}">
                    <h3>${p.name}</h3>
                    <div class="price">${p.price} ₽</div>
                    <p><strong>Категория:</strong> ${p.category}</p>
                    <p><strong>Доставка:</strong> ${p.delivery_type === 'today' ? 'Сегодня' : 'Завтра'}</p>
                    <div class="product-actions">
                        <button class="delete-btn" onclick="deleteProduct(${p.id})">Удалить</button>
                    </div>
                </div>
            `).join('');
        }
        
        // Load orders
        async function loadOrders() {
            const response = await fetch(`${API_URL}/orders`);
            const orders = await response.json();
            
            const container = document.getElementById('orders-list');
            if (orders.length === 0) {
                container.innerHTML = '<p>Заказов пока нет</p>';
                return;
            }
            
            container.innerHTML = orders.map(o => `
                <div class="order-card">
                    <h3>Заказ #${o.id}</h3>
                    <div class="order-info">
                        <div><strong>Имя:</strong> ${o.customer_name}</div>
                        <div><strong>Телефон:</strong> ${o.customer_phone}</div>
                        <div><strong>Адрес:</strong> ${o.customer_address}</div>
                        <div><strong>Сумма:</strong> ${o.total_price} ₽</div>
                    </div>
                    <div class="order-items">
                        <strong>Товары:</strong>
                        ${o.items.map(item => `<div>- ${item.name} x${item.quantity} = ${item.price * item.quantity} ₽</div>`).join('')}
                    </div>
                    <small>Дата: ${new Date(o.created_at).toLocaleString('ru-RU')}</small>
                </div>
            `).join('');
        }
        
        // Add product form
        document.getElementById('add-product-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            data.price = parseInt(data.price);
            
            const response = await fetch(`${API_URL}/products`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showSuccess('Товар добавлен!');
                e.target.reset();
                loadProducts();
            }
        });
        
        // Delete product
        async function deleteProduct(id) {
            if (!confirm('Удалить товар?')) return;
            
            await fetch(`${API_URL}/products/${id}`, { method: 'DELETE' });
            showSuccess('Товар удален!');
            loadProducts();
        }
        
        // Show success message
        function showSuccess(message) {
            const el = document.getElementById('success-message');
            el.textContent = message;
            el.style.display = 'block';
            setTimeout(() => el.style.display = 'none', 3000);
        }
        
        // Initial load
        loadProducts();
        loadOrders();
        
        // Refresh orders every 30 seconds
        setInterval(loadOrders, 30000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
