"""HobbyHabit."""

from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Completion, Hobby, UserHobby


app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined  # Raises an error if an undefined variable is used in Jinja 2.
app.jinja_env.auto_reload = True  # What does this do??
app.secret_key = "ABC"  # Required to use Flask sessions and the debug toolbar.


# Display homepage.
@app.route('/', methods=['GET'])
def homepage():
    """Display homepage."""

    return render_template("homepage.html")


# Process registration then redirect to page displaying add hobbies form, or redirect existing user to login page.
@app.route('/register', methods=['POST'])
def register_user():
    """Process registration form and add user to database."""

    # Get data from form.
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    # Create new User and assign it data.
    new_user = User()
    new_user.username = username
    new_user.email = email
    new_user.password = password

    user = User.query.filter_by(email=email).first()  # Returns None if not in DB, which is Falsey.

    # Check if user already exists in DB. If account exists, redirect to login.
    if user:
        flash("An account with that email already exists")
        return redirect("/login")

    # Otherwise add user to DB, flash confirmation, and save user to session.
    else:
        db.session.add(new_user)
        db.session.commit()

        flash("Account successfully created")
        session["user_id"] = new_user.user_id

        return redirect("/add-hobbies")


# Display dynamic add hobbies form.
@app.route('/add-hobbies', methods=['GET'])
def display_add_hobbies_form():
    """Display add hobbies form."""

    return render_template("add-hobbies.html")


# Process add hobbies form and commit data to DB, then redirect to add goals page.
@app.route('/process-hobbies', methods=['POST'])
def process_add_hobbies_form():
    """Process add hobbies form."""

    # Get data from form.
    num_hobbies = request.form["num-hobbies"]

    # Make as many new goals as user adds to form.
    for hobby_num in range(int(num_hobbies)):

        # Get hobby name, see if it's in the DB
        hobby_name = request.form.get("hobby-name-" + str(hobby_num + 1))
        hobby_obj = Hobby.query.filter(Hobby.hobby_name == hobby_name).first()

        # If hobby not in the DB, add to DB.
        if not hobby_obj:
            hobby_obj = Hobby(hobby_name=hobby_name)
            db.session.add(hobby_obj)
            db.session.commit()

    # What's connecting the hobbies the user adds to the actual user(user_id)?? The session??
    return redirect("/add-goals")


# Display add goals form.
@app.route('/add-goals', methods=['GET'])
def display_add_goals_form():
    """Display add goals form."""

    # Get current user from session.
    current_user = session["user_id"]

    # Get list of current user's hobbies from DB.
    current_user_hobbies = db.session.query(User.hobby.hobby_name).filter(User.user_id == current_user).all()

    # user_first_name = db.session.query(User.first_name).filter(User.user_id == current_user).first()

    # Render add goals template and pass list of hobbies to Jinja.
    return render_template("add-goals.html",
                           current_user_hobbies=current_user_hobbies)


# Process add goals form and commit data to DB, redirect to user dashboard.
@app.route('/process-goals', methods=['POST'])
def process_add_goals_form():
    """Process add goals form."""

    # # get data from form.
    # # add data to db, assigning to appropriate hobby.

    # # num_hobbies = request.form.get("num-hobbies")

    # #make as many new goals as were input
    # for hobby_num in range(num_hobbies):

    #     #get hobby name, see if it's in the DB
    #     hobby_name = request.form.get("hobby-name-" + str(hobby_num + 1))
    #     hobby_obj = Hobby.query.filter(Hobby.hobby_name == hobby_name).first()

    #     #if it's not in the DB, add it
    #     if not hobby_obj:
    #         hobby_obj = Hobby(hobby_name=hobby_name)
    #         db.session.add(hobby_obj)
    #         db.session.commit()

    #     #create a new goal and assign it data
    #     new_goal = Goal()
    #     new_goal.user_id = session["user_id"]
    #     new_goal.hobby = hobby_obj
    #     new_goal.goal_frequency_num = (
    #         request.form.get("hobby-freq-num-" + str(hobby_num + 1)))
    #     new_goal.goal_frequency_time_unit = (
    #         request.form.get("hobby-freq-time-unit-" + str(hobby_num + 1)))
    #     db.session.add(new_goal)

    # #add the new goals to the DB
    # db.session.commit()

    # return redirect("/dashboard")

    pass


# Display user dashboard.
@app.route('/dashboard', methods=['POST'])
def display_dashboard():
    """Display user's dashboard."""

    return render_template("dashboard.html")


# Display form on login page.
@app.route('/login', methods=['GET'])
def login_form():
    """Display login form."""

    return render_template("login-form.html")


# Process login form and add user to session.
@app.route('/login', methods=['POST'])
def process_login_form():
    """Process login form."""

    # Get data from form.
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()

    if not user:
        flash("Invalid username")
        return redirect("/login")

    if user.password != password:
        flash("Invalid password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Login successful")

    return redirect("/dashboard")


# Log user out and remove from session.
@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Log out successful")

    return redirect("/")


################################################################################


if __name__ == "__main__":

    app.debug = True
    DebugToolbarExtension(app)
    connect_to_db(app)
    app.run(host="0.0.0.0")