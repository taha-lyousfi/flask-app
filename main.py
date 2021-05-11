from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "something random"
db = SQLAlchemy(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    firstname = db.Column(db.String(70))
    lastname = db.Column(db.String(70))

    def __init__(self, username, password, firstname, lastname, email):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.email = email


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin/")
def admin():
    if "username" in session:
        admin = User.query.filter_by(username="test").first()
        if (
            session["username"] == admin.username
            and session["password"] == admin.password
        ):
            return "<h1>Hello Admin <h1>"
        else:
            return redirect(url_for("user"))
    else:
        redirect(url_for("login"))


@app.route("/allusers/")
def all_users():
    users = User.query.all()
    return render_template("all.html", users=users)


@app.route("/signup/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_username = User.query.filter_by(
            username=request.form["username"]
        ).first()
        if existing_username:
            flash("Already used username")
            return redirect(url_for("register"))
        existing_email = User.query.filter_by(email=request.form["email"]).first()
        if existing_email:
            flash("Already used email")
            return redirect(url_for("register"))

        new_user = User(
            request.form["username"],
            request.form["password"],
            request.form["firstname"],
            request.form["lastname"],
            request.form["email"],
        )
        db.session.add(new_user)
        db.session.commit()
        session["username"] = request.form["username"]
        session["password"] = request.form["password"]
        session["firstname"] = request.form["firstname"]
        session["lastname"] = request.form["lastname"]
        session["email"] = request.form["email"]
        return redirect(url_for("user"))

    return render_template("register.html")


@app.route("/changeuser/", methods=["GET", "POST"])
def changeuser():
    if request.method == "POST":
        username = session["username"]
        username_ = request.form["username"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        password = request.form["password"]

        if username_ == username:
            user = User.query.filter_by(username=username_).first()
            user.firstname = firstname
            user.lastname = lastname
            user.password = password
            user.email = email
            db.session.add(user)
            db.session.commit()

            session["username"] = username
            session["password"] = password
            session["firstname"] = firstname
            session["lastname"] = lastname
            session["email"] = email
        else:
            flash("Choose your username please", "error")
            redirect(url_for("changeuser"))
        return redirect(url_for("user"))
    else:
        return render_template("modify.html")


@app.route("/logout/")
def logout():
    session.pop("username", None)
    session.pop("firstname", None)
    session.pop("lastname", None)
    session.pop("password", None)
    session.pop("email", None)
    return redirect(url_for("login"))


@app.route("/user/")
def user():
    if "username" in session:
        username = session["username"]
        firstname = session["firstname"]
        lastname = session["lastname"]
        email = session["email"]

        return render_template(
            "user.html",
            user=username,
            firstname=firstname,
            lastname=lastname,
            email=email,
        )
    return redirect(url_for("login"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("user"))
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]

        real_username = User.query.filter_by(username=username)
        if real_username:
            real_username = real_username.first()
            if real_username.password == password:
                session["username"] = username
                session["password"] = password
                session["firstname"] = real_username.firstname
                session["lastname"] = real_username.lastname
                session["email"] = real_username.email
            else:
                flash("Wrong username or wrong password", "error")
                redirect(url_for("login"))

        return redirect(url_for("user"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
