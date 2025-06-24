from flask import render_template

def edit(user):
    return render_template('users/edit.html', user=user)

def dashboard(user):
    return render_template('users/dashboard.html', user=user)

def perfil(user):
    return render_template("users/perfil_readonly.html", user=user)
