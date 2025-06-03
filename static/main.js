function validarEntrada() {
  const funcion = document.getElementById('funcion').value.trim();
  const variable = document.getElementById('variable').value.trim();
  const punto = document.getElementById('punto').value.trim();

  if (!funcion) {
    Swal.fire({
      title: 'Error',
      text: 'Por favor ingresa una función',
      icon: 'error',
    });
    return false;
  }

  if (!variable || !/^[a-zA-Z]$/.test(variable)) {
    Swal.fire({
      title: 'Error',
      text: 'La variable debe ser un solo carácter alfabético',
      icon: 'error',
    });
    return false;
  }

  if (!punto) {
    Swal.fire({
      title: 'Error',
      text: 'Por favor ingresa un punto para evaluar el límite',
      icon: 'error',
    });
    return false;
  }

  // Validar que el punto sea un número o infinito
  if (!/^-?\d*\.?\d+$|^oo$|^-oo$|^inf(inity)?$/i.test(punto)) {
    Swal.fire({
      title: 'Error',
      text: 'El punto debe ser un número, oo (infinito) o -oo (menos infinito)',
      icon: 'error',
    });
    return false;
  }

  return true;
}

function calcularLimite() {
  if (!validarEntrada()) return;

  const funcion = document.getElementById('funcion').value.trim();
  const variable = document.getElementById('variable').value.trim();
  const punto = document.getElementById('punto').value.trim();
  const resultadoDiv = document.getElementById('resultado');

  // Mostrar loader mientras se calcula
  Swal.fire({
    title: 'Calculando',
    html: 'Procesando el límite...',
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  // Limpiar resultados previos
  resultadoDiv.innerHTML = '';

  // Crear el cuerpo de la solicitud
  const data = {
    funcion: funcion,
    variable: variable,
    punto: punto,
  };

  // Enviar datos al backend
  fetch('/calcular', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Error en la respuesta del servidor');
      }
      return response.json();
    })
    .then((data) => {
      Swal.close();
      if (data.error) {
        Swal.fire({
          title: 'Error en el cálculo',
          text: data.error,
          icon: 'error',
        });
      } else {
        mostrarResultado(data);
      }
    })
    .catch((error) => {
      Swal.fire({
        title: 'Error',
        text: `Error al conectar con el servidor: ${error.message}`,
        icon: 'error',
      });
    });
}

function mostrarResultado(data) {
  const resultadoDiv = document.getElementById('resultado');
  resultadoDiv.classList.remove('hidden');

  let html = `
          <div class="space-y-6">
            <!-- Función original -->
            <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <h4 class="font-semibold text-gray-700 mb-2">Función original</h4>
              <div class="latex block text-lg">${data.funcion_original}</div>
            </div>
            
            <!-- Límite calculado -->
            <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <h4 class="font-semibold text-gray-700 mb-2">Límite calculado</h4>
              <div class="latex block text-xl font-mono text-primary-600">${
                data.limite
              }</div>
            </div>
            
            <!-- Discontinuidad -->
            <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
              <h4 class="font-semibold text-gray-700 mb-2">Tipo de discontinuidad</h4>
              <p class="text-gray-600 mb-1">${
                data.discontinuidad.descripcion
              }</p>
              <p class="text-lg font-medium ${
                data.discontinuidad.tipo === 'continua'
                  ? 'text-green-600'
                  : data.discontinuidad.tipo === 'evitable'
                  ? 'text-blue-600'
                  : 'text-red-600'
              }">
                ${data.discontinuidad.texto}
              </p>
            </div>
        `;

  // Mostrar función redefinida si es evitable
  if (data.discontinuidad.tipo === 'evitable') {
    html += `
            <div class="bg-green-50 p-4 rounded-lg border border-green-200">
              <h4 class="font-semibold text-green-800 mb-2">Función redefinida</h4>
              <div class="latex block">${data.funcion_redefinida}</div>
            </div>
          `;
  }

  html += `</div>`;
  resultadoDiv.innerHTML = html;
  renderLatex(resultadoDiv);
}

// function mostrarResultado(data) {
//   const resultadoDiv = document.getElementById('resultado');
//   let html = `<h3 class="font-bold text-lg mb-2">Resultado:</h3>`;

//   if (data.error) {
//     html += `<p class="text-red-600">${data.error}</p>`;
//   } else {
//     // Mostrar función original
//     html += `
//       <div class="mb-4">
//         <p><strong>Función original:</strong></p>
//         <div class="latex block">${data.funcion_original}</div>
//       </div>
//     `;

//     // Mostrar límite calculado
//     html += `
//       <div class="mb-4">
//         <p><strong>Límite:</strong></p>
//         <div class="latex block">${data.limite}</div>
//       </div>
//     `;

//     // Mostrar discontinuidad
//     html += `
//       <div class="mb-4">
//         <p><strong>Discontinuidad:</strong> ${data.discontinuidad.descripcion}</p>
//         <p class="text-blue-600"><strong>${data.discontinuidad.texto}</strong></p>
//       </div>
//     `;

//     // Mostrar función redefinida si es evitable
//     if (data.discontinuidad.tipo === 'evitable') {
//       html += `
//         <div class="mt-4 p-3 bg-green-50 rounded">
//           <p class="font-semibold">Función redefinida:</p>
//           <div class="latex block">${data.funcion_redefinida}</div>
//         </div>
//       `;
//     }
//   }

//   resultadoDiv.innerHTML = html;
//   renderLatex(resultadoDiv); // Renderizar LaTeX
// }

function renderLatex(element) {
  const texElements = element.querySelectorAll('.latex');
  texElements.forEach((el) => {
    try {
      katex.render(el.textContent, el, {
        throwOnError: false,
        displayMode: el.classList.contains('block'),
      });
    } catch (e) {
      console.error(e);
    }
  });
}
