
import mysql.connector
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from pathlib import Path
import html


# 1. MySQL Connection

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="login_signup"
)

cursor = conn.cursor()

print("MySQL Connected Successfully!")


# 2. Request Handler

class MyHandler(BaseHTTPRequestHandler):

    # Display HTML Pages

    def send_page(self, filename):

        file_path = Path(__file__).parent / filename

        content = file_path.read_text(encoding="utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.end_headers()

        self.wfile.write(content.encode("utf-8"))


    # GET Request

    def do_GET(self):

        if self.path == "/":
            self.send_page("home.html")

        elif self.path == "/signup":
            self.send_page("signUp.html")

        elif self.path == "/login":
            self.send_page("login.html")

        else:
            self.send_error(404, "Page Not Found")


    # POST Request

    def do_POST(self):

        length = int(self.headers.get("Content-Length", 0))

        body = self.rfile.read(length).decode("utf-8")

        data = parse_qs(body)

        # SIGNUP

        if self.path == "/signup":

            name = data.get("name", [""])[0].strip()
            email = data.get("email", [""])[0].strip()
            password = data.get("password", [""])[0]

            if not name or not email or not password:
                self.send_error(400, "All fields are required")
                return

            try:

                query = """
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
                """

                values = (name, email, password)

                cursor.execute(query, values)

                conn.commit()

                self.send_html("""
                    <h2>Signup Successful!</h2>
                    <a href="/login">Login Now</a>
                """)

            except mysql.connector.IntegrityError:

                conn.rollback()

                self.send_html("""
                    <h2>Email Already Registered!</h2>
                    <a href="/signup">Try Again</a>
                """)

        # LOGIN

        elif self.path == "/login":

            email = data.get("email", [""])[0].strip()
            password = data.get("password", [""])[0]

            query = """
            SELECT name
            FROM users
            WHERE email = %s AND password = %s
            """

            cursor.execute(query, (email, password))

            user = cursor.fetchone()

            if user:

                name = html.escape(user[0])

                self.send_html(f"""
                    <h2>Welcome {name}!</h2>
                    <p>Login Successful!</p>
                    <a href="/">Go Home</a>
                """)

            else:

                self.send_html("""
                    <h2>Invalid Email or Password!</h2>
                    <a href="/login">Try Again</a>
                """)

        else:

            self.send_error(404, "Page Not Found")


    # Send HTML Response

    def send_html(self, content):

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.end_headers()

        self.wfile.write(content.encode("utf-8"))


# 3. Start Server

server = HTTPServer(("localhost", 8000), MyHandler)

print("Server running at http://localhost:8000")

server.serve_forever()
