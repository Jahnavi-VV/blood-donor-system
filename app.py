from flask import Flask, render_template, request, redirect
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# -----------------------------
# Database Connection Function
# -----------------------------
def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT")),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )


# -----------------------------
# Home Page
# -----------------------------
@app.route('/')
def home():
    return render_template('index.html')


# -----------------------------
# Register Donor
# -----------------------------
@app.route('/register', methods=['POST'])
def register():

    try:

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        blood_group = request.form['blood_group']
        city = request.form['city']
        age = request.form['age']
        availability = request.form['availability']

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO donors
        (name, blood_group, phone, city, age, availability)
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        values = (
            name,
            blood_group,
            phone,
            city,
            age,
            availability
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return render_template(
            "success.html",
            name=name,
            blood_group=blood_group,
            city=city
        )

    except Exception as e:
        return f"Error : {e}"


# -----------------------------
# Search by Blood Group
# -----------------------------
@app.route('/search_blood')
def search_blood():

    blood_group = request.args.get('blood_group')

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT id,name,blood_group,phone,city,age,availability
    FROM donors
    WHERE blood_group=%s
    AND availability='Yes'
    """

    cursor.execute(query, (blood_group,))
    donors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "results.html",
        donors=donors
    )


# -----------------------------
# Search by City
# -----------------------------
@app.route('/search_city')
def search_city():

    city = request.args.get('city')

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT id,name,blood_group,phone,city,age,availability
    FROM donors
    WHERE city=%s
    AND availability='Yes'
    """

    cursor.execute(query, (city,))
    donors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "results.html",
        donors=donors
    )


# -----------------------------
# Advanced Search
# -----------------------------
@app.route('/search')
def search():

    blood_group = request.args.get('blood_group')
    city = request.args.get('city')

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT id,name,blood_group,phone,city,age,availability
    FROM donors
    WHERE blood_group=%s
    AND city=%s
    AND availability='Yes'
    """

    cursor.execute(query, (blood_group, city))
    donors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "results.html",
        donors=donors
    )


# -----------------------------
# Mark Donor Unavailable
# -----------------------------
@app.route('/mark_unavailable/<int:id>')
def mark_unavailable(id):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE donors
    SET availability='No'
    WHERE id=%s
    """

    cursor.execute(query, (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/')

@app.route('/admin')
def admin():
    return render_template('admin_login.html')


@app.route('/admin_login', methods=['POST'])
def admin_login():

    username = request.form['username']
    password = request.form['password']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM admin WHERE username=%s AND password=%s",
        (username, password)
    )

    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    if admin:
        return redirect('/dashboard')
    else:
        return "Invalid Username or Password"


@app.route('/dashboard')
def dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM donors")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM donors WHERE availability='Yes'")
    available = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM donors WHERE availability='No'")
    unavailable = cursor.fetchone()[0]

    cursor.execute("SELECT id,name,blood_group,phone,city,age,availability FROM donors")
    donors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        available=available,
        unavailable=unavailable,
        donors=donors
    )
# -----------------------------
# Delete Donor
# -----------------------------
@app.route('/delete/<int:id>')
def delete(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM donors WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/dashboard')


# -----------------------------
# Edit Donor (Temporary)
# -----------------------------
@app.route('/edit/<int:id>')
def edit(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id,name,blood_group,phone,city,age,availability FROM donors WHERE id=%s",
        (id,)
    )

    donor = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit.html", donor=donor)
@app.route('/update/<int:id>', methods=['POST'])
def update(id):

    name = request.form['name']
    phone = request.form['phone']
    city = request.form['city']
    age = request.form['age']
    availability = request.form['availability']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE donors
        SET name=%s,
            phone=%s,
            city=%s,
            age=%s,
            availability=%s
        WHERE id=%s
    """, (name, phone, city, age, availability, id))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/dashboard')
# -----------------------------
# Run Flask
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)