from flask import render_template

def detalle(vehiculo):
    return render_template("driver/vehiculo_readonly.html", vehiculo=vehiculo)

def formulario(form, vehiculo=None):
    return render_template("driver/vehiculo_form.html", form=form, vehiculo=vehiculo)
