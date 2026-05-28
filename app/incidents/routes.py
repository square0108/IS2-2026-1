from flask import Blueprint, render_template

incidents = Blueprint('incidents', __name__)

@incidents.route('/incidents')
def incidents_list():

    return render_template(
        'incidents/incidents_list.html'
    )