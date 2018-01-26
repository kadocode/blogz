from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'mysupersecretkey'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    completed = db.Column(db.Boolean)
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        self.completed = False

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username 
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in!", "success")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #TODO - validate
        if len(username) < 3 or len(username) > 20 or " " in username:
             flash("Username Not Valid", 'error')
        if len(password) < 3 or len(password) > 20 or " " in password:
             flash("Password Not Valid", 'error')
        if password != verify:
             flash("Passwords Do Not Match", 'error')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            #TODO - user better response messaging
            flash("That user already exists!", 'error')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def blog_index():
    
    blog_id = request.args.get('id')
    if blog_id:
        blog_id = int(blog_id)
        blog = Blog.query.get(blog_id)
        return render_template('onetime.html', blog=blog)
    blogs = Blog.query.filter_by(completed=False).all()
    return render_template('blog.html', title="Start A Blog!", blogs=blogs)

@app.route('/delete-blog', methods=['POST'])
def delete_blog():
    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.completed = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    body = ''
    title = ''
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner =User.query.filter_by(username=session['username']).first()
        has_error = False
        if not title:
            flash("Please enter a title", 'error')
            has_error = True
        if not body:
            flash("Please enter a body", 'error')
            has_error = True
        if not has_error:
            blog = Blog(title, body, owner)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(blog.id))
    return render_template('newpost.html', body=body, title=title)

@app.route('/')
def index():
    user_list = User.query.all()
    return render_template('index.html', user_list=user_list)


if __name__ == '__main__':
    app.run()