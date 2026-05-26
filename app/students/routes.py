from flask import Blueprint, render_template

students = Blueprint('students', __name__)

@students.route('/students')
def search_students():
    return render_template('students/search_students.html')