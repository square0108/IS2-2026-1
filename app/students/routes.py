# No estoy seguro si debería haber una ruta independiente "estudiantes", pues no son usuarios del sistema
# Ver la lista de estudiantes podría ser un componente para usuarios ya existentes, algo como /reporter/students/ 

from flask import Blueprint, render_template

students = Blueprint('students', __name__)

@students.route('/students')
def search_students():
    return render_template('students/search_students.html')