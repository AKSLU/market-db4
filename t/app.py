from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        dbname="base",
        user="postgres",
        password="20062007",
        host="localhost",
        port="5432"
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username = %s AND password = %s", (username, password))
            result = cursor.fetchone()

            if result:
                cursor.execute("""
                    SELECT items2.id, name, price, description, image_url, count, supplier
                    FROM items2
                    JOIN quantity ON items2.id = quantity.id
                """)
                items = cursor.fetchall()
                cursor.close()
                conn.close()
                return render_template('items.html', items=items)
            else:
                cursor.close()
                conn.close()
                return render_template('login.html', error="Invalid username or password")
        except Exception as e:
            return f"Database connection error: {e}"

    return render_template('login.html')

@app.route('/items')
def show_items():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT items2.id, name, price, description, image_url, count, supplier
            FROM items2
            JOIN quantity ON items2.id = quantity.id
        """)
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('items.html', items=items)
    except Exception as e:
        return f"Error loading items: {e}"

@app.route('/buys')
def show_buys():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.item_name, b.cost, u.username, u.balance
            FROM buys b
            LEFT JOIN users u ON b.user_id = u.user_id
        """)
        buys = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('buys.html', buys=buys)
    except Exception as e:
        return f"Error loading purchases: {e}"

@app.route('/buy/<int:item_id>')
def buy(item_id):
    try:
        user_id = 1  

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT count FROM quantity WHERE id = %s", (item_id,))
        quantity_result = cursor.fetchone()

        cursor.execute("SELECT name, price FROM items2 WHERE id = %s", (item_id,))
        item_result = cursor.fetchone()

        cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        balance_result = cursor.fetchone()

        if quantity_result and quantity_result[0] > 0 and item_result and balance_result:
            name, price = item_result
            balance = balance_result[0]

            if balance >= price:
                cursor.execute("UPDATE quantity SET count = count - 1 WHERE id = %s", (item_id,))
                cursor.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (price, user_id))
                cursor.execute("""
                    INSERT INTO buys (item_name, cost, user_id)
                    VALUES (%s, %s, %s)
                """, (name, price, user_id))
                conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        return f"Purchase error: {e}"

    return redirect('/items')

if __name__ == '__main__':
    app.run(debug=True)





