from flask import Blueprint, render_template

incidents = Blueprint('incidents', __name__)

fake_incidents = [
    {
        "id": 1,
        "date": "15/05/2026",
        "incident": "Pelea en recreo",
        "status": "Abierto"
    },
    {
        "id": 2,
        "date": "14/05/2026",
        "incident": "Llegó tarde a clases",
        "status": "En proceso"
    },
    {
        "id": 3,
        "date": "12/05/2026",
        "incident": "Uso indebido de celular",
        "status": "Finalizado"
    }
]

@incidents.route('/incidents')
def incidents_list():

    teacher_name = "Juan Pérez"

    return render_template(
        'incidents/incidents_list.html',
        teacher_name=teacher_name,
        incidents=fake_incidents
    )


@incidents.route('/incidents/<int:id>/edit')
def edit_incident(id):

    incident = None

    for i in fake_incidents:
        if i["id"] == id:
            incident = i
            break

    return render_template(
        'incidents/edit_incident.html',
        incident=incident
    )