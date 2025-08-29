import flet as ft
import mysql.connector

# ----------------- CONEXIÓN MYSQL -----------------
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='1234',
            database='stock sin ia',
            ssl_disabled=True
        )
        if connection.is_connected():
            print('Conexión exitosa a MySQL')
            return connection
    except Exception as ex:
        print('Error de conexión a MySQL:', ex)
        return None

def registrar_usuario(usuario: str, contrasena: str, correo: str) -> bool:
    conexion = connect_to_db()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        consulta = "INSERT INTO usuarios (usuario, contrasena, correo_electronico) VALUES (%s, %s, %s)"
        valores = (usuario, contrasena, correo)
        cursor.execute(consulta, valores)
        conexion.commit()
        return True
    except Exception as ex:
        print('Error al registrar usuario:', ex)
        return False
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def validar_login(usuario: str, contrasena: str) -> bool:
    conexion = connect_to_db()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        consulta = "SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s"
        valores = (usuario, contrasena)
        cursor.execute(consulta, valores)
        return cursor.fetchone() is not None
    except Exception as ex:
        print('Error al validar login:', ex)
        return False
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# ----------------- VISTAS LOGIN / REGISTRO -----------------
def login_view(page: ft.Page):
    def ir_a_registro(e):
        page.go("/registro")

    def iniciar_sesion(e):
        usuario = txt_usuario_login.value
        contrasena = txt_contrasena_login.value
        if validar_login(usuario, contrasena):
            lbl_mensaje_login.value = "Login exitoso"
            lbl_mensaje_login.color = "green"
            page.update()
            page.go("/inventario")
        else:
            lbl_mensaje_login.value = "Usuario o contraseña incorrectos"
            lbl_mensaje_login.color = "red"
            page.update()

    txt_usuario_login = ft.TextField(label="Usuario", width=300)
    txt_contrasena_login = ft.TextField(label="Contraseña", password=True, width=300)
    btn_login = ft.ElevatedButton("Iniciar sesión", width=300, on_click=iniciar_sesion)
    lbl_mensaje_login = ft.Text("", color="red")
    
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Iniciar Sesión", size=20, weight="bold"),
                txt_usuario_login,
                txt_contrasena_login,
                btn_login,
                lbl_mensaje_login,
                ft.Row(
                    [
                        ft.Text("¿No tienes una cuenta?"),
                        ft.TextButton("Crear cuenta", on_click=ir_a_registro),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment="center",
            alignment="center",
            spacing=10,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )

def registro_view(page: ft.Page):
    def registrar(e):
        usuario = txt_usuario_reg.value
        contrasena = txt_contrasena_reg.value
        correo = txt_correo_reg.value
        if registrar_usuario(usuario, contrasena, correo):
            lbl_mensaje_reg.value = "Registro exitoso"
            lbl_mensaje_reg.color = "green"
            page.update()
            page.go("/")
        else:
            lbl_mensaje_reg.value = "Error al registrar"
            lbl_mensaje_reg.color = "red"
            page.update()

    def ir_a_login(e):
        page.go("/")

    txt_usuario_reg = ft.TextField(label="Usuario", width=300)
    txt_contrasena_reg = ft.TextField(label="Contraseña", password=True, width=300)
    txt_correo_reg = ft.TextField(label="Correo electrónico", width=300)
    btn_registrar = ft.ElevatedButton("Registrar", width=300, on_click=registrar)
    lbl_mensaje_reg = ft.Text("", color="red")

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Registro", size=20, weight="bold"),
                txt_usuario_reg,
                txt_contrasena_reg,
                txt_correo_reg,
                btn_registrar,
                lbl_mensaje_reg,
                ft.Row(
                    [
                        ft.Text("¿Ya tienes una cuenta?"),
                        ft.TextButton("Inicia sesión", on_click=ir_a_login),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment="center",
            alignment="center",
            spacing=10,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )

# ----------------- PANTALLA INVENTARIO (del archivo visual) -----------------
def inventario_view(page: ft.Page):
    def ir_a_agregar(e):
        page.go("/agregar_productos")
    def ir_a_eliminar(e):
        page.go("/eliminar_producto")
    def ir_a_seleccionar_producto(e):
        page.go("/seleccionar_producto")

    productos = obtener_productos("")
    filas = [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(nombre)),
                ft.DataCell(ft.Text(str(stock))),
                ft.DataCell(ft.Text(ubicacion)),
                ft.DataCell(ft.Text("Usuario")),
            ]
        )
        for (id_prod, nombre, stock, ubicacion) in productos
    ]

    Titulo = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Registro y seguimiento", size=20, weight=ft.FontWeight.BOLD),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Producto")),
                            ft.DataColumn(ft.Text("Stock")),
                            ft.DataColumn(ft.Text("Ubicación")),
                            ft.DataColumn(ft.Text("Usuario"))
                        ],
                        rows=filas,
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton("Agregar Entrada", color=ft.Colors.BLUE, on_click=ir_a_agregar),
                            ft.ElevatedButton("Agregar Salida", color=ft.Colors.BLUE, on_click=ir_a_eliminar),
                            ft.ElevatedButton("Editar Datos", color=ft.Colors.BLUE, on_click=ir_a_seleccionar_producto),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
            ),
            padding=10,
        )
    )
    # Bloque: Gestión de inventario
    Titulo_Inventario = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Gestión de inventario", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Stock de seguridad recomendado"),
                    ft.Text("100", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text("Rotación de inventario"),
                    ft.ElevatedButton("Info", color=ft.Colors.BLUE),
                ],
            ),
            padding=10,
        )
    )

    # Bloque: Predictivo de demanda
    Titulo_Demanda = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Predictivo de demanda", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("120", size=30, weight=ft.FontWeight.BOLD),
                    ft.Text("Unidades proyectadas"),
                ],
            ),
            padding=10,
        )
    )

    # Bloque: Datos
    Titulo_Datos_Aparte = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Beneficios", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([ft.Icon(ft.Icons.FACE), ft.Text("Mejor experiencia del cliente")]),
                    ft.Row([ft.Icon(ft.Icons.TRENDING_UP), ft.Text("Mayor rentabilidad")]),
                ],
            ),
            padding=10,
        )
    )

    # Bloque: Herramientas y tecnología
    herramientas = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("Herramientas y tecnología", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([ft.Icon(ft.Icons.COMPUTER), ft.Text("Sistemas ERP")]),
                    ft.Row([ft.Icon(ft.Icons.SYNC), ft.Text("Integrada en línea")]),
                    ft.Row([ft.Icon(ft.Icons.APPS), ft.Text("Aplicaciones de Mercado Libre")]),
                    ft.Row([ft.Icon(ft.Icons.SETTINGS_INPUT_COMPONENT), ft.Text("Integración con otras plataformas")]),
                ],
            ),
            padding=10,
        )
    )

    data_1 = ft.LineChartData(
        color=ft.Colors.BLUE,
        stroke_width=3,
        curved=False,
        stroke_cap_round=True,
        data_points=[
            ft.LineChartDataPoint(0, 2),   # Ene
            ft.LineChartDataPoint(1, 4),   # Feb
            ft.LineChartDataPoint(2, 3),   # Mar
            ft.LineChartDataPoint(3, 6),   # Abr
            ft.LineChartDataPoint(4, 5),   # May
            ft.LineChartDataPoint(5, 7),   # Jun
            ft.LineChartDataPoint(6, 3),   # Jul
            ft.LineChartDataPoint(7, 6),   # Ago
            ft.LineChartDataPoint(8, 4),   # Sep
            ft.LineChartDataPoint(9, 7),   # Oct
            ft.LineChartDataPoint(10, 5),  # Nov
            ft.LineChartDataPoint(11, 8),  # Dic
        ],
    )

    meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

    grafica = ft.LineChart(
        data_series=[data_1],
        border=ft.border.all(2, ft.Colors.with_opacity(0.2, ft.Colors.BLACK)),
        horizontal_grid_lines=ft.ChartGridLines(interval=1, color=ft.Colors.AMBER),
        vertical_grid_lines=ft.ChartGridLines(interval=1, color=ft.Colors.AMBER_ACCENT),
        left_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=2, label=ft.Text("20K", size=12)),
                ft.ChartAxisLabel(value=4, label=ft.Text("40K", size=12)),
                ft.ChartAxisLabel(value=6, label=ft.Text("60K", size=12)),
                ft.ChartAxisLabel(value=8, label=ft.Text("80K", size=12)),
            ],
            labels_size=40,
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=i,
                    label=ft.Container(
                        content=ft.Text(mes, size=10, color=ft.Colors.BLACK,
                                        rotate=ft.Rotate(angle=-45)),
                        margin=ft.margin.only(top=10),
                    ),
                ) for i, mes in enumerate(meses)
            ],
            labels_size=60,  # más espacio porque están rotados
        ),
        min_y=0,
        max_y=9,
        min_x=0,
        max_x=11,  # 12 meses → 0 a 11
        expand=True,
        height=400,
    )
    return ft.Column(
        [
            ft.Text("GESTION DE INVENTARIO", size=30, weight=ft.FontWeight.BOLD),
        ft.Row(
            [
                ft.Column([Titulo, Titulo_Inventario], spacing=20, expand=True),
                ft.Column([Titulo_Demanda, Titulo_Datos_Aparte, herramientas,grafica], spacing=20, expand=True),
            ],
            spacing=20,
            ),
        ],
        expand=True,
    )

def boton_agregar_productos(page: ft.Page):
    def volver_inventario(e):
        page.go("/inventario")

    def guardar_producto(e):
        nombre = txt_nombre.value
        stock = txt_stock.value
        ubicacion = txt_ubicacion.value

        if nombre and stock.isdigit():
            if agregar_producto(nombre, int(stock), ubicacion):
                lbl_mensaje.value = "Producto agregado con éxito"
                lbl_mensaje.color = "green"
                txt_nombre.value = ""
                txt_stock.value = ""
                txt_ubicacion.value = ""
            else:
                lbl_mensaje.value = "Error al agregar producto"
                lbl_mensaje.color = "red"
        else:
            lbl_mensaje.value = "Ingresa datos válidos"
            lbl_mensaje.color = "orange"

        page.update()

    txt_nombre = ft.TextField(label="Nombre del producto", width=300)
    txt_stock = ft.TextField(label="Cantidad en stock", width=300)
    txt_ubicacion = ft.TextField(label="Ubicación", width=300)
    btn_guardar = ft.ElevatedButton("Guardar", width=300, on_click=guardar_producto)
    btn_volver = ft.ElevatedButton("Volver al inventario", on_click=volver_inventario)
    lbl_mensaje = ft.Text("", color="red")

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Agregar Producto", size=25, weight="bold"),
                txt_nombre,
                txt_stock,
                txt_ubicacion,
                btn_guardar,
                btn_volver,
                lbl_mensaje,
            ],
            horizontal_alignment="center",
            alignment="center",
            spacing=10,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )
def eliminar_producto(page: ft.Page):
    def volver_inventario(e):
        page.go("/inventario")

    txt_filtro = ft.TextField(label="Buscar producto", width=300)
    lst_productos = ft.ListView(width=300, height=300)

    # Función para actualizar la lista según el filtro
    def actualizar_lista(e=None):
        lst_productos.controls.clear()
        productos = obtener_productos(txt_filtro.value)
        for id_prod, nombre_prod, stock_prod, ubicacion_prod in productos:
            
            def eliminar_producto_click(e, pid=id_prod):
                if eliminar_producto_db(pid):
                    actualizar_lista()  # 🔄 actualiza la lista después de eliminar

            btn_eliminar = ft.ElevatedButton(
                "Eliminar",
                on_click=eliminar_producto_click,
                width=100
            )
            lst_productos.controls.append(
                ft.Row([ft.Text(nombre_prod), btn_eliminar], alignment="spaceBetween")
            )
        page.update()

    txt_filtro.on_change = actualizar_lista  # actualiza al escribir
    actualizar_lista()  # llena la lista al cargar

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Eliminar Producto", size=25, weight="bold"),
                txt_filtro,
                lst_productos,
                ft.ElevatedButton("Volver al inventario", on_click=volver_inventario, width=300),
            ],
            horizontal_alignment="center",
            alignment="center",
            spacing=10,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )

def actualizar_producto(id_producto: int, nombre: str, stock: int, ubicacion: str) -> bool:
    conexion = connect_to_db()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        consulta = """
            UPDATE productos
            SET nombre = %s, stock = %s, categoria = %s
            WHERE id_producto = %s
        """
        valores = (nombre, stock, ubicacion, id_producto)
        cursor.execute(consulta, valores)
        conexion.commit()
        return True
    except Exception as ex:
        print("Error al actualizar producto:", ex)
        return False
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def modificar_producto(page: ft.Page, id_producto: int = None):
    def volver_inventario(e):
        page.go("/inventario")

    def guardar_cambios(e):
        nombre = txt_nombre.value
        stock = txt_stock.value
        ubicacion = txt_ubicacion.value
        if nombre and stock.isdigit():
            if actualizar_producto(id_producto, nombre, int(stock), ubicacion):
                lbl_mensaje.value = "Producto actualizado con éxito"
                lbl_mensaje.color = "green"
            else:
                lbl_mensaje.value = "Error al actualizar producto"
                lbl_mensaje.color = "red"
        else:
            lbl_mensaje.value = "Ingresa datos válidos"
            lbl_mensaje.color = "orange"
        page.update()

    txt_nombre = ft.TextField(label="Nombre del producto", width=300)
    txt_stock = ft.TextField(label="Cantidad en stock", width=300)
    txt_ubicacion = ft.TextField(label="Ubicación", width=300)
    btn_guardar = ft.ElevatedButton("Guardar cambios", width=300, on_click=guardar_cambios)
    btn_volver = ft.ElevatedButton("Volver al inventario", on_click=volver_inventario)
    lbl_mensaje = ft.Text("", color="red")

    if id_producto:
        conexion = connect_to_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                consulta = "SELECT nombre, stock, categoria FROM productos WHERE id_producto = %s"
                cursor.execute(consulta, (id_producto,))
                producto = cursor.fetchone()
                if producto:
                    txt_nombre.value = producto[0]
                    txt_stock.value = str(producto[1])
                    txt_ubicacion.value = producto[2]
            except Exception as ex:
                print("Error al cargar producto:", ex)
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Modificar Producto", size=25, weight="bold"),
                txt_nombre,
                txt_stock,
                txt_ubicacion,
                btn_guardar,
                btn_volver,
                lbl_mensaje,
            ],
            horizontal_alignment="center",
            alignment="center",
            spacing=10,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )

def seleccionar_producto_view(page: ft.Page):
    def volver_inventario(e):
        page.go("/inventario")

    def editar_producto(e, id_producto):
        page.go(f"/modificar_producto/{id_producto}")

    txt_filtro = ft.TextField(label="Buscar producto", width=300)
    lst_productos = ft.ListView(width=300, height=300)

    def actualizar_lista(e=None):
        lst_productos.controls.clear()
        productos = obtener_productos(txt_filtro.value)
        for id_prod, nombre_prod, _, _ in productos:
            lst_productos.controls.append(
                ft.ElevatedButton(
                    nombre_prod,
                    on_click=lambda e, pid=id_prod: editar_producto(e, pid),
                    width=200
                )
            )
        page.update()

    txt_filtro.on_change = actualizar_lista
    actualizar_lista()

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Selecciona un Producto para Editar", size=25, weight="bold"),
                txt_filtro,
                lst_productos,
                ft.ElevatedButton("Volver al Inventario", on_click=volver_inventario, width=300),
            ],
            horizontal_alignment="center",
            alignment="center",
            spacing=10,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )

def agregar_producto(nombre: str, stock: int, ubicacion: str) -> bool:
    conexion = connect_to_db()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        consulta = "INSERT INTO productos (nombre, stock, categoria) VALUES (%s, %s, %s)"
        valores = (nombre, stock, ubicacion)
        cursor.execute(consulta, valores)
        conexion.commit()
        return True
    except Exception as ex:
        print("Error al agregar producto:", ex)
        return False
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def obtener_productos(filtro=""):
    conexion = connect_to_db()
    if not conexion:
        return []
    try:
        cursor = conexion.cursor()
        consulta = "SELECT id_producto, nombre, stock, categoria FROM productos WHERE nombre LIKE %s"
        cursor.execute(consulta, ('%' + filtro + '%',))
        return cursor.fetchall()  # ahora devuelve (id, nombre, stock, categoria)
    except Exception as ex:
        print("Error al obtener productos:", ex)
        return []
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# ----------------- ELIMINAR PRODUCTO -----------------
def eliminar_producto_db(id_producto):
    conexion = connect_to_db()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        consulta = "DELETE FROM productos WHERE id_producto = %s"
        cursor.execute(consulta, (id_producto,))
        conexion.commit()
        return True
    except Exception as ex:
        print("Error al eliminar producto:", ex)
        return False
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# ----------------- MAIN APP -----------------
def main(page: ft.Page):
    page.title = "GESTION DE INVENTARIO"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    def route_change(route):
        page.views.clear()
    
        if page.route == "/":
            page.views.append(ft.View("/", [login_view(page)], padding=20))
        elif page.route == "/registro":
            page.views.append(ft.View("/registro", [registro_view(page)], padding=20))
        elif page.route == "/inventario":
            page.views.append(ft.View("/inventario", [inventario_view(page)], padding=20))
        elif page.route == "/agregar_productos":
            page.views.append(ft.View("/agregar_productos", [boton_agregar_productos(page)], padding=20))
        elif page.route == "/eliminar_producto":
            page.views.append(ft.View("/eliminar_producto", [eliminar_producto(page)], padding=20))
        elif page.route == "/seleccionar_producto":
            page.views.append(ft.View("/seleccionar_producto", [seleccionar_producto_view(page)], padding=20))
        elif page.route.startswith("/modificar_producto/"):
            id_producto = int(page.route.split("/")[-1])
            page.views.append(ft.View("/modificar_producto", [modificar_producto(page, id_producto)], padding=20))
    
        page.update()



    page.on_route_change = route_change
    page.go("/")

ft.app(target=main)