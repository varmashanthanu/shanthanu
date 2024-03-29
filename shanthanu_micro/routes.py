from flask import render_template, redirect, url_for, request, flash
from shanthanu_micro import db, app
from shanthanu_micro.models import User, Post
from shanthanu_micro.forms import LoginForm, PostForm, PasswordForm
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, login_required, logout_user
import pandas as pd
from shanthanu_micro import admin_control as ac
from datetime import datetime as dt

db.create_all()
user = User.query.filter_by(username='admin').first()
if user is None:
    ac.create_admin()
else:
    print('Admin user already exists')


def build_post(post, form):
    post.title = form.title.data
    post.category = form.category.data
    post.description = form.description.data
    post.body = form.body.data
    post.tags = form.tags.data
    post.draft = form.draft.data
    return post


@app.route('/')
def home():
    return render_template('home.html', title='Home')


@app.route('/blog_index')
def blog_index():
    if current_user.is_authenticated:
        table_data = pd.read_sql('SELECT * FROM POST;', db.session.bind)
    else:
        table_data = pd.read_sql('SELECT * FROM POST WHERE LOWER(category) NOT LIKE \'portfolio\' AND draft = False;', db.session.bind)
    if not table_data.empty:
        table_data['date_created'] = table_data.date_created.dt.strftime('%d %b, %Y')
    table_data = table_data[['id', 'title', 'description', 'tags', 'date_created']]
    return render_template('blog_index.html', title='thoughts', table_data=table_data)


@app.route('/view_blog/<int:post_id>')
def view_blog(post_id):
    # todo fix the parameters being sent in the response to consolidated post object
    post = Post.query.get(post_id)
    post.date_created = dt.strftime(post.date_created, '%d %b, %Y')
    return render_template('view_blog.html', post=post)


@app.route('/portfolio')
def portfolio():

    drafts = True if current_user.is_authenticated else False

    query_statement = 'SELECT * FROM POST WHERE LOWER(category) LIKE \'portfolio\''
    if not drafts:
        query_statement += ' AND draft = False'
    query_statement += ';'
    table_data = pd.read_sql(query_statement, db.session.bind)
    table_data.sort_values(['date_created'], ascending=[0], inplace=True)
    table_data = table_data[['id', 'title', 'body']]
    return render_template('portfolio.html', title='Portfolio', data=table_data)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


# ----------------------------------- ADMIN FUNCTIONS ----------------------------------- #


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog_index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('blog_index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('blog_index'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    form = PasswordForm()
    message = None
    if request.method == 'POST' and form.validate_on_submit():
        if form.validate_on_submit():
            user = User.query.filter_by(username='admin').first()
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            message = 'Successfully changed password'
        else:
            message = 'Failed'
    return render_template('admin.html', form=form, title='Admin Dashboard', message=message)


@app.route('/add_blog', methods=['GET', 'POST'])
@login_required
def add_blog():
    # todo something wrong with the way the post object comes in - made part of the url
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post = build_post(post=post, form=form)
        db.session.add(post)
        db.session.commit()
        return render_template('view_blog.html', post=post)
    return render_template('add_blog.html', title='New Blog', form=form)


@app.route('/edit_blog/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(post_id):
    post = Post.query.get(post_id)
    form = PostForm(obj=post)
    if request.method == 'POST' and form.validate_on_submit():
        post = build_post(post=post, form=form)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('view_blog', post_id=post.id))
    return render_template('add_blog.html', title=post.title + ' - Edit', form=form)


@app.route('/delete_blog/<int:post_id>')
@login_required
def delete_blog(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog_index'))
