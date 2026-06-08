const urlAPI = 'http://localhost:5000/api/materiales';


async function cargarInventario() {
    const respuesta = await fetch(urlAPI);
    const materiales = await respuesta.json();
    
    const tabla = document.getElementById('lista-materiales');
    tabla.innerHTML = ''; 

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

    
    document.getElementById('nombre').value = '';
    document.getElementById('cantidad').value = '';

    cargarInventario();
}

cargarInventario();