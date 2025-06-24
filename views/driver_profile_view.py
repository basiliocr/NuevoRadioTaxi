from flask import render_template

def detalle(perfil):
    return render_template("driver/perfil_readonly.html", perfil=perfil)

def formulario(form, perfil=None):
    return render_template("driver/perfil_form.html", form=form, perfil=perfil)
