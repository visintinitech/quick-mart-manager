"""
QuickMart Manager - Sistema de Gestión para Supermercado
Versión 1.0
Desarrollado por: Dev Junior
"""

import sqlite3
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================

DB_NAME = "quickmart.db"

def conectar_bd():
    """Establece conexión con la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)

def crear_tablas():
    """Crea las tablas necesarias si no existen."""
    conn = conectar_bd()
    cursor = conn.cursor()

    # Tabla de proveedores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            direccion TEXT
        )
    ''')

    # Tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL CHECK (precio >= 0),
            stock INTEGER NOT NULL CHECK (stock >= 0),
            categoria TEXT,
            proveedor_id INTEGER,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL
        )
    ''')

    # Tabla de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            direccion TEXT
        )
    ''')

    # Tabla de ventas (cabecera)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            cliente_id INTEGER,
            total REAL NOT NULL CHECK (total >= 0),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
        )
    ''')

    # Tabla de detalle de ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
            subtotal REAL NOT NULL CHECK (subtotal >= 0),
            FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
        )
    ''')

    conn.commit()
    conn.close()

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def limpiar_pantalla():
    """Limpia la consola (funciona en Windows y Unix)."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def pausa():
    """Pausa la ejecución hasta que el usuario presione Enter."""
    input("\nPresiona Enter para continuar...")

def validar_entero_positivo(mensaje):
    """Solicita un entero positivo hasta que se ingrese correctamente."""
    while True:
        try:
            valor = int(input(mensaje))
            if valor >= 0:
                return valor
            print("El valor debe ser mayor o igual a 0.")
        except ValueError:
            print("Debes ingresar un número entero.")

def validar_flotante_positivo(mensaje):
    """Solicita un flotante positivo hasta que se ingrese correctamente."""
    while True:
        try:
            valor = float(input(mensaje))
            if valor >= 0:
                return valor
            print("El valor debe ser mayor o igual a 0.")
        except ValueError:
            print("Debes ingresar un número (puede tener decimales).")

def obtener_fecha_actual():
    """Devuelve la fecha actual en formato YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ============================================
# FUNCIONES DE GESTIÓN DE PROVEEDORES
# ============================================

def agregar_proveedor():
    """Agrega un nuevo proveedor a la base de datos."""
    print("\n--- AGREGAR NUEVO PROVEEDOR ---")
    nombre = input("Nombre: ").strip()
    if not nombre:
        print("El nombre es obligatorio.")
        return
    telefono = input("Teléfono: ").strip()
    email = input("Email: ").strip()
    direccion = input("Dirección: ").strip()

    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO proveedores (nombre, telefono, email, direccion) VALUES (?, ?, ?, ?)",
            (nombre, telefono, email, direccion)
        )
        conn.commit()
        print("✅ Proveedor agregado correctamente.")
    except sqlite3.Error as e:
        print(f"❌ Error al agregar proveedor: {e}")
    finally:
        conn.close()

def listar_proveedores():
    """Muestra todos los proveedores."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, email, direccion FROM proveedores ORDER BY nombre")
    proveedores = cursor.fetchall()
    conn.close()

    if not proveedores:
        print("No hay proveedores registrados.")
        return

    print("\n--- LISTA DE PROVEEDORES ---")
    print(f"{'ID':<4} {'Nombre':<25} {'Teléfono':<15} {'Email':<25} {'Dirección'}")
    print("-" * 80)
    for p in proveedores:
        print(f"{p[0]:<4} {p[1]:<25} {p[2]:<15} {p[3]:<25} {p[4]}")

def obtener_proveedores_para_select():
    """Devuelve una lista de proveedores (id, nombre) para usar en combos."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM proveedores ORDER BY nombre")
    resultados = cursor.fetchall()
    conn.close()
    return resultados

# ============================================
# FUNCIONES DE GESTIÓN DE CLIENTES
# ============================================

def agregar_cliente():
    """Agrega un nuevo cliente."""
    print("\n--- AGREGAR NUEVO CLIENTE ---")
    nombre = input("Nombre: ").strip()
    if not nombre:
        print("El nombre es obligatorio.")
        return
    telefono = input("Teléfono: ").strip()
    email = input("Email: ").strip()
    direccion = input("Dirección: ").strip()

    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO clientes (nombre, telefono, email, direccion) VALUES (?, ?, ?, ?)",
            (nombre, telefono, email, direccion)
        )
        conn.commit()
        print("✅ Cliente agregado correctamente.")
    except sqlite3.Error as e:
        print(f"❌ Error al agregar cliente: {e}")
    finally:
        conn.close()

def listar_clientes():
    """Muestra todos los clientes."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, email, direccion FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()
    conn.close()

    if not clientes:
        print("No hay clientes registrados.")
        return

    print("\n--- LISTA DE CLIENTES ---")
    print(f"{'ID':<4} {'Nombre':<25} {'Teléfono':<15} {'Email':<25} {'Dirección'}")
    print("-" * 80)
    for c in clientes:
        print(f"{c[0]:<4} {c[1]:<25} {c[2]:<15} {c[3]:<25} {c[4]}")

def obtener_clientes_para_select():
    """Devuelve lista de clientes (id, nombre)."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
    resultados = cursor.fetchall()
    conn.close()
    return resultados

# ============================================
# FUNCIONES DE GESTIÓN DE PRODUCTOS
# ============================================

def agregar_producto():
    """Agrega un nuevo producto."""
    print("\n--- AGREGAR NUEVO PRODUCTO ---")
    codigo = input("Código (único): ").strip()
    if not codigo:
        print("El código es obligatorio.")
        return
    nombre = input("Nombre: ").strip()
    if not nombre:
        print("El nombre es obligatorio.")
        return
    descripcion = input("Descripción: ").strip()
    precio = validar_flotante_positivo("Precio: ")
    stock = validar_entero_positivo("Stock inicial: ")
    categoria = input("Categoría: ").strip()

    # Mostrar proveedores para elegir
    proveedores = obtener_proveedores_para_select()
    if proveedores:
        print("\nProveedores disponibles:")
        for p in proveedores:
            print(f"{p[0]} - {p[1]}")
        proveedor_id = input("ID del proveedor (opcional, Enter para omitir): ").strip()
        if proveedor_id.isdigit():
            proveedor_id = int(proveedor_id)
        else:
            proveedor_id = None
    else:
        print("No hay proveedores registrados. Puedes agregar uno después.")
        proveedor_id = None

    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria, proveedor_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (codigo, nombre, descripcion, precio, stock, categoria, proveedor_id)
        )
        conn.commit()
        print("✅ Producto agregado correctamente.")
    except sqlite3.IntegrityError:
        print("❌ El código ya existe. Usa un código diferente.")
    except sqlite3.Error as e:
        print(f"❌ Error al agregar producto: {e}")
    finally:
        conn.close()

def listar_productos():
    """Muestra todos los productos con su proveedor."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.codigo, p.nombre, p.descripcion, p.precio, p.stock, p.categoria, pr.nombre
        FROM productos p
        LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
        ORDER BY p.nombre
    ''')
    productos = cursor.fetchall()
    conn.close()

    if not productos:
        print("No hay productos registrados.")
        return

    print("\n--- LISTA DE PRODUCTOS ---")
    print(f"{'ID':<4} {'Código':<10} {'Nombre':<20} {'Precio':<8} {'Stock':<6} {'Categoría':<12} {'Proveedor'}")
    print("-" * 85)
    for prod in productos:
        print(f"{prod[0]:<4} {prod[1]:<10} {prod[2]:<20} ${prod[4]:<7.2f} {prod[5]:<6} {prod[6]:<12} {prod[7] if prod[7] else 'N/A'}")

def buscar_producto():
    """Busca productos por nombre o código (coincidencia parcial)."""
    criterio = input("Ingresa nombre o código a buscar: ").strip()
    if not criterio:
        print("Debes ingresar un criterio de búsqueda.")
        return

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.codigo, p.nombre, p.precio, p.stock, p.categoria, pr.nombre
        FROM productos p
        LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
        WHERE p.nombre LIKE ? OR p.codigo LIKE ?
        ORDER BY p.nombre
    ''', (f"%{criterio}%", f"%{criterio}%"))
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("No se encontraron productos.")
        return

    print("\n--- RESULTADOS DE BÚSQUEDA ---")
    print(f"{'ID':<4} {'Código':<10} {'Nombre':<20} {'Precio':<8} {'Stock':<6} {'Categoría':<12} {'Proveedor'}")
    print("-" * 85)
    for prod in resultados:
        print(f"{prod[0]:<4} {prod[1]:<10} {prod[2]:<20} ${prod[3]:<7.2f} {prod[4]:<6} {prod[5]:<12} {prod[6] if prod[6] else 'N/A'}")

def actualizar_producto():
    """Actualiza precio y/o stock de un producto existente."""
    codigo = input("Ingresa el código del producto a actualizar: ").strip()
    if not codigo:
        print("El código es obligatorio.")
        return

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, precio, stock FROM productos WHERE codigo = ?", (codigo,))
    producto = cursor.fetchone()
    if not producto:
        print("Producto no encontrado.")
        conn.close()
        return

    print(f"\nProducto: {producto[1]} | Precio actual: ${producto[2]:.2f} | Stock actual: {producto[3]}")
    nuevo_precio = input("Nuevo precio (Enter para mantener): ").strip()
    nuevo_stock = input("Nuevo stock (Enter para mantener): ").strip()

    # Preparar actualización
    campos = []
    valores = []
    if nuevo_precio:
        try:
            precio = float(nuevo_precio)
            if precio < 0:
                print("El precio no puede ser negativo.")
                conn.close()
                return
            campos.append("precio = ?")
            valores.append(precio)
        except ValueError:
            print("Precio inválido. Se mantiene el actual.")

    if nuevo_stock:
        try:
            stock = int(nuevo_stock)
            if stock < 0:
                print("El stock no puede ser negativo.")
                conn.close()
                return
            campos.append("stock = ?")
            valores.append(stock)
        except ValueError:
            print("Stock inválido. Se mantiene el actual.")

    if not campos:
        print("No se realizaron cambios.")
        conn.close()
        return

    valores.append(producto[0])  # ID para el WHERE
    query = f"UPDATE productos SET {', '.join(campos)} WHERE id = ?"
    try:
        cursor.execute(query, valores)
        conn.commit()
        print("✅ Producto actualizado correctamente.")
    except sqlite3.Error as e:
        print(f"❌ Error al actualizar: {e}")
    finally:
        conn.close()

def eliminar_producto():
    """Elimina un producto por su código."""
    codigo = input("Ingresa el código del producto a eliminar: ").strip()
    if not codigo:
        print("El código es obligatorio.")
        return

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM productos WHERE codigo = ?", (codigo,))
    producto = cursor.fetchone()
    if not producto:
        print("Producto no encontrado.")
        conn.close()
        return

    confirmar = input(f"¿Seguro que deseas eliminar el producto '{producto[1]}'? (s/n): ").lower()
    if confirmar != 's':
        print("Operación cancelada.")
        conn.close()
        return

    try:
        cursor.execute("DELETE FROM productos WHERE id = ?", (producto[0],))
        conn.commit()
        print("✅ Producto eliminado.")
    except sqlite3.IntegrityError:
        print("❌ No se puede eliminar porque tiene ventas asociadas.")
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def reporte_stock_bajo():
    """Muestra productos con stock por debajo de un umbral."""
    umbral = validar_entero_positivo("Stock mínimo (umbral): ")

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT codigo, nombre, stock, categoria
        FROM productos
        WHERE stock < ?
        ORDER BY stock ASC
    ''', (umbral,))
    productos = cursor.fetchall()
    conn.close()

    if not productos:
        print(f"No hay productos con stock menor a {umbral}.")
        return

    print(f"\n--- PRODUCTOS CON STOCK BAJO (menor a {umbral}) ---")
    print(f"{'Código':<10} {'Nombre':<25} {'Stock':<6} {'Categoría'}")
    print("-" * 50)
    for p in productos:
        print(f"{p[0]:<10} {p[1]:<25} {p[2]:<6} {p[3]}")

# ============================================
# FUNCIONES DE VENTAS
# ============================================

def registrar_venta():
    """Registra una nueva venta con múltiples productos."""
    print("\n--- REGISTRAR NUEVA VENTA ---")

    # Seleccionar cliente
    clientes = obtener_clientes_para_select()
    if clientes:
        print("\nClientes disponibles:")
        for c in clientes:
            print(f"{c[0]} - {c[1]}")
        cliente_id = input("ID del cliente (opcional, Enter para cliente genérico): ").strip()
        if cliente_id.isdigit():
            cliente_id = int(cliente_id)
        else:
            cliente_id = None
    else:
        print("No hay clientes registrados. Se usará cliente genérico.")
        cliente_id = None

    # Variables para el carrito
    carrito = []  # lista de tuplas (producto_id, cantidad, precio_unitario, subtotal)
    total_venta = 0.0

    while True:
        print("\n--- AGREGAR PRODUCTO AL CARRITO ---")
        codigo = input("Código del producto (o 'fin' para terminar): ").strip()
        if codigo.lower() == 'fin':
            break

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, precio, stock FROM productos WHERE codigo = ?", (codigo,))
        producto = cursor.fetchone()
        conn.close()

        if not producto:
            print("❌ Producto no encontrado.")
            continue

        print(f"Producto: {producto[1]} | Precio: ${producto[2]:.2f} | Stock disponible: {producto[3]}")
        cantidad = validar_entero_positivo("Cantidad: ")
        if cantidad == 0:
            print("Cantidad debe ser mayor a 0.")
            continue
        if cantidad > producto[3]:
            print(f"❌ Stock insuficiente. Disponible: {producto[3]}")
            continue

        subtotal = producto[2] * cantidad
        total_venta += subtotal
        carrito.append((producto[0], cantidad, producto[2], subtotal))
        print(f"✅ Agregado: {producto[1]} x {cantidad} = ${subtotal:.2f}")

        # Actualizar stock en la base de datos (se hará al final para evitar inconsistencias si falla)
        # Pero lo haremos después de confirmar la venta.

    if not carrito:
        print("No se agregaron productos. Venta cancelada.")
        return

    print(f"\n--- RESUMEN DE LA VENTA ---")
    print(f"Total: ${total_venta:.2f}")
    confirmar = input("¿Confirmar venta? (s/n): ").lower()
    if confirmar != 's':
        print("Venta cancelada.")
        return

    # Guardar en BD
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        # Insertar cabecera de venta
        fecha = obtener_fecha_actual()
        cursor.execute(
            "INSERT INTO ventas (fecha, cliente_id, total) VALUES (?, ?, ?)",
            (fecha, cliente_id, total_venta)
        )
        venta_id = cursor.lastrowid

        # Insertar detalles y actualizar stock
        for prod_id, cant, precio, subtotal in carrito:
            cursor.execute(
                "INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (venta_id, prod_id, cant, precio, subtotal)
            )
            # Reducir stock
            cursor.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ? AND stock >= ?",
                (cant, prod_id, cant)
            )
            if cursor.rowcount == 0:
                # Si no se actualizó, significa que el stock cambió entre la verificación y la venta
                raise Exception(f"Stock insuficiente para el producto ID {prod_id}. Venta cancelada.")

        conn.commit()
        print(f"✅ Venta registrada con éxito. ID de venta: {venta_id} | Total: ${total_venta:.2f}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al registrar la venta: {e}")
    finally:
        conn.close()

def ver_historial_ventas():
    """Muestra todas las ventas con sus detalles."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.id, v.fecha, c.nombre, v.total
        FROM ventas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.fecha DESC
    ''')
    ventas = cursor.fetchall()
    conn.close()

    if not ventas:
        print("No hay ventas registradas.")
        return

    print("\n--- HISTORIAL DE VENTAS ---")
    for venta in ventas:
        print(f"\n📄 Venta #{venta[0]} | Fecha: {venta[1]} | Cliente: {venta[2] if venta[2] else 'Genérico'} | Total: ${venta[3]:.2f}")
        # Mostrar detalles de esta venta
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.nombre, dv.cantidad, dv.precio_unitario, dv.subtotal
            FROM detalle_venta dv
            JOIN productos p ON dv.producto_id = p.id
            WHERE dv.venta_id = ?
        ''', (venta[0],))
        detalles = cursor.fetchall()
        conn.close()
        if detalles:
            print("  Productos:")
            for det in detalles:
                print(f"    - {det[0]} x {det[1]} = ${det[2]:.2f} c/u -> subtotal ${det[3]:.2f}")

def reporte_ventas_dia():
    """Muestra el total de ventas del día actual."""
    hoy = datetime.now().strftime("%Y-%m-%d")
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(total) FROM ventas WHERE fecha LIKE ?",
        (f"{hoy}%",)
    )
    total = cursor.fetchone()[0]
    conn.close()
    if total is None:
        total = 0.0
    print(f"\n--- VENTAS DEL DÍA ({hoy}) ---")
    print(f"Total recaudado: ${total:.2f}")

# ============================================
# MENÚ PRINCIPAL
# ============================================

def mostrar_menu():
    """Muestra el menú principal."""
    limpiar_pantalla()
    print("=" * 50)
    print("   🛒 QuickMart Manager - Supermercado")
    print("=" * 50)
    print("1. Gestión de productos")
    print("2. Gestión de proveedores")
    print("3. Gestión de clientes")
    print("4. Registrar venta")
    print("5. Ver historial de ventas")
    print("6. Reporte de stock bajo")
    print("7. Reporte de ventas del día")
    print("8. Buscar producto")
    print("9. Salir")
    print("=" * 50)

def menu_productos():
    """Submenú de gestión de productos."""
    while True:
        limpiar_pantalla()
        print("\n--- GESTIÓN DE PRODUCTOS ---")
        print("1. Agregar producto")
        print("2. Listar productos")
        print("3. Actualizar producto (precio/stock)")
        print("4. Eliminar producto")
        print("5. Volver al menú principal")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            agregar_producto()
            pausa()
        elif opcion == "2":
            listar_productos()
            pausa()
        elif opcion == "3":
            actualizar_producto()
            pausa()
        elif opcion == "4":
            eliminar_producto()
            pausa()
        elif opcion == "5":
            break
        else:
            print("Opción inválida.")
            pausa()

def menu_proveedores():
    """Submenú de gestión de proveedores."""
    while True:
        limpiar_pantalla()
        print("\n--- GESTIÓN DE PROVEEDORES ---")
        print("1. Agregar proveedor")
        print("2. Listar proveedores")
        print("3. Volver al menú principal")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            agregar_proveedor()
            pausa()
        elif opcion == "2":
            listar_proveedores()
            pausa()
        elif opcion == "3":
            break
        else:
            print("Opción inválida.")
            pausa()

def menu_clientes():
    """Submenú de gestión de clientes."""
    while True:
        limpiar_pantalla()
        print("\n--- GESTIÓN DE CLIENTES ---")
        print("1. Agregar cliente")
        print("2. Listar clientes")
        print("3. Volver al menú principal")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            agregar_cliente()
            pausa()
        elif opcion == "2":
            listar_clientes()
            pausa()
        elif opcion == "3":
            break
        else:
            print("Opción inválida.")
            pausa()

def main():
    """Función principal del programa."""
    crear_tablas()  # Asegura que las tablas existan

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            menu_productos()
        elif opcion == "2":
            menu_proveedores()
        elif opcion == "3":
            menu_clientes()
        elif opcion == "4":
            registrar_venta()
            pausa()
        elif opcion == "5":
            ver_historial_ventas()
            pausa()
        elif opcion == "6":
            reporte_stock_bajo()
            pausa()
        elif opcion == "7":
            reporte_ventas_dia()
            pausa()
        elif opcion == "8":
            buscar_producto()
            pausa()
        elif opcion == "9":
            print("¡Gracias por usar QuickMart Manager! Hasta luego.")
            break
        else:
            print("Opción inválida.")
            pausa()

if __name__ == "__main__":
    main()
