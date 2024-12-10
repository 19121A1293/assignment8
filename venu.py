from flask import Flask, request, render_template, jsonify
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Database credentials from environment variables
credentials = {
    "host": os.getenv("DB_HOST"),  # PostgreSQL host
    "username": os.getenv("DB_USERNAME"),  # PostgreSQL default user
    "password": os.getenv("DB_PASSWORD"),  # Your PostgreSQL password
    "dbname": os.getenv("DB_NAME"),  # The name of your PostgreSQL database
    "port": int(os.getenv("DB_PORT", 5432))  # Default PostgreSQL port
}

def connect_to_database():
    # Connect to PostgreSQL database
    connection = psycopg2.connect(
        host=credentials["host"],
        user=credentials["username"],
        password=credentials["password"],
        dbname=credentials["dbname"],
        port=credentials["port"]
    )
    return connection

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Create table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            text VARCHAR(255) NOT NULL
        )
        """)

        # If it's a POST request, insert the message into the database
        if request.method == "POST":
            message = request.form.get("message")
            if message:
                cursor.execute("INSERT INTO messages (text) VALUES (%s)", (message,))
                connection.commit()

        # Read all messages
        cursor.execute("SELECT * FROM messages")
        results = cursor.fetchall()

        # Clean up and close connection
        cursor.close()
        connection.close()

        # Render the index template with messages
        return render_template("index.html", messages=results)

    except Exception as e:
        # Return any error that occurs during DB interaction
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)