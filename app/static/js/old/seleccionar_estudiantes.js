// No sé JavaScript, tuve que generarlo con LLM
// 1. Cargar la lista desde la memoria del navegador, o crear una vacía
let selectedStudents = JSON.parse(localStorage.getItem('listaInvolucrados')) || [];

// 2. Cuando la página termine de cargar, reconstruir la lista visualmente
document.addEventListener('DOMContentLoaded', () => {
    if (selectedStudents.length > 0) {
        document.getElementById('emptyListMsg').style.display = 'none';
        selectedStudents.forEach(student => {
            renderInvolvedItem(student.id, student.name);
        });
    }
});

function addInvolucrado(studentId, studentName) {
    // Verificar si ya existe en el arreglo
    if (selectedStudents.some(s => s.id === studentId)) {
        alert(studentName + " ya está en la lista.");
        return;
    }
    // Chequear si la variable fue definida en el HTML y si ya alcanzamos el límite
    if (typeof window.MAX_STUDENTS !== 'undefined' && selectedStudents.length >= window.MAX_STUDENTS) {
        if (window.MAX_STUDENTS === 1) {
            // UX amigable: Si el límite es 1, simplemente reemplazamos al estudiante actual
            removeInvolucrado(selectedStudents[0].id);
        } else {
            // Si el límite es mayor a 1 (ej: máximo 3), mostramos una alerta
            alert("Has alcanzado el límite de estudiantes permitidos para este reporte.");
            return;
        }
    }

    // Agregar al arreglo y guardar en la memoria del navegador
    selectedStudents.push({ id: studentId, name: studentName });
    localStorage.setItem('listaInvolucrados', JSON.stringify(selectedStudents));

    // Ocultar el mensaje de "Vacío" y renderizar el item
    document.getElementById('emptyListMsg').style.display = 'none';
    renderInvolvedItem(studentId, studentName);
}

function renderInvolvedItem(studentId, studentName) {
    const involvedList = document.getElementById('involvedList');
    const listItem = document.createElement('li');
    listItem.className = "list-group-item d-flex justify-content-between align-items-center py-2";
    listItem.id = "involved-item-" + studentId;
    listItem.innerHTML = `
        ${studentName}
        <button type="button" class="btn btn-sm btn-danger" onclick="removeInvolucrado('${studentId}')">X</button>
    `;
    involvedList.appendChild(listItem);
}

function removeInvolucrado(studentId) {
    // Filtrar el estudiante eliminado y actualizar la memoria
    selectedStudents = selectedStudents.filter(s => s.id !== studentId);
    localStorage.setItem('listaInvolucrados', JSON.stringify(selectedStudents));

    // Eliminar los elementos visuales y ocultos
    document.getElementById("involved-item-" + studentId).remove();

    // Mostrar mensaje de vacío si ya no quedan estudiantes
    if (selectedStudents.length === 0) {
        document.getElementById('emptyListMsg').style.display = 'block';
    }
}

// Injección de los estudiantes involucrados al Form
const forms = document.querySelectorAll('.antecedenteForm');

forms.forEach(form => {
    form.addEventListener('submit', (e) => {
        // 1. Validar que la lista no esté vacía
        if (selectedStudents.length === 0) {
            e.preventDefault(); // Aborta el envío del POST a Flask
            alert("Debe seleccionar al menos un estudiante involucrado.");
            return;
        }

        // 2. Inyectar los IDs directamente en el formulario que disparó el evento
        selectedStudents.forEach(student => {
            const hiddenInput = document.createElement('input');
            hiddenInput.type = "hidden";
            hiddenInput.name = "id_estudiantes_involucrados";
            hiddenInput.value = student.id;
            form.appendChild(hiddenInput); // Se inyecta dentro del form específico (Diagnóstico u Observación)
        });

        // 3. Limpiar memoria para el próximo reporte
        localStorage.removeItem('listaInvolucrados');
    });
});