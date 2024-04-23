from datetime import datetime

from flask import render_template, request, url_for, flash, current_app
from werkzeug.utils import redirect
from flask_login import current_user, login_user, logout_user
from flask_babel import _

from app.forms import MessageForm
from app.models import Message
from app import db
from app.models import User
from app.models import CocktailDTO
from app.forms import SimpleForm, EvalForm, LoginForm, RegistrationForm, ResetPasswordForm
from app import app, cocktailRecommender
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email

from flask_paginate import Pagination, get_page_args
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')

def index():
    return render_template('index.html')

@app.route('/cocktails')
def cocktails():
    return render_template('cocktails.html')

@app.route('/specially4u', methods=["GET", "POST"])
def specially4u():
    form = SimpleForm()
    error = ""
    if form.validate_on_submit():
        if len(form.fruits_cb.data) + len(form.alco_cb.data) + len(form.nonalco_cb.data) + len(form.others_cb.data) < 2:
            error = "You must selected at least two ingredients"
            return render_template('specially4u.html', form=form, error=error)
        else:
            
            response = [form.fruits_cb.data, form.alco_cb.data, form.nonalco_cb.data, form.others_cb.data]
            user_query = [val.lower() for sublist in response for val in sublist]
            print('USER QUERY ', user_query)

            
            cocktail = cocktailRecommender.get_recommendation(user_query)

            if cocktail.name is None:
                return render_template('no_recommendation.html', user_query=user_query)
            else:
                return redirect(url_for('cocktail', name=cocktail.name, ask_eval=True))
    return render_template('specially4u.html', form=form, error=error)

@app.route('/help')
def help():
    return render_template('help.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', name=''), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', name=''), 500




if __name__ == '__main__':
        app.run(debug=True)