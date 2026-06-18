let selectedStudents = JSON.parse(localStorage.getItem('listaInvolucrados')) || [];

document.addEventListener('DOMContentLoaded', () => {
    if (selectedStudents.length > 0) {
        document.getElementById('emptyListMsg').style.display = 'none';
        selectedStudents.forEach(student => renderInvolvedItem(student.id, student.name));
        validarEstadoFormulario();
    }

    const selectTipo = document.getElementById('tipoAntecedente');
    
    selectTipo.addEventListener('change', function() {
        const tipoSeleccionado = this.value;
        
        limpiarFormularioYEstudiantes();

        document.querySelectorAll('.formulario-dinamico').forEach(bloque => {
            bloque.style.display = 'none';
        });

        document.querySelectorAll('.inputs-incidente, .inputs-diagnostico').forEach(input => {
            input.removeAttribute('required');
        });

        const helperText = document.getElementById('reglaEstudiantesHelper');
        const txtDescripcion = document.getElementById('descripcionGeneral');
        
        document.getElementById('bloque-descripcion').style.display = 'block';
        document.getElementById('btnSubmitForm').style.display = 'block';

        // Lógica de textos y despliegues según tipo
        if (tipoSeleccionado === 'incidente') {
            document.getElementById('bloque-incidente').style.display = 'block';
            document.querySelectorAll('.inputs-incidente').forEach(i => i.setAttribute('required', 'true'));
            
            helperText.innerText = "Registro de un evento puntual que afecta la convivencia escolar.";
            txtDescripcion.placeholder = "Describa el incidente (ej. Juan empujó a Pedro en el patio durante el recreo).";
            
        } else if (tipoSeleccionado === 'diagnostico') {
            document.getElementById('bloque-diagnostico').style.display = 'block';
            document.querySelectorAll('.inputs-diagnostico').forEach(i => i.setAttribute('required', 'true'));
            
            helperText.innerText = "Evaluación formal de una condición mental, conductual o de personalidad.";
            txtDescripcion.placeholder = "Describa los detalles o el razonamiento del diagnóstico.";
            
        } else if (tipoSeleccionado === 'observacion') {
            helperText.innerText = "Anotación sobre conductas, estado de ánimo o situaciones de interés general.";
            txtDescripcion.placeholder = "Describa la observación (ej. María se ha mostrado inusualmente retraída y no participa en clases).";
        }

        validarEstadoFormulario();
    });

    document.getElementById('antecedenteForm').addEventListener('submit', (e) => {
        const tipoActual = selectTipo.value;

        if (selectedStudents.length === 0) {
            e.preventDefault();
            alert("Debe seleccionar al menos un estudiante involucrado.");
            return;
        }

        // Medida de seguridad extra antes de enviar
        if (tipoActual === 'diagnostico' && selectedStudents.length > 1) {
            e.preventDefault();
            return;
        }

        selectedStudents.forEach(student => {
            const hiddenInput = document.createElement('input');
            hiddenInput.type = "hidden";
            hiddenInput.name = "id_estudiantes_involucrados";
            hiddenInput.value = student.id;
            e.target.appendChild(hiddenInput);
        });

        localStorage.removeItem('listaInvolucrados');
    });
});

function limpiarFormularioYEstudiantes() {
    document.querySelectorAll('.formulario-dinamico input, .formulario-dinamico textarea, .formulario-dinamico select').forEach(el => {
        el.value = "";
    });
    document.getElementById('descripcionGeneral').value = "";

    selectedStudents = [];
    localStorage.removeItem('listaInvolucrados');
    
    const listaUI = document.getElementById('involvedList');
    Array.from(listaUI.children).forEach(child => {
        if (child.id !== 'emptyListMsg') child.remove();
    });
    
    document.getElementById('emptyListMsg').style.display = 'block';
    validarEstadoFormulario();
}

function addInvolucrado(studentId, studentName) {
    if (selectedStudents.some(s => s.id === studentId)) {
        alert(studentName + " ya está en la lista.");
        return;
    }

    selectedStudents.push({ id: studentId, name: studentName });
    localStorage.setItem('listaInvolucrados', JSON.stringify(selectedStudents));

    document.getElementById('emptyListMsg').style.display = 'none';
    renderInvolvedItem(studentId, studentName);
    validarEstadoFormulario();
}

function removeInvolucrado(studentId) {
    selectedStudents = selectedStudents.filter(s => s.id !== studentId);
    localStorage.setItem('listaInvolucrados', JSON.stringify(selectedStudents));
    document.getElementById("involved-item-" + studentId).remove();

    if (selectedStudents.length === 0) {
        document.getElementById('emptyListMsg').style.display = 'block';
    }
    validarEstadoFormulario();
}

function renderInvolvedItem(studentId, studentName) {
    const involvedList = document.getElementById('involvedList');
    const listItem = document.createElement('li');
    listItem.className = "list-group-item d-flex justify-content-between align-items-center py-2";
    listItem.id = "involved-item-" + studentId;
    listItem.innerHTML = `
        ${studentName}
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeInvolucrado('${studentId}')">X</button>
    `;
    involvedList.appendChild(listItem);
}

// Función centralizada para evaluar reglas reactivamente
function validarEstadoFormulario() {
    document.getElementById('contadorEstudiantes').innerText = selectedStudents.length;
    
    const tipoActual = document.getElementById('tipoAntecedente').value;
    const btnSubmit = document.getElementById('btnSubmitForm');
    const warningDiagnostico = document.getElementById('diagnosticoWarning');

    // Revisar regla estricta del diagnóstico
    if (tipoActual === 'diagnostico' && selectedStudents.length > 1) {
        warningDiagnostico.style.display = 'block';
        btnSubmit.disabled = true;
    } else {
        warningDiagnostico.style.display = 'none';
        btnSubmit.disabled = false;
    }
}