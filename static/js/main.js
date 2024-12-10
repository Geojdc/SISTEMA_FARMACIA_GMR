// ------------PARA VENTAS-------------
function mostrarPrecio() {
    var select = document.getElementById('id_pro');
    var precioInput = document.getElementById('precio');
    var selectedOption = select.options[select.selectedIndex];
    
    if (selectedOption) {
        var precio = selectedOption.getAttribute('data-precio');
        precioInput.value = precio ? parseFloat(precio).toFixed(2) : '';
    }
    calcularPrecioTotal(); // Calcular el precio total inmediatamente después de mostrar el precio unitario
}

function calcularPrecioTotal() {
    var precio = parseFloat(document.getElementById('precio').value) || 0;
    var cantidad = parseInt(document.getElementById('cantidad').value) || 0;
    var precioTotalInput = document.getElementById('precio_total');
    
    var precioTotal = precio * cantidad;
    precioTotalInput.value = precioTotal.toFixed(2);
}

function filtrarProductos() {
    var categoriaSelect = document.getElementById('cod_cate');
    var productosSelect = document.getElementById('id_pro');
    var categoriaSeleccionada = categoriaSelect.value;

    for (var i = 0; i < productosSelect.options.length; i++) {
        var option = productosSelect.options[i];
        if (option.getAttribute('data-categoria') === categoriaSeleccionada || option.value === '') {
            option.style.display = 'block';
        } else {
            option.style.display = 'none';
        }
    }

    productosSelect.value = '';
}
// ------------------------------------- para compras
function mostrarPrecio1(){
    var select = document.getElementById('id_pro');
    var precioInput = document.getElementById('precio_unitario');
    var selectedOption = select.options[select.selectedIndex];
    
    if (selectedOption) {
        var precio = selectedOption.getAttribute('data-precio');
        precioInput.value = precio ? parseFloat(precio).toFixed(2) : '';
    }
}
// ---------------------------------->-----------------
    function filtrarProductosYProveedores() {
        var categoriaSelect = document.getElementById('cod_cate');
        var productosSelect = document.getElementById('id_pro');
        var proveedorSelect = document.getElementById('cod_prov');
        var categoriaSeleccionada = categoriaSelect.value;
        var proveedorSeleccionado = categoriaSelect.options[categoriaSelect.selectedIndex].getAttribute('data-proveedor');
    
        // Filtrar productos
        for (var i = 0; i < productosSelect.options.length; i++) {
            var option = productosSelect.options[i];
            if (option.getAttribute('data-categoria') === categoriaSeleccionada || option.value === '') {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        }
    
        productosSelect.value = '';
    
        // Seleccionar proveedor automáticamente
        proveedorSelect.value = proveedorSeleccionado;
    }
    
    function calcularStockYTotal() {
        var cantidadCaja = parseFloat(document.getElementById('cantidad_caja').value) || 0;
        var cantidadUnidad = parseFloat(document.getElementById('cantidad_unidad').value) || 0;
        var precioCaja = parseFloat(document.getElementById('precio_caja').value) || 0;
        
        var stock = document.getElementById('stock');
        var precioTotal = document.getElementById('precio_total');
    
        stock.value = cantidadCaja * cantidadUnidad;
        precioTotal.value = (cantidadCaja * precioCaja).toFixed(2);
    }
        