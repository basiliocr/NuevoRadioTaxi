from flask import render_template

def dashboard(conductor):
    return render_template("driver/dashboard.html", conductor=conductor)

def perfil(conductor):
    return render_template("driver/perfil_readonly.html", conductor=conductor)

def vehiculo(conductor, vehiculo):
    return render_template("driver/vehiculo.html", conductor=conductor, vehiculo=vehiculo)
