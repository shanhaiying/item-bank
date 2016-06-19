# *- coding: utf-8 -*

from flask import render_template, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from app.auth import auth
from app.models import User
from forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.index'))
        flash(u'账号或密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已经注销')
    return redirect(url_for('auth.login'))
