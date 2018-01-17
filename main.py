from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:beproductive@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET'])
def index():
    blog_id = request.args.get('id')
    if blog_id:
        blog_id = int(blog_id)
        blog = Blog.query.get(blog_id)
        return render_template('onetime.html', blog=blog)
    bloglist = Blog.query.all()
    return render_template('blog.html', title="Build-a-Blog", bloglist=bloglist)

@app.route('/delete-blog', methods=['POST'])
def delete_blog():
    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.completed = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    body = ''
    title = ''
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        has_error = False
        if not title:
            flash("Please enter a title", 'error')
            has_error = True
        if not body:
            flash("Please enter a body", 'error')
            has_error = True
        if not has_error:
            blog = Blog(title, body)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(blog.id))
    return render_template('newpost.html', body=body, title=title)


if __name__ == '__main__':
    app.run()