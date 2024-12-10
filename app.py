from flask import Flask ,render_template,url_for,request,redirect,session,flash
import sqlite3 
from datetime import datetime
#Libreria para gestion de los has en passwords
from werkzeug.security import generate_password_hash,check_password_hash

from functools import wraps

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file
import io
from reportlab.lib.pagesizes import letter, landscape

app=Flask(__name__)
app.secret_key = 'supersecretkey'
def init_db():
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    # -----------------SECCION DE CREACION DE TABLAS------------------------
    # TABLA USUARIO
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY,
        nombre_usuario TEXT NOT NULL,
        rol TEXT NOT NULL,
        usuario TEXT NOT NULL,
        password TEXT NOT NULL
        )
        """
    )
    conn.commit()
    # conn.close()
    # TABLA CLIENTES
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cliente (
        cod_cli INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        telefono TEXT NOT NULL
        )
        """
    )
    conn.commit()
    # TABLA VENTAS
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS venta(
    cod_ven INTEGER PRIMARY KEY AUTOINCREMENT, 
    fecha_ven TEXT NOT NULL,
    id_pro INTEGER NOT NULL,
    precio INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    cod_cli INTEGER NOT NULL,
    FOREIGN KEY (id_pro) REFERENCES producto (id_pro),
    FOREIGN KEY (cod_cli) REFERENCES cliente (cod_cli)
    )
    """
    )
    conn.commit()
    # TABLA PROVEEDORES
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS proveedores (
        cod_prov INTEGER PRIMARY KEY,
        nombre_prov TEXT NOT NULL,
        telefono_prov INTEGER NOT NULL,
        direccion TEXT NOT NULL
        )
        """
    )
    conn.commit()
    # TABLA CATEGORIA 
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categoria (
        cod_cate INTEGER PRIMARY KEY,
        nombre_cate TEXT NOT NULL,
        cod_prov INTEGER NOT NULL,
        FOREIGN KEY (cod_prov) REFERENCES proveedores (cod_prov)
        )
        """
    )
    conn.commit()
    #TABLA PRODUCTOS
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS producto (
        id_pro INTEGER PRIMARY KEY,
        cod_pro INTEGER NOT NULL,
        nombre_pro TEXT UNIQUE NOT NULL,
        precio_unitario INTEGER NOT NULL,
        precio_de_venta INTEGER NOT NULL,
        fecha_caducidad TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        descripcion TEXT NOT NULL,
        cod_cate INTEGER NOT NULL,
        FOREIGN KEY (cod_cate) REFERENCES categoria (cod_cate)
        )
        """
    )
    conn.commit()
    # TABLA COMPRAS
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS  compra(
    cod_com INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pro INTEGER NOT NULL, 
    stock INTEGER NOT NULL,
    cantidad_unidad INTEGER NOT NULL,
    cantidad_caja INTEGER NOT NULL,
    precio_caja INTEGER NOT NULL,
    fecha_compra TEXT NOT NULL,
    cod_prov INTEGER NOT NULL,
    FOREIGN KEY (id_pro) REFERENCES producto (id_pro),
    FOREIGN KEY (cod_prov) REFERENCES proveedores (cod_prov)
    )
    """
    )
    conn.commit()
    conn.close()
   
init_db()
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user_id' not in session:
            return redirect("/login")
        return f(*args,**kwargs)
    return decorated_function


@app.route("/")
def index():
    # lo que mostrara primero
    # return render_template('auth/login.html')
    return render_template('index.html')
@app.route ("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        nombre_usuario=request.form['nombre_usuario']
        rol=request.form['rol']
        usuario=request.form['usuario']
        password=request.form['password']
        # encriptar el password
        password_encriptado= generate_password_hash(password)
        #almacenar en la bd
        conn=sqlite3.connect("sistema_farmacia.db")
        cursor=conn.cursor()
        cursor.execute("INSERT INTO usuario (nombre_usuario,rol,usuario,password)VALUES(?,?,?,?)",
                       (nombre_usuario,rol,usuario,password_encriptado))
        conn.commit()
        conn.close()
        return redirect("/usuarios")
    return render_template("auth/register.html")
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method=='POST':
        usuario=request.form['usuario']
        password=request.form['password']

        conn=sqlite3.connect("sistema_farmacia.db")
        # permite tener registros como diccionario
        conn.row_factory=sqlite3.Row
        cursor=conn.cursor()
        cursor.execute("SELECT* FROM usuario WHERE usuario=?",(usuario,))
        usuario=cursor.fetchone()


        if usuario and check_password_hash(usuario['password'],password):
            session['user_id'] = usuario['id']
            return redirect('/admin/dashboard')
    return render_template('auth/login.html')
# para mostrarla lista de usuarios
@app.route("/usuarios")
def usuarios():
    conn=sqlite3.connect("sistema_farmacia.db")
    #permite manejar los registros como diccionarios
    conn.row_factory=sqlite3.Row

    cursor=conn.cursor()
    cursor.execute("select * from usuario")
    #para recuperar los registros guardar dentro de la variable productos
    usuarios=cursor.fetchall()
    #para mostrar
    return render_template("auth/listar_usuarios.html",usuarios=usuarios)
# editar
@app.route("/usuarios/editar/<int:id>")
def editar(id):
    conn=sqlite3.connect("sistema_farmacia.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    cursor.execute("select * from usuario where id=?",(id,))
    # para obtener el registro  se usa fetchone  para un solo registro y lo guardamos en la variable 
    # producto
    usuario= cursor.fetchone()
    conn.close()
    # luego aqui enviar a ese formulario de editar.html para recuperar los datos
    return render_template("/auth/editar_usuario.html",usuario=usuario)
#  aqui crear otra funcion para guardar los datos de editar
@app.route("/usuarios/actualizar",methods=['POST'])
def actualizar():
    id=request.form['id']
    nombre_usuario=request.form['nombre_usuario']
    rol=request.form['rol']
    usuario=request.form['usuario']
    password=request.form['password']
    password_encriptado= generate_password_hash(password)
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("UPDATE usuario set nombre_usuario=?,rol=?,usuario=?,password=? where id=?",(nombre_usuario,rol,usuario,password_encriptado,id))
    conn.commit()
    conn.close()
    return redirect ("/usuarios")

# eliminar
@app.route("/usuarios/eliminar/<int:id>")
def eliminar(id):
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("delete from usuario where id=?",(id,))
    conn.commit()
    conn.close()
    return redirect('/usuarios')
@app.route("/logout")
def logout():
    session.pop('user_id',None)

    return redirect("/")
    
@app.route("/admin/dashboard")
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

# CODIGO DE CLIENTES
@app.route("/clientes")
def clientes():
    conn=sqlite3.connect("sistema_farmacia.db")
    #permite manejar los registros como diccionarios
    conn.row_factory=sqlite3.Row

    cursor=conn.cursor()
    cursor.execute("select * from cliente")
    #para recuperar los registros guardar dentro de la variable productos
    clientes=cursor.fetchall()
    #para mostrar
    return render_template("clientes/listar_clientes.html",clientes=clientes)

@app.route("/clientes/nuevo")
def nuevo():
    return render_template('/clientes/nuevo.html')
# funcion para guardar los datos del formulario
@app.route("/clientes/nuevo/guardar",methods=['POST'])
def guardar():
    nombre=request.form['nombre']
    apellido=request.form['apellido']
    telefono=request.form['telefono']

    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()

    cursor.execute("INSERT INTO cliente (nombre,apellido,telefono)VALUES(?,?,?)",(nombre,apellido,telefono))
    conn.commit()
    conn.close()
    return redirect('/clientes')

# editar
@app.route("/clientes/editar/<int:cod_cli>")
def editar_cliente(cod_cli):
    conn=sqlite3.connect("sistema_farmacia.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    cursor.execute("select * from cliente where cod_cli=?",(cod_cli,))
    # para obtener el registro  se usa fetchone  para un solo registro y lo guardamos en la variable 
    # producto
    cliente= cursor.fetchone()
    conn.close()
    # luego aqui enviar a ese formulario de editar.html para recuperar los datos
    return render_template("/clientes/editar_cliente.html",cliente=cliente)
#  aqui crear otra funcion para guardar los datos de editar
@app.route("/clientes/actualizar",methods=['POST'])
def actualizar_cliente():
    cod_cli=request.form['cod_cli']
    nombre=request.form['nombre']
    apellido=request.form['apellido']
    telefono=request.form['telefono']
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("UPDATE cliente set nombre=?,apellido=?,telefono=? where cod_cli=?",(nombre,apellido,telefono,cod_cli))
    conn.commit()
    conn.close()
    return redirect ("/clientes")

#eliminar
@app.route("/clientes/eliminar/<int:cod_cli>")
def eliminar_cliente (cod_cli):
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("delete from cliente where cod_cli=?",(cod_cli,))
    conn.commit()
    conn.close()
    return redirect('/clientes')

# CODIGO DE VENTAS
@app.route("/ventas")
def ventas():
    conn=sqlite3.connect("sistema_farmacia.db")
    #permite manejar los registros como diccionarios
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    cursor.execute("select venta.cod_ven, venta.fecha_ven, producto.nombre_pro,venta.precio,venta.cantidad, cliente.nombre || ' ' || cliente.apellido AS nombre_completo_cliente FROM venta JOIN cliente ON venta.cod_cli = cliente.cod_cli JOIN producto ON venta.id_pro = producto.id_pro")
    #para recuperar los registros guardar dentro de la variable productos
    ventas=cursor.fetchall()
     # Calcular la suma total de la columna "Precio Total"
    cursor.execute('''
        SELECT SUM(venta.precio * venta.cantidad) AS suma_total
        FROM venta
    ''')
    suma_total = cursor.fetchone()[0] or 0

    conn.close()
    return render_template('ventas/listar_ventas.html', ventas=ventas, suma_total=suma_total)

    #para mostrar
    # return render_template("ventas/listar_ventas.html",ventas=ventas)

@app.route("/ventas/nuevo", methods=['GET', 'POST'])
def nueva_venta():
    conn = sqlite3.connect('sistema_farmacia.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener los datos de la tabla relacion clientes
    cursor.execute('SELECT cod_cli, nombre, apellido FROM cliente')
    clientes = cursor.fetchall()
     # Obtener los datos de la tabla relacion productos
    cursor.execute('SELECT id_pro, nombre_pro,precio_de_venta ,cod_cate FROM producto')
    productos = cursor.fetchall()
      # Obtener los datos de la tabla relacion categoria
    cursor.execute('SELECT cod_cate, nombre_cate FROM categoria')
    categorias = cursor.fetchall()
    

    if request.method == 'POST':
        fecha_ven=request.form['fecha_ven']
        id_pro=request.form['id_pro']
        precio=request.form['precio']
        cantidad=int(request.form['cantidad'])
        cod_cli=request.form['cod_cli']
        fecha_ven=datetime.now().strftime('%Y-%m-%d %H:%M')
         # Verificar la cantidad disponible del producto
        cursor.execute("SELECT cantidad FROM producto WHERE id_pro = ?", (id_pro,))
        producto = cursor.fetchone()
        cantidad_disponible = producto['cantidad']
        
        if cantidad > cantidad_disponible:
            flash('Producto agotado o cantidad insuficiente.', 'danger')
            conn.close()
            return redirect(url_for('nueva_venta'))

        cursor.execute("INSERT INTO venta (fecha_ven,id_pro,precio,cantidad,cod_cli )VALUES(?,?,?,?,?)",(fecha_ven,id_pro,precio,cantidad,cod_cli))
        # Actualizar la cantidad del producto 
        cursor.execute("UPDATE producto SET cantidad = cantidad - ? WHERE id_pro = ?", (cantidad, id_pro))
        conn.commit()
        conn.close()
        return redirect(url_for('ventas'))
    return render_template('/ventas/nueva_venta.html',clientes=clientes,productos=productos,categorias=categorias)
# ------------------------------------------------
# editar
@app.route("/ventas/editar/<int:cod_ven>")
def editar_venta(cod_ven):
    conn=sqlite3.connect("sistema_farmacia.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    # Obtener los datos de la tabla relacion clientes
    cursor.execute('SELECT cod_cli, nombre, apellido FROM cliente')
    clientes = cursor.fetchall()
    # Obtener los datos de la tabla relacion productos
    cursor.execute('SELECT id_pro, nombre_pro,precio_de_venta ,cod_cate FROM producto')
    productos = cursor.fetchall()
      # Obtener los datos de la tabla relacion categoria
    cursor.execute('SELECT cod_cate, nombre_cate FROM categoria')
    categorias = cursor.fetchall()
    cursor.execute("select * from venta where cod_ven=?",(cod_ven,))
    # para obtener el registro  se usa fetchone  para un solo registro y lo guardamos en la variable 
    # producto
    venta= cursor.fetchone()
    conn.close()
    # luego aqui enviar a ese formulario de editar.html para recuperar los datos
    return render_template("/ventas/editar_venta.html",venta=venta,productos=productos,clientes=clientes,categorias=categorias)
#  aqui crear otra funcion para guardar los datos de editar
@app.route("/ventas/actualizar",methods=['POST'])
def actualizar_venta():
    cod_ven=request.form['cod_ven']
    fecha_ven=request.form['fecha_ven']
    id_pro=request.form['id_pro']
    precio=request.form['precio']
    cantidad=request.form['cantidad']
    cod_cli=request.form['cod_cli']
    fecha_ven=datetime.now().strftime('%Y-%m-%d %H:%M')
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("UPDATE venta set fecha_ven=?,id_pro=?,precio=?,cantidad=?,cod_cli=? where cod_ven=?",(fecha_ven,id_pro,precio,cantidad,cod_cli,cod_ven))
    conn.commit()
    conn.close()
    return redirect ("/ventas")


#eliminar
@app.route("/ventas/eliminar/<int:cod_ven>")
def eliminar_venta (cod_ven):
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("delete from venta where cod_ven=?",(cod_ven,))
    conn.commit()
   # Verificar si la tabla está vacía y reiniciar el AUTOINCREMENT
    cursor.execute('SELECT COUNT(*) FROM venta')
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="venta"')
        conn.commit()

    cursor.execute('''
        SELECT SUM(venta.precio * venta.cantidad) AS suma_total
        FROM venta
    ''')
    suma_total = cursor.fetchone()[0] or 0


    conn.close()
    return redirect('/ventas')

@app.route('/ventas/pdf')
def generar_reporte_ventas():
    conn = sqlite3.connect("sistema_farmacia.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT venta.cod_ven, venta.fecha_ven, producto.nombre_pro, venta.precio, venta.cantidad, cliente.nombre || ' ' || cliente.apellido AS nombre_completo_cliente
        FROM venta
        JOIN cliente ON venta.cod_cli = cliente.cod_cli
        JOIN producto ON venta.id_pro = producto.id_pro
        GROUP BY venta.cod_ven
    """)
    
    ventas = cursor.fetchall()

    cursor.execute("SELECT SUM(venta.precio * venta.cantidad) AS suma_total FROM venta")
    suma_total = cursor.fetchone()[0] or 0

    conn.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(letter))
    pdf.setTitle("Reporte de Ventas")
    pdf.setFont("Helvetica", 12)

    pdf.drawString(30, 565, "FARMACIA EL BUEN DOCTOR")
    pdf.drawString(30, 550, "Reporte de Ventas")
    pdf.drawString(30, 535, "Fecha: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    pdf.drawString(30, 520, "------------------------------------------------------------------------------------------------------------------------------------------------")
    
    y_position = 500

    # Añadir encabezados de columna
    pdf.drawString(30, y_position, "ID")
    pdf.drawString(100, y_position, "Fecha")
    pdf.drawString(200, y_position, "Producto")
    pdf.drawString(310, y_position, "Precio")
    pdf.drawString(380, y_position, "Cantidad")
    pdf.drawString(470, y_position, "Cliente")
    pdf.drawString(600, y_position, "Total")
   
    y_position -= 20
   

    for venta in ventas:
        if y_position < 40:
            pdf.showPage()
            pdf.setFont("Helvetica", 8)
            y_position = 500
            
        pdf.drawString(30, y_position, str(venta['cod_ven']))
        pdf.drawString(90, y_position, venta['fecha_ven'])
        pdf.drawString(200, y_position, venta['nombre_pro'])
        pdf.drawString(320, y_position, str(venta['precio']))
        pdf.drawString(398, y_position, str(venta['cantidad']))
        pdf.drawString(450, y_position, venta['nombre_completo_cliente'])
        pdf.drawString(610, y_position, str(venta['precio'] * venta['cantidad']))
        y_position -= 20

    # Añadir el total en la parte inferior
    if y_position < 60:
        pdf.showPage()
        pdf.setFont("Helvetica", 8)
        y_position = 500
    pdf.drawString(30, y_position, "------------------------------------------------------------------------------------------------------------------------------------------------")
    y_position -= 20
    pdf.drawString(500, y_position, "Total: ")
    pdf.drawString(610, y_position, str(suma_total))

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='reporte_ventas.pdf', mimetype='application/pdf')


# CODIGO PROVEEDORES
@app.route("/proveedores")
def proveedores():
    conn=sqlite3.connect("sistema_farmacia.db")
    #permite manejar los registros como diccionarios
    conn.row_factory=sqlite3.Row

    cursor=conn.cursor()
    cursor.execute("select * from proveedores")
    #para recuperar los registros guardar dentro de la variable productos
    proveedores=cursor.fetchall()
    #para mostrar
    return render_template("proveedores/listar_proveedores.html",proveedores=proveedores)

@app.route("/proveedores/nuevo")
def nuevo_proveedor():
    return render_template('/proveedores/nuevo_proveedor.html')
# funcion para guardar los datos del formulario
@app.route("/proveedores/nuevo/guardar",methods=['POST'])
def guardar_proveedor():
    nombre_prov=request.form['nombre_prov']
    telefono_prov=request.form['telefono_prov']
    direccion=request.form['direccion']

    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()

    cursor.execute("INSERT INTO proveedores (nombre_prov,telefono_prov,direccion)VALUES(?,?,?)",(nombre_prov,telefono_prov,direccion))
    conn.commit()
    conn.close()
    return redirect('/proveedores')
# editar
@app.route("/proveedores/editar/<int:cod_prov>")
def editar_proveedor(cod_prov):
    conn=sqlite3.connect("sistema_farmacia.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    cursor.execute("select * from proveedores where cod_prov=?",(cod_prov,))
    # para obtener el registro  se usa fetchone  para un solo registro y lo guardamos en la variable 
    # producto
    proveedor= cursor.fetchone()
    conn.close()
    # luego aqui enviar a ese formulario de editar.html para recuperar los datos
    return render_template("/proveedores/editar_proveedor.html",proveedor=proveedor)
#  aqui crear otra funcion para guardar los datos de editar
@app.route("/proveedores/actualizar",methods=['POST'])
def actualizar_proveedor():
    cod_prov=request.form['cod_prov']
    nombre_prov=request.form['nombre_prov']
    telefono_prov=request.form['telefono_prov']
    direccion=request.form['direccion']
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("UPDATE proveedores set nombre_prov=?,telefono_prov=?,direccion=? where cod_prov=?",(nombre_prov,telefono_prov,direccion,cod_prov))
    conn.commit()
    conn.close()
    return redirect ("/proveedores")

#eliminar
@app.route("/proveedores/eliminar/<int:cod_prov>")
def eliminar_proveedor (cod_prov):
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("delete from proveedores where cod_prov=?",(cod_prov,))
    conn.commit()
    conn.close()
    return redirect('/proveedores')

#CODIGO CATEGORIA
@app.route("/categorias")
def categorias():
    conn=sqlite3.connect("sistema_farmacia.db")
    #permite manejar los registros como diccionarios
    conn.row_factory=sqlite3.Row

    cursor=conn.cursor()
    cursor.execute("select categoria.cod_cate, categoria.nombre_cate,proveedores.nombre_prov AS nombre_proveedor FROM categoria JOIN proveedores ON categoria.cod_prov = proveedores.cod_prov")
    #para recuperar los registros guardar dentro de la variable productos
    categorias=cursor.fetchall()
    return render_template("categorias/listar_categorias.html",categorias=categorias)
@app.route("/categorias/nuevo", methods=['GET', 'POST'])
def nueva_categoria():
    conn = sqlite3.connect('sistema_farmacia.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
     # Obtener los datos de la tabla proveedor
    cursor.execute('SELECT cod_prov, nombre_prov FROM proveedores')
    proveedores = cursor.fetchall()

    if request.method == 'POST':
        nombre_cate=request.form['nombre_cate']
        cod_prov=request.form['cod_prov']

        cursor.execute("INSERT INTO categoria (nombre_cate,cod_prov)VALUES(?,?)",(nombre_cate,cod_prov))
        conn.commit()
        conn.close()
        return redirect(url_for('categorias'))
    return render_template('/categorias/nueva_categoria.html',proveedores=proveedores)

# editar
@app.route("/categorias/editar/<int:cod_cate>")
def editar_categoria(cod_cate):
    conn=sqlite3.connect("sistema_farmacia.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
      # Obtener los datos de la tabla proveedor
    cursor.execute('SELECT cod_prov, nombre_prov FROM proveedores')
    proveedores = cursor.fetchall()
    cursor.execute("select * from categoria where cod_cate=?",(cod_cate,))
    # para obtener el registro  se usa fetchone  para un solo registro y lo guardamos en la variable 
    # categoria
    categoria= cursor.fetchone()
    conn.close()
    # luego aqui enviar a ese formulario de editar.html para recuperar los datos
    return render_template("/categorias/editar_categoria.html",categoria=categoria,proveedores=proveedores)
#  aqui crear otra funcion para guardar los datos de editar
@app.route("/categorias/actualizar",methods=['POST'])
def actualizar_categoria():
    cod_cate=request.form['cod_cate']
    nombre_cate=request.form['nombre_cate']
    cod_prov=request.form['cod_prov']
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("UPDATE categoria set nombre_cate=?,cod_prov=? where cod_cate=?",(nombre_cate,cod_prov,cod_cate))
    conn.commit()
    conn.close()
    return redirect ("/categorias")
#eliminar
@app.route("/categorias/eliminar/<int:cod_cate>")
def eliminar_categoria (cod_cate):
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("delete from categoria where cod_cate=?",(cod_cate,))
    conn.commit()
    conn.close()
    return redirect('/categorias')
#CODIGO PRODUCTO

@app.route("/productos")
def productos():
    conn=sqlite3.connect("sistema_farmacia.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
   
    cursor.execute('''
        SELECT producto.id_pro, producto.cod_pro, producto.nombre_pro, producto.precio_unitario, 
               producto.precio_de_venta, producto.fecha_caducidad, producto.cantidad, 
               producto.descripcion, categoria.nombre_cate AS nombre_categoria 
        FROM producto 
        JOIN categoria ON producto.cod_cate = categoria.cod_cate
    ''')
    productos=cursor.fetchall()
    return render_template("productos/listar_productos.html", productos=productos)

@app.route("/productos/nuevo", methods=['GET', 'POST'])
def nuevo_producto():
    conn = sqlite3.connect('sistema_farmacia.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener los datos de la tabla categoria
    cursor.execute('SELECT cod_cate, nombre_cate FROM categoria')
    categorias = cursor.fetchall()

    if request.method == 'POST':
        cod_pro = request.form['cod_pro']
        nombre_pro = request.form['nombre_pro']
        precio_unitario = request.form['precio_unitario']
        precio_de_venta = request.form['precio_de_venta']
        fecha_caducidad = request.form['fecha_caducidad']
        cantidad = request.form['cantidad']
        descripcion = request.form['descripcion']
        cod_cate = request.form['cod_cate']

        cursor.execute('''
            INSERT INTO producto (cod_pro, nombre_pro, precio_unitario, precio_de_venta, 
                                  fecha_caducidad, cantidad, descripcion, cod_cate) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cod_pro, nombre_pro, precio_unitario, precio_de_venta, fecha_caducidad, cantidad, descripcion, cod_cate))
        
        conn.commit()
        conn.close()
        flash('Producto agregado exitosamente.', 'success')
        return redirect(url_for('productos'))
    

    return render_template('productos/nuevo_producto.html', categorias=categorias)
# editar
@app.route("/productos/editar/<int:id_pro>")
def editar_producto(id_pro):
    conn=sqlite3.connect("sistema_farmacia.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
      # Obtener los datos de la tabla categoria
    cursor.execute('SELECT cod_cate, nombre_cate FROM categoria')
    categorias = cursor.fetchall()

    cursor.execute("select * from producto where id_pro=?",(id_pro,))
    # para obtener el registro  se usa fetchone  para un solo registro y lo guardamos en la variable 
    # categoria
    producto= cursor.fetchone()
    conn.close()
    # luego aqui enviar a ese formulario de editar.html para recuperar los datos
    return render_template("/productos/editar_producto.html",producto=producto,categorias=categorias)
#  aqui crear otra funcion para guardar los datos de editar
@app.route("/productos/actualizar",methods=['POST'])
def actualizar_producto():
    id_pro = request.form['id_pro']
    cod_pro = request.form['cod_pro']
    nombre_pro = request.form['nombre_pro']
    precio_unitario = request.form['precio_unitario']
    precio_de_venta = request.form['precio_de_venta']
    fecha_caducidad = request.form['fecha_caducidad']
    cantidad = request.form['cantidad']
    descripcion = request.form['descripcion']
    cod_cate = request.form['cod_cate']

    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("UPDATE producto set cod_pro=?,nombre_pro=?,precio_unitario=?,precio_de_venta=?,fecha_caducidad=?,cantidad=?,descripcion=?,cod_cate=? where id_pro=?",(cod_pro,nombre_pro,precio_unitario,precio_de_venta,fecha_caducidad,cantidad,descripcion,cod_cate,id_pro))
    conn.commit()
    conn.close()
    return redirect ("/productos")
#eliminar
@app.route("/productos/eliminar/<int:id_pro>")
def eliminar_producto (id_pro):
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("delete from producto where id_pro=?",(id_pro,))
    conn.commit()
    conn.close()
    return redirect('/productos')
# <-----------------------------------------------------CÓDIGO COMPRAS---------------------------------------------------------------->
@app.route("/compras")
def compras():
    conn = sqlite3.connect("sistema_farmacia.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Ajustar la consulta para evitar duplicación
    cursor.execute("""
        SELECT compra.cod_com, producto.nombre_pro, producto.precio_unitario, compra.stock, compra.cantidad_unidad, compra.cantidad_caja, compra.precio_caja, compra.fecha_compra, proveedores.nombre_prov, categoria.nombre_cate
        FROM compra
        JOIN producto ON compra.id_pro = producto.id_pro
        JOIN proveedores ON compra.cod_prov = proveedores.cod_prov
        LEFT JOIN categoria ON producto.cod_cate = categoria.cod_cate
        GROUP BY compra.cod_com
    """)
    
    compras = cursor.fetchall()
    
    cursor.execute("SELECT SUM(compra.precio_caja * compra.cantidad_caja) AS suma_total FROM compra")
    suma_total = cursor.fetchone()[0] or 0

    conn.close()
    return render_template('compras/listar_compras.html', compras=compras, suma_total=suma_total)

@app.route("/compras/nuevo", methods=['GET', 'POST'])
def nueva_compra():
    conn = sqlite3.connect('sistema_farmacia.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener los datos de la tabla relacion producto
    cursor.execute('SELECT id_pro, nombre_pro, precio_unitario,cod_cate FROM producto')
    productos = cursor.fetchall()
     # Obtener los datos de la tabla relacion proveedores
    cursor.execute('SELECT cod_prov, nombre_prov FROM proveedores')
    proveedores = cursor.fetchall()
     # Obtener los datos de la tabla relacion categoria
    cursor.execute('SELECT cod_cate, nombre_cate,cod_prov FROM categoria')
    categorias = cursor.fetchall()
    
    if request.method == 'POST':
        id_pro=request.form['id_pro']
        stock=int(request.form['stock'])
        cantidad_unidad=int(request.form['cantidad_unidad'])
        cantidad_caja=int(request.form['cantidad_caja'])
        precio_caja=float(request.form['precio_caja'])
        fecha_compra=datetime.now().strftime('%Y-%m-%d %H:%M')
        cod_prov=request.form['cod_prov']
    

        cursor.execute("INSERT INTO compra (id_pro,stock,cantidad_unidad,cantidad_caja,precio_caja,fecha_compra,cod_prov )VALUES(?,?,?,?,?,?,?)",(id_pro,stock,cantidad_unidad,cantidad_caja,precio_caja,fecha_compra,cod_prov))
        # Actualizar la cantidad del producto 
        cursor.execute("UPDATE producto SET cantidad = cantidad + ? WHERE id_pro = ?", (stock, id_pro))
        conn.commit()
        conn.close()
        return redirect(url_for('compras'))
    return render_template('/compras/nueva_compra.html',proveedores=proveedores,productos=productos,categorias=categorias)
# editar
@app.route("/compras/editar/<int:cod_com>")
def editar_compra(cod_com):
    conn=sqlite3.connect("sistema_farmacia.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
   # Obtener los datos de la tabla relacion producto
    cursor.execute('SELECT id_pro, nombre_pro, precio_unitario,cod_cate FROM producto')
    productos = cursor.fetchall()
     # Obtener los datos de la tabla relacion proveedores
    cursor.execute('SELECT cod_prov, nombre_prov FROM proveedores')
    proveedores = cursor.fetchall()
     # Obtener los datos de la tabla relacion categoria
    cursor.execute('SELECT cod_cate, nombre_cate,cod_prov FROM categoria')
    categorias = cursor.fetchall()
    cursor.execute("select * from compra where cod_com=?",(cod_com,))
    # para obtener el registro  se usa fetchone  para un solo registro y lo guardamos en la variable 
    # producto
    compra= cursor.fetchone()
    conn.close()
    # luego aqui enviar a ese formulario de editar.html para recuperar los datos
    return render_template("/compras/editar_compra.html",compra=compra,productos=productos,proveedores=proveedores,categorias=categorias)
#  aqui crear otra funcion para guardar los datos de editar
@app.route("/compras/actualizar",methods=['POST'])
def actualizar_compra():
    cod_com=request.form['cod_com']
    id_pro=request.form['id_pro']
    stock=int(request.form['stock'])
    cantidad_unidad=int(request.form['cantidad_unidad'])
    cantidad_caja=int(request.form['cantidad_caja'])
    precio_caja=float(request.form['precio_caja'])
    fecha_compra=datetime.now().strftime('%Y-%m-%d %H:%M')
    cod_prov=request.form['cod_prov']
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("UPDATE compra set id_pro=?,stock=?,cantidad_unidad=?,cantidad_caja=?,precio_caja=? ,fecha_compra=?,cod_prov=? where cod_com=?",(id_pro,stock,cantidad_unidad,cantidad_caja,precio_caja,fecha_compra,cod_prov,cod_com))
    conn.commit()
    conn.close()
    return redirect ("/compras")


#eliminar
@app.route("/compras/eliminar/<int:cod_com>")
def eliminar_compra (cod_com):
    conn=sqlite3.connect("sistema_farmacia.db")
    cursor=conn.cursor()
    cursor.execute("delete from compra where cod_com=?",(cod_com,))
    conn.commit()
      # Verificar si la tabla está vacía y reiniciar el AUTOINCREMENT
    cursor.execute('SELECT COUNT(*) FROM compra')
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="compra"')
        conn.commit()

    cursor.execute('''
        SELECT SUM(compra.precio_caja * compra.cantidad_caja) AS suma_total
        FROM compra
    ''')
    suma_total = cursor.fetchone()[0] or 0
    conn.close()
    return redirect('/compras')

@app.route('/compras/pdf')
def generar_reporte_compras():
    conn = sqlite3.connect("sistema_farmacia.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT compra.cod_com, producto.nombre_pro, producto.precio_unitario, compra.stock, compra.cantidad_unidad, compra.cantidad_caja, compra.precio_caja, compra.fecha_compra, proveedores.nombre_prov, categoria.nombre_cate
        FROM compra
        JOIN producto ON compra.id_pro = producto.id_pro
        JOIN proveedores ON compra.cod_prov = proveedores.cod_prov
        LEFT JOIN categoria ON producto.cod_cate = categoria.cod_cate
        GROUP BY compra.cod_com
    """)
    
    compras = cursor.fetchall()
    
    cursor.execute("SELECT SUM(compra.precio_caja * compra.cantidad_caja) AS suma_total FROM compra")
    suma_total = cursor.fetchone()[0] or 0

    conn.close()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(letter))
    pdf.setTitle("Reporte de Compras")
    pdf.setFont("Helvetica", 8)

    pdf.drawString(30, 565, "FARMACIA EL BUEN DOCTOR")
    pdf.drawString(30, 550, "Reporte de Compras")
    pdf.drawString(30, 535, "Fecha: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    pdf.drawString(30, 520, "------------------------------------------------------------")
    
    y_position = 500

    # Añadir encabezados de columna
    pdf.drawString(30, y_position, "ID")
    pdf.drawString(50, y_position, "Categoría")
    pdf.drawString(170, y_position, "Producto")
    pdf.drawString(255, y_position, "Stock")
    pdf.drawString(305, y_position, "P. Unitario")
    pdf.drawString(380, y_position, "C. Unidad")
    pdf.drawString(425, y_position, "C. Caja")
    pdf.drawString(500, y_position, "P. Caja")
    pdf.drawString(565, y_position, "Fecha")
    pdf.drawString(650, y_position, "Proveedor")
    pdf.drawString(725, y_position, "P. Total")

    y_position -= 20

    for compra in compras:
        if y_position < 40:
            pdf.showPage()
            pdf.setFont("Helvetica", 8)
            y_position = 500
            
        pdf.drawString(30, y_position, str(compra['cod_com']))
        pdf.drawString(50, y_position, compra['nombre_cate'])
        pdf.drawString(170, y_position, compra['nombre_pro'])
        pdf.drawString(255, y_position, str(compra['stock']))
        pdf.drawString(305, y_position, str(compra['precio_unitario']))
        pdf.drawString(390, y_position, str(compra['cantidad_unidad']))
        pdf.drawString(425, y_position, str(compra['cantidad_caja']))
        pdf.drawString(500, y_position, str(compra['precio_caja']))
        pdf.drawString(565, y_position, compra['fecha_compra'])
        pdf.drawString(650, y_position, compra['nombre_prov'])
        pdf.drawString(725, y_position, str(compra['precio_caja'] * compra['cantidad_caja']))
        y_position -= 20

    # Añadir la suma total en la parte inferior
    if y_position < 60:
        pdf.showPage()
        pdf.setFont("Helvetica", 8)
        y_position = 500
    
    pdf.drawString(30, y_position, "------------------------------------------------------------")
    y_position -= 20
    pdf.drawString(600, y_position, "Total: ")
    pdf.drawString(725, y_position, str(suma_total))

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='reporte_compras.pdf', mimetype='application/pdf')











   








if __name__=="__main__":
    app.run(debug=True)
