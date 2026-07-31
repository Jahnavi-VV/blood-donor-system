from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)


# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Register Donor
@app.route('/register', methods=['POST'])
def register():

    try:

        # Form Data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']

        blood_group = request.form['blood_group']
        city = request.form['city']
        age = request.form['age']
        availability = request.form['availability']

        # MySQL Connection
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="blood_donor_system"
        )

        cursor = conn.cursor()

        # Insert Query
        query = '''
        INSERT INTO donors
        (name, blood_group, phone, city, age, availability)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''

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

        # Success Receipt Page
        return render_template(
            'success.html',
            name=name,
            blood_group=blood_group,
            city=city
        )

    except Exception as e:
        return f"Error: {e}"


# Search Donors
@app.route('/search')
def search():

    blood_group = request.args.get('blood_group')
    city = request.args.get('city')

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="blood_donor_system"
    )

    cursor = conn.cursor()

    query = '''
    SELECT id, name, blood_group, phone, city, age, availability
    FROM donors
    WHERE blood_group=%s
    AND city=%s
    AND availability='Yes'
    '''

    values = (blood_group, city)

    cursor.execute(query, values)

    donors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'results.html',
        donors=donors
    )


# Mark Donor Unavailable
@app.route('/mark_unavailable/<int:id>')
def mark_unavailable(id):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="blood_donor_system"
    )

    cursor = conn.cursor()

    query = '''
    UPDATE donors
    SET availability='No'
    WHERE id=%s
    '''

    cursor.execute(query, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)