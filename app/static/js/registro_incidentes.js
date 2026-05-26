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

    // Agregar al arreglo y guardar en la memoria del navegador
    selectedStudents.push({ id: studentId, name: studentName });
    localStorage.setItem('listaInvolucrados', JSON.stringify(selectedStudents));

    // Ocultar el mensaje de "Vacío" y renderizar el item
    document.getElementById('emptyListMsg').style.display = 'none';
    renderInvolvedItem(studentId, studentName);
}

function removeInvolucrado(studentId) {
    // Filtrar el estudiante eliminado y actualizar la memoria
    selectedStudents = selectedStudents.filter(s => s.id !== studentId);
    localStorage.setItem('listaInvolucrados', JSON.stringify(selectedStudents));

    // Eliminar los elementos visuales y ocultos
    document.getElementById("involved-item-" + studentId).remove();
    document.getElementById("hidden-input-" + studentId).remove();

    // Mostrar mensaje de vacío si ya no quedan estudiantes
    if (selectedStudents.length === 0) {
        document.getElementById('emptyListMsg').style.display = 'block';
    }
}

// 3. Función auxiliar para inyectar el HTML (Evita repetir código)
function renderInvolvedItem(studentId, studentName) {
    // A. Crear el elemento visual en la lista
    const involvedList = document.getElementById('involvedList');
    const listItem = document.createElement('li');
    listItem.className = "list-group-item d-flex justify-content-between align-items-center py-2";
    listItem.id = "involved-item-" + studentId;
    listItem.innerHTML = `
        ${studentName}
        <button type="button" class="btn btn-sm btn-danger" onclick="removeInvolucrado('${studentId}')">X</button>
    `;
    involvedList.appendChild(listItem);

    // B. Crear el input oculto para que Flask lo reciba en el POST
    const hiddenContainer = document.getElementById('hiddenInputsContainer');
    const hiddenInput = document.createElement('input');
    hiddenInput.type = "hidden";
    hiddenInput.name = "id_estudiantes_involucrados"; // Key de acceso enviada al POST
    hiddenInput.value = studentId;
    hiddenInput.id = "hidden-input-" + studentId;
    hiddenContainer.appendChild(hiddenInput);
}

// 4. LIMPIEZA: Borrar la memoria SOLO cuando el formulario se envíe exitosamente
const form = document.getElementById('incidentForm');
if (form) {
    form.addEventListener('submit', () => {
        // Al darle a "Registrar Incidente", limpiamos la lista para el siguiente reporte
        localStorage.removeItem('listaInvolucrados');
    });
}