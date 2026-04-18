const urlAPI = 'http://localhost:5000/api/materiales';

// Función para pedir los datos a Python y dibujarlos en la tabla
async function cargarInventario() {
    const respuesta = await fetch(urlAPI);
    const materiales = await respuesta.json();
    
    const tabla = document.getElementById('lista-materiales');
    tabla.innerHTML = ''; // Limpiar la tabla antes de llenarla

    materiales.forEach(mat => {
        tabla.innerHTML += `
            <tr>
                <td>${mat.id}</td>
                <td>${mat.nombre}</td>
                <td><strong>${mat.cantidad}</strong></td>
                <td>${mat.unidad}</td>
            </tr>
        `;
    });
}

// Función para enviar los datos de los inputs a Python
async function guardarMaterial() {
    const nombre = document.getElementById('nombre').value;
    const cantidad = document.getElementById('cantidad').value;
    const unidad = document.getElementById('unidad').value;

    if (!nombre || !cantidad) {
        alert("Por favor llena todos los campos");
        return;
    }

    const nuevoMaterial = { nombre, cantidad, unidad };

    await fetch(urlAPI, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nuevoMaterial)
    });

    // Limpiar los campos
    document.getElementById('nombre').value = '';
    document.getElementById('cantidad').value = '';

    // Recargar la tabla
    cargarInventario();
}

// Cargar el inventario automáticamente cuando se abre la página
cargarInventario();