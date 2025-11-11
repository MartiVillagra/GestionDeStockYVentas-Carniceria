
    // --- VARIABLES GLOBALES ---
    let carrito = [];
    let productoActual = '';
    let formaPago = '';
    let totalVenta = 0;

    // --- FUNCIONES DE PRODUCTOS ---
    function abrirModal(nombre, precio) {
      productoActual = nombre;
      document.getElementById('nombreProducto').innerText = nombre + ' - $' + precio + '/kg';
      document.getElementById('precioProducto').value = precio;
      document.getElementById('cantidad').value = '';
      new bootstrap.Modal(document.getElementById('modalCantidad')).show();
    }

    function agregarAlCarrito() {
      const cantidad = parseFloat(document.getElementById('cantidad').value);
      const precio = parseFloat(document.getElementById('precioProducto').value);
      if (!cantidad || cantidad <= 0) return alert('Ingrese una cantidad válida');

      const subtotal = cantidad * precio;
      carrito.push({ producto: productoActual, cantidad, precio, subtotal });

      actualizarCarrito();
      bootstrap.Modal.getInstance(document.getElementById('modalCantidad')).hide();
    }

    function eliminarProducto(index) {
      carrito.splice(index, 1);
      actualizarCarrito();
    }

    function actualizarCarrito() {
      const lista = document.getElementById('cart-items');
      lista.innerHTML = '';
      totalVenta = 0;

      if (carrito.length === 0) {
        lista.innerHTML = '<li class="list-group-item text-center text-gray-500 py-4">Vacío.</li>';
      } else {
        carrito.forEach((item, i) => {
          totalVenta += item.subtotal;
          lista.innerHTML += `
            <li class="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>${item.producto}</strong><br>
                <small>${item.cantidad} kg x $${item.precio}</small>
              </div>
              <div>
                <span class="fw-bold text-danger">$${item.subtotal.toFixed(2)}</span>
                <button class="btn btn-sm btn-danger ms-2" onclick="eliminarProducto(${i})">X</button>
              </div>
            </li>`;
        });
      }
      document.getElementById('cart-total').innerText = '$' + totalVenta.toFixed(2);
      calcularVuelto(); // actualiza si ya estaba en efectivo
    }

    // --- FORMAS DE PAGO ---
    function seleccionarPago(metodo) {
      formaPago = metodo;

      ['efectivo', 'tarjeta', 'transferencia'].forEach(id => {
        const btn = document.getElementById('btn-payment-' + id);
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-secondary');
      });

      const btnActivo = document.getElementById('btn-payment-' + metodo);
      btnActivo.classList.remove('btn-outline-secondary');
      btnActivo.classList.add('btn-primary');

      document.getElementById('efectivo-section').style.display = metodo === 'efectivo' ? 'block' : 'none';
    }

    function calcularVuelto() {
      if (formaPago !== 'efectivo') return;
      const recibido = parseFloat(document.getElementById('monto-recibido').value) || 0;
      const vuelto = recibido - totalVenta;
      document.getElementById('vuelto').innerText = vuelto >= 0 ? vuelto.toFixed(2) : '0.00';
    }

    // --- FINALIZAR VENTA ---
    document.getElementById('btn-finalize-sale').addEventListener('click', () => {
      if (carrito.length === 0) return alert('No hay productos en el carrito');
      if (!formaPago) return alert('Seleccione una forma de pago');

      if (formaPago === 'efectivo') {
        const recibido = parseFloat(document.getElementById('monto-recibido').value);
        if (!recibido || recibido < totalVenta) return alert('Monto insuficiente o inválido');
      }

      // Aquí conectarás con tu backend FastAPI:
      // fetch('/api/ventas', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ carrito, formaPago, totalVenta }) });

      alert(`Venta finalizada (${formaPago})\nTotal: $${totalVenta.toFixed(2)}`);

      carrito = [];
      actualizarCarrito();
      document.getElementById('monto-recibido').value = '';
      document.getElementById('vuelto').innerText = '0.00';
      seleccionarPago(''); // desactiva todo
    });

    // --- LIMPIAR CARRITO ---
    document.getElementById('btn-clear-cart').addEventListener('click', () => {
      if (confirm('¿Desea vaciar el carrito?')) {
        carrito = [];
        actualizarCarrito();
      }
    });

    // -- INICIO Y CIERRE DE CAJA
    document.getElementById('apertura-form').addEventListener('submit', async e => {
      e.preventDefault();
      await apiCall('caja/apertura', 'POST', { monto_inicial: parseFloat(monto_apertura.value) });
      alert('Caja abierta correctamente.');
      monto_apertura.value = '';
    });

    document.getElementById('btn-cierre').addEventListener('click', async () => {
      const resumen = await apiCall('caja/cierre', 'POST');
      document.getElementById('resumen-cierre').innerHTML = `
        <p><b>Total en Efectivo:</b> $${resumen.efectivo.toFixed(2)}</p>
        <p><b>Total en Tarjeta:</b> $${resumen.tarjeta.toFixed(2)}</p>
        <p><b>Total en Transferencia:</b> $${resumen.transferencia.toFixed(2)}</p>
        <p class="text-lg font-bold mt-2">TOTAL FINAL: $${resumen.total.toFixed(2)}</p>`;
    });

    // -- MOVIMIENTOS
    document.addEventListener("DOMContentLoaded", () => {
      cargarMovimientos();
      document.getElementById("formEgreso").addEventListener("submit", registrarEgreso);
    });

    // Cargar historial de movimientos
    async function cargarMovimientos() {
      const movimientos = await apiCall("movimientos/"); // 🔗 tu endpoint FastAPI

      const ingresos = movimientos.filter(m => m.tipo === "ingreso");
      const egresos = movimientos.filter(m => m.tipo === "egreso");

      renderTabla(ingresos, "tablaIngresos");
      renderTabla(egresos, "tablaEgresos");
    }

    // Mostrar tabla
    function renderTabla(lista, idTabla) {
      const tbody = document.getElementById(idTabla);
      tbody.innerHTML = "";

      if (lista.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted">Sin registros</td></tr>`;
        return;
      }

      lista.forEach(m => {
        const fila = `
          <tr>
            <td>${new Date(m.fecha).toLocaleDateString()}</td>
            <td>${m.descripcion}</td>
            <td>$${m.monto.toFixed(2)}</td>
          </tr>`;
        tbody.innerHTML += fila;
      });
    }

    // Registrar nuevo egreso
    async function registrarEgreso(e) {
      e.preventDefault();
      const egreso = {
        tipo: "egreso",
        descripcion: document.getElementById("descripcion").value,
        monto: parseFloat(document.getElementById("monto").value),
        fecha: document.getElementById("fecha").value
      };

      await apiCall("movimientos/", "POST", egreso);
      alert("✅ Egreso registrado correctamente");
      document.getElementById("formEgreso").reset();
      cargarMovimientos();
    }

    //-- RESUMEN
 document.addEventListener('DOMContentLoaded', async () => {
      const ventas = await apiCall('ventas/');
      const egresos = await apiCall('movimientos/');

      const totalVentas = ventas.reduce((a,b) => a + b.total, 0);
      const totalEgresos = egresos.reduce((a,b) => a + b.monto, 0);

      document.getElementById('ventas-totales').textContent = `$${totalVentas.toFixed(2)}`;
      document.getElementById('egresos-totales').textContent = `$${totalEgresos.toFixed(2)}`;
      document.getElementById('ganancia-neta').textContent = `$${(totalVentas - totalEgresos).toFixed(2)}`;

      const labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
      const data = [25000, 32000, 18000, 40000, 36000, 42000, 30000];

      new Chart(document.getElementById('grafico-ventas'), {
        type: 'bar',
        data: {
          labels,
          datasets: [{ label: 'Ventas Diarias ($)', data }]
        }
      });
    });

    //-- SUELDOS
document.addEventListener('DOMContentLoaded', async () => {
      const empleados = await apiCall('empleados/');
      const select = document.getElementById('empleado-sueldo');
      select.innerHTML = '<option value="">Seleccionar</option>';
      empleados.forEach(e => {
        select.innerHTML += `<option value="${e.id}">${e.nombre}</option>`;
      });
      cargarSueldos();
    });

    async function cargarSueldos() {
      const sueldos = await apiCall('sueldos/');
      const tabla = document.getElementById('tabla-sueldos');
      tabla.innerHTML = '';
      sueldos.forEach(s => {
        tabla.innerHTML += `
          <tr>
            <td>${s.fecha_pago}</td>
            <td>${s.empleado}</td>
            <td>${s.metodo_pago}</td>
            <td>$${s.monto.toFixed(2)}</td>
          </tr>`;
      });
    }

    document.getElementById('sueldo-form').addEventListener('submit', async e => {
      e.preventDefault();
      await apiCall('sueldos/', 'POST', {
        empleado_id: empleado-sueldo.value,
        monto: parseFloat(monto.value),
        metodo_pago: metodo.value
      });
      alert('Sueldo registrado correctamente');
      monto.value = '';
      cargarSueldos();
    });

    //-- STOCK
    document.addEventListener('DOMContentLoaded', loadProducts);

        async function loadProducts() {
            const res = await apiCall('productos/');
            const body = document.getElementById('stock-table-body');
            body.innerHTML = '';
            if (!res?.error) {
                res.forEach(p => {
                    body.innerHTML += `
          <tr>
            <td>${p.id_producto}</td>
            <td>${p.nombre_producto}</td>
            <td>${p.categoria}</td>
            <td>$${p.precio_gramo.toFixed(2)}</td>
            <td>${p.stock_gramo.toFixed(2)}</td>
            <td>
              <button class="btn btn-sm btn-warning" onclick="editProduct(${p.id_producto})">Editar</button>
              <button class="btn btn-sm btn-danger" onclick="deleteProduct(${p.id_producto})">Eliminar</button>
            </td>
          </tr>`;
                });
            }
        }

        async function deleteProduct(id) {
            if (confirm("¿Eliminar este producto?")) {
                await apiCall(`productos/${id}`, 'DELETE');
                loadProducts();
            }
        }

        function editProduct(id) {
            // completar para abrir modal con datos
        }