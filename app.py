from flask import Flask, render_template, request, redirect, session
import pickle
from models import db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'very_secret_key_here'
app.config.update(
    SESSION_COOKIE_SECURE=False,
    REMEMBER_COOKIE_DURATION=3600  # Duration in seconds
)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Vulnerable SQL query
        query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        user = db.engine.execute(query).fetchone()
        if user:
            session['user_id'] = user.id
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('user_id')
        if user_id:
            post = Post(title=title, content=content, user_id=user_id)
            db.session.add(post)
            db.session.commit()
            return redirect('/')
    return render_template('create.html')

@app.route('/save', methods=['POST'])
def save():
    data = request.form['data']
    with open('data.pkl', 'wb') as file:
        pickle.dump(data, file)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
