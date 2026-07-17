"""
QuickMart Manager 2.0 - Sistema de Gestión para Supermercado
Completo con validaciones, descuentos, promociones, gráficos y más.
Desarrollado por: VisintiniTech
Realizado el 14 de julio y finalizado el 17 del mismo mes
"""

import sqlite3
import hashlib
import os
import shutil
import datetime
import configparser
from tkinter import *
from tkinter import ttk, messagebox, filedialog, simpledialog
import tkinter.font as tkFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import re

# ============================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================

DB_NAME = "quickmart.db"
BACKUP_DIR = "backups"
FACTURAS_DIR = "facturas"
REPORTES_DIR = "reportes"
CONFIG_FILE = "config.ini"
VERSION = "2.0"

# Crear directorios
for d in [BACKUP_DIR, FACTURAS_DIR, REPORTES_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================
# FUNCIONES DE BASE DE DATOS (CAPA DE DATOS)
# ============================================

def conectar_bd():
    return sqlite3.connect(DB_NAME)

def crear_tablas():
    conn = conectar_bd()
    c = conn.cursor()
    # Usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin','cajero'))
    )''')
    # Proveedores
    c.execute('''CREATE TABLE IF NOT EXISTS proveedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        direccion TEXT
    )''')
    # Clientes
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        direccion TEXT
    )''')
    # Promociones
    c.execute('''CREATE TABLE IF NOT EXISTS promociones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK(tipo IN ('porcentaje','2x1','cantidad')),
        valor REAL,
        fecha_inicio TEXT,
        fecha_fin TEXT,
        activa INTEGER DEFAULT 1
    )''')
    # Productos
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio REAL NOT NULL CHECK(precio>=0),
        stock INTEGER NOT NULL CHECK(stock>=0),
        categoria TEXT,
        proveedor_id INTEGER,
        descuento REAL DEFAULT 0,
        promocion_id INTEGER,
        FOREIGN KEY(proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL,
        FOREIGN KEY(promocion_id) REFERENCES promociones(id) ON DELETE SET NULL
    )''')
    # Ventas
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        cliente_id INTEGER,
        total REAL NOT NULL,
        usuario_id INTEGER,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE SET NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
    )''')
    # Detalle venta
    c.execute('''CREATE TABLE IF NOT EXISTS detalle_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        subtotal REAL NOT NULL,
        descuento_aplicado REAL DEFAULT 0,
        FOREIGN KEY(venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
        FOREIGN KEY(producto_id) REFERENCES productos(id) ON DELETE RESTRICT
    )''')
    # Compras
    c.execute('''CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        proveedor_id INTEGER,
        total REAL NOT NULL,
        usuario_id INTEGER,
        FOREIGN KEY(proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
    )''')
    # Detalle compra
    c.execute('''CREATE TABLE IF NOT EXISTS detalle_compra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compra_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        costo_unitario REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY(compra_id) REFERENCES compras(id) ON DELETE CASCADE,
        FOREIGN KEY(producto_id) REFERENCES productos(id) ON DELETE RESTRICT
    )''')
    conn.commit()
    # Insertar usuario admin por defecto
    c.execute("SELECT id FROM usuarios WHERE username='admin'")
    if not c.fetchone():
        hash_pass = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO usuarios (username, password_hash, rol) VALUES (?,?,?)",
                  ("admin", hash_pass, "admin"))
        conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_usuario(username, password):
    conn = conectar_bd()
    c = conn.cursor()
    c.execute("SELECT id, rol, password_hash FROM usuarios WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    if user and user[2] == hash_password(password):
        return user[0], user[1]
    return None, None

# ============================================
# CLASE PRINCIPAL - INTERFAZ GRÁFICA
# ============================================

class QuickMartApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"QuickMart Manager v{VERSION}")
        self.root.geometry("1300x750")
        self.usuario_id = None
        self.rol = None
        self.tema_oscuro = False
        self.cargar_configuracion()
        self.aplicar_tema()
        self.mostrar_login()

    # ---------- CONFIGURACIÓN Y TEMAS ----------
    def cargar_configuracion(self):
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
            self.tema_oscuro = config.getboolean("Interface", "dark_mode", fallback=False)
        else:
            self.tema_oscuro = False

    def guardar_configuracion(self):
        config = configparser.ConfigParser()
        config["Interface"] = {"dark_mode": str(self.tema_oscuro)}
        with open(CONFIG_FILE, "w") as f:
            config.write(f)

    def aplicar_tema(self):
        if self.tema_oscuro:
            bg = "#2b2b2b"
            fg = "#ffffff"
            self.root.configure(bg=bg)
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TFrame", background=bg)
            style.configure("TLabel", background=bg, foreground=fg)
            style.configure("TButton", background="#555", foreground=fg, borderwidth=1)
            style.map("TButton", background=[("active", "#777")])
            style.configure("TEntry", fieldbackground="#444", foreground=fg)
            style.configure("TCombobox", fieldbackground="#444", foreground=fg)
            style.configure("Treeview", background="#333", foreground=fg, fieldbackground="#333")
            style.map("Treeview", background=[("selected", "#555")])
            self.root.option_add("*Background", bg)
            self.root.option_add("*Foreground", fg)
        else:
            self.root.configure(bg="SystemButtonFace")
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TFrame", background="SystemButtonFace")
            style.configure("TLabel", background="SystemButtonFace", foreground="black")
            style.configure("TButton", background="#e1e1e1", foreground="black")
            style.map("TButton", background=[("active", "#c1c1c1")])
            style.configure("TEntry", fieldbackground="white", foreground="black")
            style.configure("TCombobox", fieldbackground="white", foreground="black")
            style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
            style.map("Treeview", background=[("selected", "#0078D7")])
            self.root.option_add("*Background", "SystemButtonFace")
            self.root.option_add("*Foreground", "black")

    def alternar_tema(self):
        self.tema_oscuro = not self.tema_oscuro
        self.guardar_configuracion()
        self.aplicar_tema()
        # Refrescar ventanas (opcional)

    # ---------- LOGIN ----------
    def mostrar_login(self):
        self.limpiar_ventana()
        frame = ttk.Frame(self.root)
        frame.pack(expand=True)
        ttk.Label(frame, text="Iniciar Sesión", font=("Arial", 24)).pack(pady=20)
        ttk.Label(frame, text="Usuario:").pack()
        self.entry_user = ttk.Entry(frame)
        self.entry_user.pack(pady=5)
        ttk.Label(frame, text="Contraseña:").pack()
        self.entry_pass = ttk.Entry(frame, show="*")
        self.entry_pass.pack(pady=5)
        ttk.Button(frame, text="Entrar", command=self.login).pack(pady=10)
        ttk.Label(frame, text="Usuario por defecto: admin / admin123", font=("Arial", 9)).pack()

    def login(self):
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "Ingresa usuario y contraseña")
            return
        uid, rol = verificar_usuario(user, pwd)
        if uid:
            self.usuario_id = uid
            self.rol = rol
            self.hacer_backup_auto()
            self.mostrar_dashboard()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    # ---------- BACKUP ----------
    def hacer_backup_auto(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_DIR, f"quickmart_{timestamp}.db")
            if os.path.exists(DB_NAME):
                shutil.copy2(DB_NAME, backup_file)
                archivos = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")])
                if len(archivos) > 10:
                    for f in archivos[:-10]:
                        os.remove(os.path.join(BACKUP_DIR, f))
        except Exception as e:
            print(f"Backup error: {e}")

    def hacer_backup_manual(self):
        if messagebox.askyesno("Backup", "¿Crear copia de seguridad ahora?"):
            self.hacer_backup_auto()
            messagebox.showinfo("Backup", "Copia de seguridad creada en 'backups'.")

    # ---------- DASHBOARD ----------
    def mostrar_dashboard(self):
        self.limpiar_ventana()
        # Menú
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        archivo_menu = Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Cerrar sesión", command=self.cerrar_sesion)
        archivo_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        herramientas_menu = Menu(menubar, tearoff=0)
        herramientas_menu.add_command(label="Backup manual", command=self.hacer_backup_manual)
        herramientas_menu.add_command(label="Alternar tema oscuro", command=self.alternar_tema)
        menubar.add_cascade(label="Herramientas", menu=herramientas_menu)

        # Notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Crear pestañas
        self.tab_productos = ttk.Frame(self.notebook)
        self.tab_proveedores = ttk.Frame(self.notebook)
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_promociones = ttk.Frame(self.notebook)
        self.tab_ventas = ttk.Frame(self.notebook)
        self.tab_compras = ttk.Frame(self.notebook)
        self.tab_reportes = ttk.Frame(self.notebook)
        self.tab_graficos = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_productos, text="Productos")
        self.notebook.add(self.tab_proveedores, text="Proveedores")
        self.notebook.add(self.tab_clientes, text="Clientes")
        self.notebook.add(self.tab_promociones, text="Promociones")
        self.notebook.add(self.tab_ventas, text="Ventas")
        self.notebook.add(self.tab_compras, text="Compras")
        self.notebook.add(self.tab_reportes, text="Reportes")
        self.notebook.add(self.tab_graficos, text="Gráficos")

        # Construir cada pestaña
        self.construir_tab_productos()
        self.construir_tab_proveedores()
        self.construir_tab_clientes()
        self.construir_tab_promociones()
        self.construir_tab_ventas()
        self.construir_tab_compras()
        self.construir_tab_reportes()
        self.construir_tab_graficos()

        # Cargar datos iniciales
        self.cargar_productos()
        self.cargar_proveedores()
        self.cargar_clientes()
        self.cargar_promociones()
        self.cargar_ventas()
        self.cargar_compras()

        # Actualizar combos de ventas y compras
        self.actualizar_combos_venta()
        self.actualizar_combos_compra()

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def cerrar_sesion(self):
        self.usuario_id = None
        self.rol = None
        self.mostrar_login()

    # ==========================================
    # PESTAÑA PRODUCTOS (CRUD + filtros)
    # ==========================================
    def construir_tab_productos(self):
        frame_filtros = ttk.Frame(self.tab_productos)
        frame_filtros.pack(fill=X, padx=5, pady=5)
        ttk.Label(frame_filtros, text="Nombre:").pack(side=LEFT, padx=2)
        self.filtro_nombre = ttk.Entry(frame_filtros, width=15)
        self.filtro_nombre.pack(side=LEFT, padx=2)
        ttk.Label(frame_filtros, text="Categoría:").pack(side=LEFT, padx=2)
        self.filtro_categoria = ttk.Entry(frame_filtros, width=15)
        self.filtro_categoria.pack(side=LEFT, padx=2)
        ttk.Label(frame_filtros, text="Precio min:").pack(side=LEFT, padx=2)
        self.filtro_precio_min = ttk.Entry(frame_filtros, width=8)
        self.filtro_precio_min.pack(side=LEFT, padx=2)
        ttk.Label(frame_filtros, text="max:").pack(side=LEFT, padx=2)
        self.filtro_precio_max = ttk.Entry(frame_filtros, width=8)
        self.filtro_precio_max.pack(side=LEFT, padx=2)
        ttk.Button(frame_filtros, text="Buscar", command=self.buscar_productos).pack(side=LEFT, padx=5)
        ttk.Button(frame_filtros, text="Limpiar", command=self.cargar_productos).pack(side=LEFT, padx=5)
        ttk.Button(frame_filtros, text="Agregar", command=self.agregar_producto).pack(side=LEFT, padx=5)
        ttk.Button(frame_filtros, text="Editar", command=self.editar_producto).pack(side=LEFT, padx=5)
        ttk.Button(frame_filtros, text="Eliminar", command=self.eliminar_producto).pack(side=LEFT, padx=5)

        # Treeview
        self.tree_productos = ttk.Treeview(self.tab_productos,
            columns=("ID","Código","Nombre","Precio","Stock","Categoría","Proveedor","Descuento","Promoción"),
            show="headings")
        for col in self.tree_productos["columns"]:
            self.tree_productos.heading(col, text=col)
            self.tree_productos.column(col, width=100)
        self.tree_productos.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def cargar_productos(self, filtro=None):
        # Limpia y carga todos los productos (o aplica filtro)
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        conn = conectar_bd()
        c = conn.cursor()
        query = '''SELECT p.id, p.codigo, p.nombre, p.precio, p.stock, p.categoria, 
                          pr.nombre, p.descuento, prom.descripcion
                   FROM productos p
                   LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                   LEFT JOIN promociones prom ON p.promocion_id = prom.id
                   WHERE 1=1 '''
        params = []
        if filtro:
            if filtro.get('nombre'):
                query += " AND p.nombre LIKE ?"
                params.append(f"%{filtro['nombre']}%")
            if filtro.get('categoria'):
                query += " AND p.categoria LIKE ?"
                params.append(f"%{filtro['categoria']}%")
            if filtro.get('precio_min') is not None:
                query += " AND p.precio >= ?"
                params.append(filtro['precio_min'])
            if filtro.get('precio_max') is not None:
                query += " AND p.precio <= ?"
                params.append(filtro['precio_max'])
            if filtro.get('stock_min') is not None:
                query += " AND p.stock >= ?"
                params.append(filtro['stock_min'])
        query += " ORDER BY p.nombre"
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        for row in rows:
            self.tree_productos.insert("", END, values=row)

    def buscar_productos(self):
        filtro = {}
        nombre = self.filtro_nombre.get().strip()
        if nombre:
            filtro['nombre'] = nombre
        categoria = self.filtro_categoria.get().strip()
        if categoria:
            filtro['categoria'] = categoria
        pmin = self.filtro_precio_min.get().strip()
        if pmin:
            try:
                filtro['precio_min'] = float(pmin)
            except:
                messagebox.showerror("Error", "Precio mínimo debe ser número")
                return
        pmax = self.filtro_precio_max.get().strip()
        if pmax:
            try:
                filtro['precio_max'] = float(pmax)
            except:
                messagebox.showerror("Error", "Precio máximo debe ser número")
                return
        self.cargar_productos(filtro)

    def agregar_producto(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores pueden agregar productos")
            return
        ventana = Toplevel(self.root)
        ventana.title("Agregar Producto")
        ventana.geometry("400x500")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)

        # Campos
        ttk.Label(frame, text="Código:*").grid(row=0, column=0, sticky=W, pady=2)
        entry_codigo = ttk.Entry(frame)
        entry_codigo.grid(row=0, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Nombre:*").grid(row=1, column=0, sticky=W, pady=2)
        entry_nombre = ttk.Entry(frame)
        entry_nombre.grid(row=1, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Descripción:").grid(row=2, column=0, sticky=W, pady=2)
        entry_desc = ttk.Entry(frame)
        entry_desc.grid(row=2, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Precio:*").grid(row=3, column=0, sticky=W, pady=2)
        entry_precio = ttk.Entry(frame)
        entry_precio.grid(row=3, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Stock:*").grid(row=4, column=0, sticky=W, pady=2)
        entry_stock = ttk.Entry(frame)
        entry_stock.grid(row=4, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Categoría:").grid(row=5, column=0, sticky=W, pady=2)
        entry_cat = ttk.Entry(frame)
        entry_cat.grid(row=5, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Proveedor:").grid(row=6, column=0, sticky=W, pady=2)
        combo_prov = ttk.Combobox(frame, state="readonly")
        combo_prov.grid(row=6, column=1, pady=2, sticky=W)
        # Cargar proveedores en combo
        provs = self.obtener_proveedores_combo()
        combo_prov['values'] = [f"{p[0]} - {p[1]}" for p in provs]
        ttk.Label(frame, text="Descuento (%):").grid(row=7, column=0, sticky=W, pady=2)
        entry_desc_pct = ttk.Entry(frame)
        entry_desc_pct.grid(row=7, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Promoción:").grid(row=8, column=0, sticky=W, pady=2)
        combo_prom = ttk.Combobox(frame, state="readonly")
        combo_prom.grid(row=8, column=1, pady=2, sticky=W)
        promos = self.obtener_promociones_combo()
        combo_prom['values'] = [f"{p[0]} - {p[1]}" for p in promos]

        def guardar():
            codigo = entry_codigo.get().strip()
            nombre = entry_nombre.get().strip()
            desc = entry_desc.get().strip()
            precio_str = entry_precio.get().strip()
            stock_str = entry_stock.get().strip()
            cat = entry_cat.get().strip()
            prov_seleccionado = combo_prov.get()
            desc_pct_str = entry_desc_pct.get().strip()
            prom_seleccionado = combo_prom.get()

            # Validaciones
            if not codigo:
                messagebox.showerror("Error", "El código es obligatorio")
                return
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            try:
                precio = float(precio_str)
                if precio < 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Precio debe ser número positivo")
                return
            try:
                stock = int(stock_str)
                if stock < 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Stock debe ser entero positivo")
                return
            desc_pct = 0.0
            if desc_pct_str:
                try:
                    desc_pct = float(desc_pct_str)
                    if desc_pct < 0 or desc_pct > 100:
                        raise ValueError
                except:
                    messagebox.showerror("Error", "Descuento debe ser 0-100")
                    return
            # Proveedor y promoción
            proveedor_id = None
            if prov_seleccionado:
                try:
                    proveedor_id = int(prov_seleccionado.split(" - ")[0])
                except:
                    pass
            promocion_id = None
            if prom_seleccionado:
                try:
                    promocion_id = int(prom_seleccionado.split(" - ")[0])
                except:
                    pass

            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO productos 
                    (codigo, nombre, descripcion, precio, stock, categoria, proveedor_id, descuento, promocion_id)
                    VALUES (?,?,?,?,?,?,?,?,?)''',
                    (codigo, nombre, desc, precio, stock, cat, proveedor_id, desc_pct, promocion_id))
                conn.commit()
                messagebox.showinfo("Éxito", "Producto agregado")
                ventana.destroy()
                self.cargar_productos()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El código ya existe")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()

        ttk.Button(frame, text="Guardar", command=guardar).grid(row=9, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=9, column=1, pady=10)

    def editar_producto(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un producto")
            return
        item = self.tree_productos.item(seleccion[0])
        valores = item['values']
        if not valores:
            return
        prod_id = valores[0]
        # Obtener datos actuales
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT * FROM productos WHERE id=?", (prod_id,))
        prod = c.fetchone()
        conn.close()
        if not prod:
            messagebox.showerror("Error", "Producto no encontrado")
            return
        # Ventana similar a agregar pero con datos precargados
        ventana = Toplevel(self.root)
        ventana.title("Editar Producto")
        ventana.geometry("400x500")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(frame, text="Código:*").grid(row=0, column=0, sticky=W, pady=2)
        entry_codigo = ttk.Entry(frame)
        entry_codigo.insert(0, prod[1])
        entry_codigo.grid(row=0, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Nombre:*").grid(row=1, column=0, sticky=W, pady=2)
        entry_nombre = ttk.Entry(frame)
        entry_nombre.insert(0, prod[2])
        entry_nombre.grid(row=1, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Descripción:").grid(row=2, column=0, sticky=W, pady=2)
        entry_desc = ttk.Entry(frame)
        entry_desc.insert(0, prod[3] or "")
        entry_desc.grid(row=2, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Precio:*").grid(row=3, column=0, sticky=W, pady=2)
        entry_precio = ttk.Entry(frame)
        entry_precio.insert(0, str(prod[4]))
        entry_precio.grid(row=3, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Stock:*").grid(row=4, column=0, sticky=W, pady=2)
        entry_stock = ttk.Entry(frame)
        entry_stock.insert(0, str(prod[5]))
        entry_stock.grid(row=4, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Categoría:").grid(row=5, column=0, sticky=W, pady=2)
        entry_cat = ttk.Entry(frame)
        entry_cat.insert(0, prod[6] or "")
        entry_cat.grid(row=5, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Proveedor:").grid(row=6, column=0, sticky=W, pady=2)
        combo_prov = ttk.Combobox(frame, state="readonly")
        combo_prov.grid(row=6, column=1, pady=2, sticky=W)
        provs = self.obtener_proveedores_combo()
        combo_prov['values'] = [f"{p[0]} - {p[1]}" for p in provs]
        if prod[7]:
            combo_prov.set(f"{prod[7]} - {self.obtener_nombre_proveedor(prod[7])}")
        ttk.Label(frame, text="Descuento (%):").grid(row=7, column=0, sticky=W, pady=2)
        entry_desc_pct = ttk.Entry(frame)
        entry_desc_pct.insert(0, str(prod[8] or 0))
        entry_desc_pct.grid(row=7, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Promoción:").grid(row=8, column=0, sticky=W, pady=2)
        combo_prom = ttk.Combobox(frame, state="readonly")
        combo_prom.grid(row=8, column=1, pady=2, sticky=W)
        promos = self.obtener_promociones_combo()
        combo_prom['values'] = [f"{p[0]} - {p[1]}" for p in promos]
        if prod[9]:
            combo_prom.set(f"{prod[9]} - {self.obtener_nombre_promocion(prod[9])}")

        def guardar():
            codigo = entry_codigo.get().strip()
            nombre = entry_nombre.get().strip()
            desc = entry_desc.get().strip()
            precio_str = entry_precio.get().strip()
            stock_str = entry_stock.get().strip()
            cat = entry_cat.get().strip()
            prov_seleccionado = combo_prov.get()
            desc_pct_str = entry_desc_pct.get().strip()
            prom_seleccionado = combo_prom.get()
            # Validaciones iguales
            if not codigo:
                messagebox.showerror("Error", "Código obligatorio")
                return
            if not nombre:
                messagebox.showerror("Error", "Nombre obligatorio")
                return
            try:
                precio = float(precio_str)
                if precio < 0: raise ValueError
            except:
                messagebox.showerror("Error", "Precio debe ser número positivo")
                return
            try:
                stock = int(stock_str)
                if stock < 0: raise ValueError
            except:
                messagebox.showerror("Error", "Stock debe ser entero positivo")
                return
            desc_pct = 0.0
            if desc_pct_str:
                try:
                    desc_pct = float(desc_pct_str)
                    if desc_pct < 0 or desc_pct > 100: raise ValueError
                except:
                    messagebox.showerror("Error", "Descuento 0-100")
                    return
            proveedor_id = None
            if prov_seleccionado:
                try:
                    proveedor_id = int(prov_seleccionado.split(" - ")[0])
                except:
                    pass
            promocion_id = None
            if prom_seleccionado:
                try:
                    promocion_id = int(prom_seleccionado.split(" - ")[0])
                except:
                    pass
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute('''UPDATE productos SET codigo=?, nombre=?, descripcion=?, precio=?, stock=?, 
                    categoria=?, proveedor_id=?, descuento=?, promocion_id=? WHERE id=?''',
                    (codigo, nombre, desc, precio, stock, cat, proveedor_id, desc_pct, promocion_id, prod_id))
                conn.commit()
                messagebox.showinfo("Éxito", "Producto actualizado")
                ventana.destroy()
                self.cargar_productos()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El código ya existe")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()

        ttk.Button(frame, text="Guardar", command=guardar).grid(row=9, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=9, column=1, pady=10)

    def eliminar_producto(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un producto")
            return
        item = self.tree_productos.item(seleccion[0])
        prod_id = item['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute("DELETE FROM productos WHERE id=?", (prod_id,))
                conn.commit()
                messagebox.showinfo("Éxito", "Producto eliminado")
                self.cargar_productos()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "No se puede eliminar porque tiene ventas asociadas")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()

    # ==========================================
    # PESTAÑA PROVEEDORES (CRUD)
    # ==========================================
    def construir_tab_proveedores(self):
        frame = ttk.Frame(self.tab_proveedores)
        frame.pack(fill=X, padx=5, pady=5)
        ttk.Button(frame, text="Agregar", command=self.agregar_proveedor).pack(side=LEFT, padx=5)
        ttk.Button(frame, text="Editar", command=self.editar_proveedor).pack(side=LEFT, padx=5)
        ttk.Button(frame, text="Eliminar", command=self.eliminar_proveedor).pack(side=LEFT, padx=5)

        self.tree_proveedores = ttk.Treeview(self.tab_proveedores,
            columns=("ID","Nombre","Teléfono","Email","Dirección"), show="headings")
        for col in self.tree_proveedores["columns"]:
            self.tree_proveedores.heading(col, text=col)
            self.tree_proveedores.column(col, width=150)
        self.tree_proveedores.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def cargar_proveedores(self):
        for item in self.tree_proveedores.get_children():
            self.tree_proveedores.delete(item)
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT id, nombre, telefono, email, direccion FROM proveedores ORDER BY nombre")
        rows = c.fetchall()
        conn.close()
        for r in rows:
            self.tree_proveedores.insert("", END, values=r)

    def obtener_proveedores_combo(self):
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM proveedores ORDER BY nombre")
        res = c.fetchall()
        conn.close()
        return res

    def obtener_nombre_proveedor(self, id_prov):
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT nombre FROM proveedores WHERE id=?", (id_prov,))
        res = c.fetchone()
        conn.close()
        return res[0] if res else ""

    def agregar_proveedor(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        ventana = Toplevel(self.root)
        ventana.title("Agregar Proveedor")
        ventana.geometry("400x300")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Nombre:*").grid(row=0, column=0, sticky=W, pady=2)
        entry_nom = ttk.Entry(frame)
        entry_nom.grid(row=0, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Teléfono:").grid(row=1, column=0, sticky=W, pady=2)
        entry_tel = ttk.Entry(frame)
        entry_tel.grid(row=1, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky=W, pady=2)
        entry_email = ttk.Entry(frame)
        entry_email.grid(row=2, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Dirección:").grid(row=3, column=0, sticky=W, pady=2)
        entry_dir = ttk.Entry(frame)
        entry_dir.grid(row=3, column=1, pady=2, sticky=W)

        def guardar():
            nombre = entry_nom.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Nombre obligatorio")
                return
            telefono = entry_tel.get().strip()
            email = entry_email.get().strip()
            direccion = entry_dir.get().strip()
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute("INSERT INTO proveedores (nombre, telefono, email, direccion) VALUES (?,?,?,?)",
                          (nombre, telefono, email, direccion))
                conn.commit()
                messagebox.showinfo("Éxito", "Proveedor agregado")
                ventana.destroy()
                self.cargar_proveedores()
                self.actualizar_combos_venta()
                self.actualizar_combos_compra()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()
        ttk.Button(frame, text="Guardar", command=guardar).grid(row=4, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=4, column=1, pady=10)

    def editar_proveedor(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        seleccion = self.tree_proveedores.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un proveedor")
            return
        item = self.tree_proveedores.item(seleccion[0])
        vals = item['values']
        if not vals: return
        prov_id = vals[0]
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT * FROM proveedores WHERE id=?", (prov_id,))
        prov = c.fetchone()
        conn.close()
        if not prov:
            messagebox.showerror("Error", "No encontrado")
            return
        ventana = Toplevel(self.root)
        ventana.title("Editar Proveedor")
        ventana.geometry("400x300")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Nombre:*").grid(row=0, column=0, sticky=W, pady=2)
        entry_nom = ttk.Entry(frame)
        entry_nom.insert(0, prov[1])
        entry_nom.grid(row=0, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Teléfono:").grid(row=1, column=0, sticky=W, pady=2)
        entry_tel = ttk.Entry(frame)
        entry_tel.insert(0, prov[2] or "")
        entry_tel.grid(row=1, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky=W, pady=2)
        entry_email = ttk.Entry(frame)
        entry_email.insert(0, prov[3] or "")
        entry_email.grid(row=2, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Dirección:").grid(row=3, column=0, sticky=W, pady=2)
        entry_dir = ttk.Entry(frame)
        entry_dir.insert(0, prov[4] or "")
        entry_dir.grid(row=3, column=1, pady=2, sticky=W)

        def guardar():
            nombre = entry_nom.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Nombre obligatorio")
                return
            telefono = entry_tel.get().strip()
            email = entry_email.get().strip()
            direccion = entry_dir.get().strip()
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute("UPDATE proveedores SET nombre=?, telefono=?, email=?, direccion=? WHERE id=?",
                          (nombre, telefono, email, direccion, prov_id))
                conn.commit()
                messagebox.showinfo("Éxito", "Proveedor actualizado")
                ventana.destroy()
                self.cargar_proveedores()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()
        ttk.Button(frame, text="Guardar", command=guardar).grid(row=4, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=4, column=1, pady=10)

    def eliminar_proveedor(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        seleccion = self.tree_proveedores.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un proveedor")
            return
        prov_id = self.tree_proveedores.item(seleccion[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar proveedor?"):
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute("DELETE FROM proveedores WHERE id=?", (prov_id,))
                conn.commit()
                messagebox.showinfo("Éxito", "Proveedor eliminado")
                self.cargar_proveedores()
                self.actualizar_combos_venta()
                self.actualizar_combos_compra()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "No se puede eliminar porque tiene productos asociados")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()

    # ==========================================
    # PESTAÑA CLIENTES (CRUD)
    # ==========================================
    def construir_tab_clientes(self):
        frame = ttk.Frame(self.tab_clientes)
        frame.pack(fill=X, padx=5, pady=5)
        ttk.Button(frame, text="Agregar", command=self.agregar_cliente).pack(side=LEFT, padx=5)
        ttk.Button(frame, text="Editar", command=self.editar_cliente).pack(side=LEFT, padx=5)
        ttk.Button(frame, text="Eliminar", command=self.eliminar_cliente).pack(side=LEFT, padx=5)

        self.tree_clientes = ttk.Treeview(self.tab_clientes,
            columns=("ID","Nombre","Teléfono","Email","Dirección"), show="headings")
        for col in self.tree_clientes["columns"]:
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=150)
        self.tree_clientes.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def cargar_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT id, nombre, telefono, email, direccion FROM clientes ORDER BY nombre")
        rows = c.fetchall()
        conn.close()
        for r in rows:
            self.tree_clientes.insert("", END, values=r)

    def obtener_clientes_combo(self):
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
        res = c.fetchall()
        conn.close()
        return res

    def agregar_cliente(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        ventana = Toplevel(self.root)
        ventana.title("Agregar Cliente")
        ventana.geometry("400x300")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Nombre:*").grid(row=0, column=0, sticky=W, pady=2)
        entry_nom = ttk.Entry(frame)
        entry_nom.grid(row=0, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Teléfono:").grid(row=1, column=0, sticky=W, pady=2)
        entry_tel = ttk.Entry(frame)
        entry_tel.grid(row=1, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky=W, pady=2)
        entry_email = ttk.Entry(frame)
        entry_email.grid(row=2, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Dirección:").grid(row=3, column=0, sticky=W, pady=2)
        entry_dir = ttk.Entry(frame)
        entry_dir.grid(row=3, column=1, pady=2, sticky=W)

        def guardar():
            nombre = entry_nom.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Nombre obligatorio")
                return
            telefono = entry_tel.get().strip()
            email = entry_email.get().strip()
            direccion = entry_dir.get().strip()
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute("INSERT INTO clientes (nombre, telefono, email, direccion) VALUES (?,?,?,?)",
                          (nombre, telefono, email, direccion))
                conn.commit()
                messagebox.showinfo("Éxito", "Cliente agregado")
                ventana.destroy()
                self.cargar_clientes()
                self.actualizar_combos_venta()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()
        ttk.Button(frame, text="Guardar", command=guardar).grid(row=4, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=4, column=1, pady=10)

    def editar_cliente(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        seleccion = self.tree_clientes.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un cliente")
            return
        item = self.tree_clientes.item(seleccion[0])
        vals = item['values']
        if not vals: return
        cli_id = vals[0]
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT * FROM clientes WHERE id=?", (cli_id,))
        cli = c.fetchone()
        conn.close()
        if not cli:
            messagebox.showerror("Error", "No encontrado")
            return
        ventana = Toplevel(self.root)
        ventana.title("Editar Cliente")
        ventana.geometry("400x300")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Nombre:*").grid(row=0, column=0, sticky=W, pady=2)
        entry_nom = ttk.Entry(frame)
        entry_nom.insert(0, cli[1])
        entry_nom.grid(row=0, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Teléfono:").grid(row=1, column=0, sticky=W, pady=2)
        entry_tel = ttk.Entry(frame)
        entry_tel.insert(0, cli[2] or "")
        entry_tel.grid(row=1, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky=W, pady=2)
        entry_email = ttk.Entry(frame)
        entry_email.insert(0, cli[3] or "")
        entry_email.grid(row=2, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Dirección:").grid(row=3, column=0, sticky=W, pady=2)
        entry_dir = ttk.Entry(frame)
        entry_dir.insert(0, cli[4] or "")
        entry_dir.grid(row=3, column=1, pady=2, sticky=W)

        def guardar():
            nombre = entry_nom.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Nombre obligatorio")
                return
            telefono = entry_tel.get().strip()
            email = entry_email.get().strip()
            direccion = entry_dir.get().strip()
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute("UPDATE clientes SET nombre=?, telefono=?, email=?, direccion=? WHERE id=?",
                          (nombre, telefono, email, direccion, cli_id))
                conn.commit()
                messagebox.showinfo("Éxito", "Cliente actualizado")
                ventana.destroy()
                self.cargar_clientes()
                self.actualizar_combos_venta()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()
        ttk.Button(frame, text="Guardar", command=guardar).grid(row=4, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=4, column=1, pady=10)

    def eliminar_cliente(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        seleccion = self.tree_clientes.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un cliente")
            return
        cli_id = self.tree_clientes.item(seleccion[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar cliente?"):
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute("DELETE FROM clientes WHERE id=?", (cli_id,))
                conn.commit()
                messagebox.showinfo("Éxito", "Cliente eliminado")
                self.cargar_clientes()
                self.actualizar_combos_venta()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "No se puede eliminar porque tiene ventas asociadas")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()

    # ==========================================
    # PESTAÑA PROMOCIONES (CRUD)
    # ==========================================
    def construir_tab_promociones(self):
        frame = ttk.Frame(self.tab_promociones)
        frame.pack(fill=X, padx=5, pady=5)
        ttk.Button(frame, text="Agregar", command=self.agregar_promocion).pack(side=LEFT, padx=5)
        ttk.Button(frame, text="Editar", command=self.editar_promocion).pack(side=LEFT, padx=5)
        ttk.Button(frame, text="Eliminar", command=self.eliminar_promocion).pack(side=LEFT, padx=5)

        self.tree_promociones = ttk.Treeview(self.tab_promociones,
            columns=("ID","Descripción","Tipo","Valor","Inicio","Fin","Activa"), show="headings")
        for col in self.tree_promociones["columns"]:
            self.tree_promociones.heading(col, text=col)
            self.tree_promociones.column(col, width=120)
        self.tree_promociones.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def cargar_promociones(self):
        for item in self.tree_promociones.get_children():
            self.tree_promociones.delete(item)
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT id, descripcion, tipo, valor, fecha_inicio, fecha_fin, activa FROM promociones ORDER BY id")
        rows = c.fetchall()
        conn.close()
        for r in rows:
            activa = "Sí" if r[6] else "No"
            self.tree_promociones.insert("", END, values=(r[0], r[1], r[2], r[3], r[4], r[5], activa))

    def obtener_promociones_combo(self):
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT id, descripcion FROM promociones WHERE activa=1 ORDER BY descripcion")
        res = c.fetchall()
        conn.close()
        return res

    def obtener_nombre_promocion(self, id_prom):
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT descripcion FROM promociones WHERE id=?", (id_prom,))
        res = c.fetchone()
        conn.close()
        return res[0] if res else ""

    def agregar_promocion(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        ventana = Toplevel(self.root)
        ventana.title("Agregar Promoción")
        ventana.geometry("400x400")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Descripción:*").grid(row=0, column=0, sticky=W, pady=2)
        entry_desc = ttk.Entry(frame)
        entry_desc.grid(row=0, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Tipo:*").grid(row=1, column=0, sticky=W, pady=2)
        combo_tipo = ttk.Combobox(frame, values=["porcentaje","2x1","cantidad"], state="readonly")
        combo_tipo.grid(row=1, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Valor (para porcentaje o cantidad):").grid(row=2, column=0, sticky=W, pady=2)
        entry_valor = ttk.Entry(frame)
        entry_valor.grid(row=2, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Fecha inicio (YYYY-MM-DD):").grid(row=3, column=0, sticky=W, pady=2)
        entry_ini = ttk.Entry(frame)
        entry_ini.grid(row=3, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Fecha fin (YYYY-MM-DD):").grid(row=4, column=0, sticky=W, pady=2)
        entry_fin = ttk.Entry(frame)
        entry_fin.grid(row=4, column=1, pady=2, sticky=W)
        var_activa = IntVar(value=1)
        ttk.Checkbutton(frame, text="Activa", variable=var_activa).grid(row=5, column=0, columnspan=2, pady=5)

        def guardar():
            desc = entry_desc.get().strip()
            tipo = combo_tipo.get()
            valor_str = entry_valor.get().strip()
            ini = entry_ini.get().strip()
            fin = entry_fin.get().strip()
            activa = var_activa.get()
            if not desc or not tipo:
                messagebox.showerror("Error", "Descripción y tipo obligatorios")
                return
            valor = None
            if valor_str:
                try:
                    valor = float(valor_str)
                except:
                    messagebox.showerror("Error", "Valor debe ser número")
                    return
            # Validar fechas
            if ini:
                try:
                    datetime.datetime.strptime(ini, "%Y-%m-%d")
                except:
                    messagebox.showerror("Error", "Formato fecha inicio inválido (YYYY-MM-DD)")
                    return
            if fin:
                try:
                    datetime.datetime.strptime(fin, "%Y-%m-%d")
                except:
                    messagebox.showerror("Error", "Formato fecha fin inválido (YYYY-MM-DD)")
                    return
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO promociones (descripcion, tipo, valor, fecha_inicio, fecha_fin, activa)
                             VALUES (?,?,?,?,?,?)''', (desc, tipo, valor, ini, fin, activa))
                conn.commit()
                messagebox.showinfo("Éxito", "Promoción agregada")
                ventana.destroy()
                self.cargar_promociones()
                self.actualizar_combos_venta()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()
        ttk.Button(frame, text="Guardar", command=guardar).grid(row=6, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=6, column=1, pady=10)

    def editar_promocion(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        seleccion = self.tree_promociones.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona una promoción")
            return
        item = self.tree_promociones.item(seleccion[0])
        vals = item['values']
        if not vals: return
        prom_id = vals[0]
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT * FROM promociones WHERE id=?", (prom_id,))
        prom = c.fetchone()
        conn.close()
        if not prom:
            messagebox.showerror("Error", "No encontrado")
            return
        ventana = Toplevel(self.root)
        ventana.title("Editar Promoción")
        ventana.geometry("400x400")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Descripción:*").grid(row=0, column=0, sticky=W, pady=2)
        entry_desc = ttk.Entry(frame)
        entry_desc.insert(0, prom[1])
        entry_desc.grid(row=0, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Tipo:*").grid(row=1, column=0, sticky=W, pady=2)
        combo_tipo = ttk.Combobox(frame, values=["porcentaje","2x1","cantidad"], state="readonly")
        combo_tipo.set(prom[2])
        combo_tipo.grid(row=1, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Valor:").grid(row=2, column=0, sticky=W, pady=2)
        entry_valor = ttk.Entry(frame)
        entry_valor.insert(0, str(prom[3]) if prom[3] is not None else "")
        entry_valor.grid(row=2, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Fecha inicio (YYYY-MM-DD):").grid(row=3, column=0, sticky=W, pady=2)
        entry_ini = ttk.Entry(frame)
        entry_ini.insert(0, prom[4] or "")
        entry_ini.grid(row=3, column=1, pady=2, sticky=W)
        ttk.Label(frame, text="Fecha fin (YYYY-MM-DD):").grid(row=4, column=0, sticky=W, pady=2)
        entry_fin = ttk.Entry(frame)
        entry_fin.insert(0, prom[5] or "")
        entry_fin.grid(row=4, column=1, pady=2, sticky=W)
        var_activa = IntVar(value=prom[6])
        ttk.Checkbutton(frame, text="Activa", variable=var_activa).grid(row=5, column=0, columnspan=2, pady=5)

        def guardar():
            desc = entry_desc.get().strip()
            tipo = combo_tipo.get()
            valor_str = entry_valor.get().strip()
            ini = entry_ini.get().strip()
            fin = entry_fin.get().strip()
            activa = var_activa.get()
            if not desc or not tipo:
                messagebox.showerror("Error", "Descripción y tipo obligatorios")
                return
            valor = None
            if valor_str:
                try:
                    valor = float(valor_str)
                except:
                    messagebox.showerror("Error", "Valor debe ser número")
                    return
            if ini:
                try:
                    datetime.datetime.strptime(ini, "%Y-%m-%d")
                except:
                    messagebox.showerror("Error", "Formato fecha inicio inválido")
                    return
            if fin:
                try:
                    datetime.datetime.strptime(fin, "%Y-%m-%d")
                except:
                    messagebox.showerror("Error", "Formato fecha fin inválido")
                    return
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute('''UPDATE promociones SET descripcion=?, tipo=?, valor=?, fecha_inicio=?, fecha_fin=?, activa=?
                             WHERE id=?''', (desc, tipo, valor, ini, fin, activa, prom_id))
                conn.commit()
                messagebox.showinfo("Éxito", "Promoción actualizada")
                ventana.destroy()
                self.cargar_promociones()
                self.actualizar_combos_venta()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()
        ttk.Button(frame, text="Guardar", command=guardar).grid(row=6, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=6, column=1, pady=10)

    def eliminar_promocion(self):
        if self.rol != 'admin':
            messagebox.showerror("Permiso", "Solo administradores")
            return
        seleccion = self.tree_promociones.selection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona una promoción")
            return
        prom_id = self.tree_promociones.item(seleccion[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar promoción?"):
            conn = conectar_bd()
            c = conn.cursor()
            try:
                c.execute("DELETE FROM promociones WHERE id=?", (prom_id,))
                conn.commit()
                messagebox.showinfo("Éxito", "Promoción eliminada")
                self.cargar_promociones()
                self.actualizar_combos_venta()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "No se puede eliminar porque está asociada a productos")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                conn.close()

    # ==========================================
    # PESTAÑA VENTAS (con descuentos y promociones)
    # ==========================================
    def construir_tab_ventas(self):
        # Panel superior: cliente y botones
        frame_sup = ttk.Frame(self.tab_ventas)
        frame_sup.pack(fill=X, padx=5, pady=5)
        ttk.Label(frame_sup, text="Cliente:").pack(side=LEFT, padx=2)
        self.cliente_combo = ttk.Combobox(frame_sup, state="readonly", width=30)
        self.cliente_combo.pack(side=LEFT, padx=5)
        ttk.Button(frame_sup, text="Agregar producto", command=self.agregar_producto_venta).pack(side=LEFT, padx=5)
        ttk.Button(frame_sup, text="Finalizar venta", command=self.finalizar_venta).pack(side=LEFT, padx=5)
        ttk.Button(frame_sup, text="Generar factura PDF", command=self.generar_factura).pack(side=LEFT, padx=5)
        ttk.Button(frame_sup, text="Limpiar carrito", command=self.limpiar_carrito).pack(side=LEFT, padx=5)

        # Carrito de compras (Treeview)
        self.tree_carrito = ttk.Treeview(self.tab_ventas,
            columns=("Producto","Cantidad","Precio unit.","Descuento","Subtotal"), show="headings")
        for col in self.tree_carrito["columns"]:
            self.tree_carrito.heading(col, text=col)
            self.tree_carrito.column(col, width=120)
        self.tree_carrito.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Total
        self.label_total_venta = ttk.Label(self.tab_ventas, text="Total: $0.00", font=("Arial", 14))
        self.label_total_venta.pack(anchor=E, padx=10, pady=5)

        # Historial de ventas
        ttk.Label(self.tab_ventas, text="Historial de ventas", font=("Arial", 12)).pack(anchor=W, padx=5)
        self.tree_ventas = ttk.Treeview(self.tab_ventas,
            columns=("ID","Fecha","Cliente","Total","Usuario"), show="headings")
        for col in self.tree_ventas["columns"]:
            self.tree_ventas.heading(col, text=col)
            self.tree_ventas.column(col, width=120)
        self.tree_ventas.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Variables de carrito
        self.carrito = []  # list of dicts: {producto_id, nombre, cantidad, precio_unitario, descuento_aplicado, subtotal}
        self.total_venta = 0.0
        self.venta_actual_id = None  # para factura

    def actualizar_combos_venta(self):
        clientes = self.obtener_clientes_combo()
        self.cliente_combo['values'] = [f"{c[0]} - {c[1]}" for c in clientes]
        if clientes:
            self.cliente_combo.set(f"{clientes[0][0]} - {clientes[0][1]}")

    def agregar_producto_venta(self):
        # Ventana para buscar producto
        ventana = Toplevel(self.root)
        ventana.title("Agregar producto al carrito")
        ventana.geometry("500x400")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(frame, text="Código o nombre:").grid(row=0, column=0, sticky=W)
        entry_busq = ttk.Entry(frame, width=30)
        entry_busq.grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Buscar", command=lambda: self.buscar_producto_venta(entry_busq.get(), tree)).grid(row=0, column=2, padx=5)

        # Treeview para mostrar resultados
        tree = ttk.Treeview(frame, columns=("ID","Código","Nombre","Precio","Stock","Descuento","Promoción"), show="headings", height=8)
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        tree.grid(row=1, column=0, columnspan=3, pady=5, sticky="nsew")

        ttk.Label(frame, text="Cantidad:").grid(row=2, column=0, sticky=W, pady=5)
        entry_cant = ttk.Entry(frame, width=10)
        entry_cant.grid(row=2, column=1, sticky=W, pady=5)
        entry_cant.insert(0, "1")

        def agregar():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showerror("Error", "Selecciona un producto")
                return
            item = tree.item(seleccion[0])
            vals = item['values']
            if not vals: return
            prod_id = vals[0]
            stock = vals[4]
            try:
                cant = int(entry_cant.get().strip())
                if cant <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Cantidad debe ser entero positivo")
                return
            if cant > stock:
                messagebox.showerror("Error", f"Stock insuficiente. Disponible: {stock}")
                return

            # Obtener precio y descuento/promoción del producto
            conn = conectar_bd()
            c = conn.cursor()
            c.execute('''SELECT p.precio, p.descuento, prom.tipo, prom.valor, prom.fecha_inicio, prom.fecha_fin
                         FROM productos p
                         LEFT JOIN promociones prom ON p.promocion_id = prom.id
                         WHERE p.id=?''', (prod_id,))
            prod_data = c.fetchone()
            conn.close()
            if not prod_data:
                messagebox.showerror("Error", "Producto no encontrado")
                return
            precio_base = prod_data[0]
            desc_pct = prod_data[1] or 0
            prom_tipo = prod_data[2]
            prom_valor = prod_data[3]
            prom_ini = prod_data[4]
            prom_fin = prod_data[5]

            # Verificar si la promoción está activa (fechas)
            prom_activa = False
            if prom_tipo:
                hoy = datetime.date.today()
                if prom_ini:
                    try:
                        ini = datetime.datetime.strptime(prom_ini, "%Y-%m-%d").date()
                    except:
                        ini = None
                else:
                    ini = None
                if prom_fin:
                    try:
                        fin = datetime.datetime.strptime(prom_fin, "%Y-%m-%d").date()
                    except:
                        fin = None
                else:
                    fin = None
                if (ini is None or ini <= hoy) and (fin is None or fin >= hoy):
                    prom_activa = True

            # Aplicar descuento
            descuento_aplicado = 0.0
            precio_final = precio_base

            # Descuento porcentual del producto
            if desc_pct > 0:
                descuento_aplicado = precio_base * (desc_pct / 100)
                precio_final = precio_base - descuento_aplicado

            # Promoción (si está activa y es más beneficiosa)
            if prom_activa and prom_tipo:
                if prom_tipo == "porcentaje" and prom_valor:
                    desc_promo = precio_base * (prom_valor / 100)
                    if desc_promo > descuento_aplicado:
                        descuento_aplicado = desc_promo
                        precio_final = precio_base - desc_promo
                elif prom_tipo == "2x1":
                    # Si la cantidad es par, se aplica descuento del 50% en la mitad de productos
                    if cant >= 2:
                        # Descuento equivalente a la mitad de los productos (gratis)
                        unidades_gratis = cant // 2
                        descuento_aplicado = unidades_gratis * precio_base
                        precio_final = (cant - unidades_gratis) * precio_base
                        # Recalculamos el precio unitario efectivo
                        precio_final_unitario = precio_final / cant if cant > 0 else 0
                    else:
                        precio_final_unitario = precio_base
                elif prom_tipo == "cantidad" and prom_valor:
                    # Ejemplo: "3x2" => valor = 3, se paga 2
                    if cant >= prom_valor:
                        grupos = cant // prom_valor
                        resto = cant % prom_valor
                        pagar = grupos * (prom_valor - 1) + resto
                        precio_final = pagar * precio_base
                        precio_final_unitario = precio_final / cant if cant > 0 else 0
                    else:
                        precio_final_unitario = precio_base
                else:
                    precio_final_unitario = precio_final
            else:
                precio_final_unitario = precio_final

            # Calcular subtotal con descuento ya aplicado
            subtotal = precio_final_unitario * cant

            # Agregar al carrito
            self.carrito.append({
                'producto_id': prod_id,
                'nombre': vals[2],
                'cantidad': cant,
                'precio_unitario': precio_final_unitario,
                'descuento_aplicado': descuento_aplicado,
                'subtotal': subtotal
            })
            self.actualizar_carrito()
            ventana.destroy()

        ttk.Button(frame, text="Agregar al carrito", command=agregar).grid(row=3, column=0, columnspan=3, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=4, column=0, columnspan=3)

        # Función de búsqueda para el tree
        def buscar_producto_venta(criterio, tree):
            for item in tree.get_children():
                tree.delete(item)
            if not criterio:
                return
            conn = conectar_bd()
            c = conn.cursor()
            c.execute('''SELECT p.id, p.codigo, p.nombre, p.precio, p.stock, p.descuento, prom.descripcion
                         FROM productos p
                         LEFT JOIN promociones prom ON p.promocion_id = prom.id
                         WHERE p.nombre LIKE ? OR p.codigo LIKE ?''',
                      (f"%{criterio}%", f"%{criterio}%"))
            rows = c.fetchall()
            conn.close()
            for r in rows:
                tree.insert("", END, values=r)

    def actualizar_carrito(self):
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        total = 0.0
        for prod in self.carrito:
            self.tree_carrito.insert("", END, values=(
                prod['nombre'],
                prod['cantidad'],
                f"${prod['precio_unitario']:.2f}",
                f"${prod['descuento_aplicado']:.2f}",
                f"${prod['subtotal']:.2f}"
            ))
            total += prod['subtotal']
        self.total_venta = total
        self.label_total_venta.config(text=f"Total: ${total:.2f}")

    def limpiar_carrito(self):
        self.carrito = []
        self.total_venta = 0.0
        self.actualizar_carrito()

    def finalizar_venta(self):
        if not self.carrito:
            messagebox.showerror("Error", "El carrito está vacío")
            return
        cliente_seleccionado = self.cliente_combo.get()
        if not cliente_seleccionado:
            messagebox.showerror("Error", "Selecciona un cliente")
            return
        try:
            cliente_id = int(cliente_seleccionado.split(" - ")[0])
        except:
            messagebox.showerror("Error", "Cliente inválido")
            return

        # Verificar stock nuevamente (por si cambió)
        conn = conectar_bd()
        c = conn.cursor()
        for prod in self.carrito:
            c.execute("SELECT stock FROM productos WHERE id=?", (prod['producto_id'],))
            stock = c.fetchone()
            if not stock or stock[0] < prod['cantidad']:
                messagebox.showerror("Error", f"Stock insuficiente para {prod['nombre']}")
                conn.close()
                return
        # Registrar venta
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = self.total_venta
        try:
            c.execute("INSERT INTO ventas (fecha, cliente_id, total, usuario_id) VALUES (?,?,?,?)",
                      (fecha, cliente_id, total, self.usuario_id))
            venta_id = c.lastrowid
            # Detalles y actualizar stock
            for prod in self.carrito:
                c.execute('''INSERT INTO detalle_venta 
                              (venta_id, producto_id, cantidad, precio_unitario, subtotal, descuento_aplicado)
                              VALUES (?,?,?,?,?,?)''',
                          (venta_id, prod['producto_id'], prod['cantidad'], prod['precio_unitario'],
                           prod['subtotal'], prod['descuento_aplicado']))
                c.execute("UPDATE productos SET stock = stock - ? WHERE id=?", 
                          (prod['cantidad'], prod['producto_id']))
            conn.commit()
            messagebox.showinfo("Éxito", f"Venta registrada con ID {venta_id}")
            self.venta_actual_id = venta_id
            # Limpiar carrito y recargar ventas
            self.limpiar_carrito()
            self.cargar_ventas()
            # Generar factura automáticamente
            self.generar_factura(venta_id)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al registrar venta: {e}")
        finally:
            conn.close()

    def cargar_ventas(self):
        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)
        conn = conectar_bd()
        c = conn.cursor()
        c.execute('''SELECT v.id, v.fecha, c.nombre, v.total, u.username
                     FROM ventas v
                     LEFT JOIN clientes c ON v.cliente_id = c.id
                     LEFT JOIN usuarios u ON v.usuario_id = u.id
                     ORDER BY v.fecha DESC''')
        rows = c.fetchall()
        conn.close()
        for r in rows:
            self.tree_ventas.insert("", 0, values=r)

    def generar_factura(self, venta_id=None):
        if venta_id is None:
            if hasattr(self, 'venta_actual_id') and self.venta_actual_id:
                venta_id = self.venta_actual_id
            else:
                messagebox.showerror("Error", "No hay venta seleccionada para facturar")
                return
        # Obtener datos de la venta
        conn = conectar_bd()
        c = conn.cursor()
        c.execute('''SELECT v.fecha, c.nombre, c.direccion, c.telefono, v.total
                     FROM ventas v
                     LEFT JOIN clientes c ON v.cliente_id = c.id
                     WHERE v.id=?''', (venta_id,))
        venta = c.fetchone()
        if not venta:
            messagebox.showerror("Error", "Venta no encontrada")
            conn.close()
            return
        fecha, cliente_nom, cliente_dir, cliente_tel, total = venta
        c.execute('''SELECT p.nombre, dv.cantidad, dv.precio_unitario, dv.subtotal, dv.descuento_aplicado
                     FROM detalle_venta dv
                     JOIN productos p ON dv.producto_id = p.id
                     WHERE dv.venta_id=?''', (venta_id,))
        detalles = c.fetchall()
        conn.close()

        # Crear PDF
        try:
            filename = os.path.join(FACTURAS_DIR, f"factura_{venta_id:04d}.pdf")
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height-50, "QuickMart Manager")
            c.setFont("Helvetica", 12)
            c.drawString(50, height-80, f"Factura N°: {venta_id:04d}")
            c.drawString(50, height-100, f"Fecha: {fecha}")
            c.drawString(50, height-120, f"Cliente: {cliente_nom or 'Genérico'}")
            if cliente_dir:
                c.drawString(50, height-140, f"Dirección: {cliente_dir}")
            if cliente_tel:
                c.drawString(50, height-160, f"Teléfono: {cliente_tel}")
            # Tabla de productos
            y = height - 200
            data = [["Producto", "Cant.", "Precio", "Dto.", "Subtotal"]]
            for d in detalles:
                data.append([d[0], str(d[1]), f"${d[2]:.2f}", f"${d[4]:.2f}", f"${d[3]:.2f}"])
            table = Table(data, colWidths=[200, 50, 70, 70, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('FONTSIZE', (0,1), (-1,-1), 9),
            ]))
            table.wrapOn(c, width-100, height)
            table.drawOn(c, 50, y - len(data)*20)
            # Total
            c.setFont("Helvetica-Bold", 14)
            c.drawString(400, y - len(data)*20 - 30, f"TOTAL: ${total:.2f}")
            c.save()
            messagebox.showinfo("Factura", f"Factura generada: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar factura: {e}")

    # ==========================================
    # PESTAÑA COMPRAS A PROVEEDORES
    # ==========================================
    def construir_tab_compras(self):
        frame_sup = ttk.Frame(self.tab_compras)
        frame_sup.pack(fill=X, padx=5, pady=5)
        ttk.Label(frame_sup, text="Proveedor:").pack(side=LEFT, padx=2)
        self.proveedor_compra_combo = ttk.Combobox(frame_sup, state="readonly", width=30)
        self.proveedor_compra_combo.pack(side=LEFT, padx=5)
        ttk.Button(frame_sup, text="Agregar producto", command=self.agregar_producto_compra).pack(side=LEFT, padx=5)
        ttk.Button(frame_sup, text="Confirmar compra", command=self.confirmar_compra).pack(side=LEFT, padx=5)
        ttk.Button(frame_sup, text="Limpiar", command=self.limpiar_compra).pack(side=LEFT, padx=5)

        self.tree_compra = ttk.Treeview(self.tab_compras,
            columns=("Producto","Cantidad","Costo unit.","Subtotal"), show="headings")
        for col in self.tree_compra["columns"]:
            self.tree_compra.heading(col, text=col)
            self.tree_compra.column(col, width=120)
        self.tree_compra.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.label_total_compra = ttk.Label(self.tab_compras, text="Total: $0.00", font=("Arial", 14))
        self.label_total_compra.pack(anchor=E, padx=10, pady=5)

        ttk.Label(self.tab_compras, text="Historial de compras", font=("Arial", 12)).pack(anchor=W, padx=5)
        self.tree_compras_hist = ttk.Treeview(self.tab_compras,
            columns=("ID","Fecha","Proveedor","Total","Usuario"), show="headings")
        for col in self.tree_compras_hist["columns"]:
            self.tree_compras_hist.heading(col, text=col)
            self.tree_compras_hist.column(col, width=120)
        self.tree_compras_hist.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.compra_carrito = []  # list of dict: {producto_id, nombre, cantidad, costo_unitario, subtotal}
        self.total_compra = 0.0

    def actualizar_combos_compra(self):
        proveedores = self.obtener_proveedores_combo()
        self.proveedor_compra_combo['values'] = [f"{p[0]} - {p[1]}" for p in proveedores]
        if proveedores:
            self.proveedor_compra_combo.set(f"{proveedores[0][0]} - {proveedores[0][1]}")

    def agregar_producto_compra(self):
        ventana = Toplevel(self.root)
        ventana.title("Agregar producto a compra")
        ventana.geometry("500x400")
        frame = ttk.Frame(ventana, padding=10)
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(frame, text="Código o nombre:").grid(row=0, column=0, sticky=W)
        entry_busq = ttk.Entry(frame, width=30)
        entry_busq.grid(row=0, column=1, padx=5)
        tree = ttk.Treeview(frame, columns=("ID","Código","Nombre","Precio","Stock"), show="headings", height=8)
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        tree.grid(row=1, column=0, columnspan=3, pady=5, sticky="nsew")

        def buscar():
            criterio = entry_busq.get().strip()
            for item in tree.get_children():
                tree.delete(item)
            if not criterio:
                return
            conn = conectar_bd()
            c = conn.cursor()
            c.execute("SELECT id, codigo, nombre, precio, stock FROM productos WHERE nombre LIKE ? OR codigo LIKE ?",
                      (f"%{criterio}%", f"%{criterio}%"))
            rows = c.fetchall()
            conn.close()
            for r in rows:
                tree.insert("", END, values=r)

        ttk.Button(frame, text="Buscar", command=buscar).grid(row=0, column=2, padx=5)

        ttk.Label(frame, text="Cantidad:").grid(row=2, column=0, sticky=W, pady=5)
        entry_cant = ttk.Entry(frame, width=10)
        entry_cant.grid(row=2, column=1, sticky=W, pady=5)
        entry_cant.insert(0, "1")
        ttk.Label(frame, text="Costo unitario:").grid(row=3, column=0, sticky=W, pady=5)
        entry_costo = ttk.Entry(frame, width=15)
        entry_costo.grid(row=3, column=1, sticky=W, pady=5)

        def agregar():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showerror("Error", "Selecciona un producto")
                return
            item = tree.item(seleccion[0])
            vals = item['values']
            if not vals: return
            prod_id = vals[0]
            try:
                cant = int(entry_cant.get().strip())
                if cant <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Cantidad debe ser entero positivo")
                return
            costo_str = entry_costo.get().strip()
            if not costo_str:
                # Usar precio actual
                costo = vals[3]
            else:
                try:
                    costo = float(costo_str)
                    if costo < 0:
                        raise ValueError
                except:
                    messagebox.showerror("Error", "Costo debe ser número positivo")
                    return
            subtotal = cant * costo
            self.compra_carrito.append({
                'producto_id': prod_id,
                'nombre': vals[2],
                'cantidad': cant,
                'costo_unitario': costo,
                'subtotal': subtotal
            })
            self.actualizar_compra_carrito()
            ventana.destroy()

        ttk.Button(frame, text="Agregar", command=agregar).grid(row=4, column=0, columnspan=3, pady=10)
        ttk.Button(frame, text="Cancelar", command=ventana.destroy).grid(row=5, column=0, columnspan=3)

    def actualizar_compra_carrito(self):
        for item in self.tree_compra.get_children():
            self.tree_compra.delete(item)
        total = 0.0
        for prod in self.compra_carrito:
            self.tree_compra.insert("", END, values=(
                prod['nombre'],
                prod['cantidad'],
                f"${prod['costo_unitario']:.2f}",
                f"${prod['subtotal']:.2f}"
            ))
            total += prod['subtotal']
        self.total_compra = total
        self.label_total_compra.config(text=f"Total: ${total:.2f}")

    def limpiar_compra(self):
        self.compra_carrito = []
        self.total_compra = 0.0
        self.actualizar_compra_carrito()

    def confirmar_compra(self):
        if not self.compra_carrito:
            messagebox.showerror("Error", "Carrito de compra vacío")
            return
        proveedor = self.proveedor_compra_combo.get()
        if not proveedor:
            messagebox.showerror("Error", "Selecciona un proveedor")
            return
        try:
            prov_id = int(proveedor.split(" - ")[0])
        except:
            messagebox.showerror("Error", "Proveedor inválido")
            return
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = self.total_compra
        conn = conectar_bd()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO compras (fecha, proveedor_id, total, usuario_id) VALUES (?,?,?,?)",
                      (fecha, prov_id, total, self.usuario_id))
            compra_id = c.lastrowid
            for prod in self.compra_carrito:
                c.execute('''INSERT INTO detalle_compra 
                              (compra_id, producto_id, cantidad, costo_unitario, subtotal)
                              VALUES (?,?,?,?,?)''',
                          (compra_id, prod['producto_id'], prod['cantidad'], prod['costo_unitario'], prod['subtotal']))
                # Incrementar stock
                c.execute("UPDATE productos SET stock = stock + ? WHERE id=?",
                          (prod['cantidad'], prod['producto_id']))
            conn.commit()
            messagebox.showinfo("Éxito", f"Compra registrada con ID {compra_id}")
            self.limpiar_compra()
            self.cargar_compras()
            self.cargar_productos()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al registrar compra: {e}")
        finally:
            conn.close()

    def cargar_compras(self):
        for item in self.tree_compras_hist.get_children():
            self.tree_compras_hist.delete(item)
        conn = conectar_bd()
        c = conn.cursor()
        c.execute('''SELECT c.id, c.fecha, p.nombre, c.total, u.username
                     FROM compras c
                     LEFT JOIN proveedores p ON c.proveedor_id = p.id
                     LEFT JOIN usuarios u ON c.usuario_id = u.id
                     ORDER BY c.fecha DESC''')
        rows = c.fetchall()
        conn.close()
        for r in rows:
            self.tree_compras_hist.insert("", 0, values=r)

    # ==========================================
    # PESTAÑA REPORTES (Exportación CSV/Excel)
    # ==========================================
    def construir_tab_reportes(self):
        frame = ttk.Frame(self.tab_reportes)
        frame.pack(fill=X, padx=5, pady=5)
        ttk.Label(frame, text="Tipo:").pack(side=LEFT, padx=2)
        self.reporte_tipo = ttk.Combobox(frame, values=["Productos","Ventas","Stock bajo","Compras"], state="readonly")
        self.reporte_tipo.set("Productos")
        self.reporte_tipo.pack(side=LEFT, padx=5)
        ttk.Label(frame, text="Desde:").pack(side=LEFT, padx=2)
        self.reporte_desde = ttk.Entry(frame, width=12)
        self.reporte_desde.pack(side=LEFT, padx=2)
        ttk.Label(frame, text="Hasta:").pack(side=LEFT, padx=2)
        self.reporte_hasta = ttk.Entry(frame, width=12)
        self.reporte_hasta.pack(side=LEFT, padx=2)
        ttk.Button(frame, text="Exportar CSV", command=self.exportar_csv).pack(side=LEFT, padx=5)
        ttk.Button(frame, text="Exportar Excel", command=self.exportar_excel).pack(side=LEFT, padx=5)

        self.tree_reporte = ttk.Treeview(self.tab_reportes,
            columns=("Col1","Col2","Col3","Col4","Col5","Col6"), show="headings")
        for col in self.tree_reporte["columns"]:
            self.tree_reporte.heading(col, text=col)
            self.tree_reporte.column(col, width=100)
        self.tree_reporte.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def exportar_csv(self):
        tipo = self.reporte_tipo.get()
        desde = self.reporte_desde.get().strip()
        hasta = self.reporte_hasta.get().strip()
        # Validar fechas si se proporcionan
        if desde:
            try:
                datetime.datetime.strptime(desde, "%Y-%m-%d")
            except:
                messagebox.showerror("Error", "Formato desde inválido (YYYY-MM-DD)")
                return
        if hasta:
            try:
                datetime.datetime.strptime(hasta, "%Y-%m-%d")
            except:
                messagebox.showerror("Error", "Formato hasta inválido (YYYY-MM-DD)")
                return
        # Obtener datos según tipo
        conn = conectar_bd()
        c = conn.cursor()
        if tipo == "Productos":
            query = '''SELECT p.codigo, p.nombre, p.precio, p.stock, p.categoria, pr.nombre
                       FROM productos p LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                       ORDER BY p.nombre'''
            c.execute(query)
        elif tipo == "Ventas":
            query = '''SELECT v.id, v.fecha, c.nombre, v.total
                       FROM ventas v LEFT JOIN clientes c ON v.cliente_id = c.id
                       WHERE 1=1'''
            params = []
            if desde:
                query += " AND v.fecha >= ?"
                params.append(desde)
            if hasta:
                query += " AND v.fecha <= ?"
                params.append(hasta + " 23:59:59")
            query += " ORDER BY v.fecha DESC"
            c.execute(query, params)
        elif tipo == "Stock bajo":
            umbral = simpledialog.askinteger("Umbral", "Ingresa el stock mínimo:", parent=self.root)
            if umbral is None:
                conn.close()
                return
            query = '''SELECT codigo, nombre, stock, categoria FROM productos WHERE stock < ? ORDER BY stock'''
            c.execute(query, (umbral,))
        elif tipo == "Compras":
            query = '''SELECT c.id, c.fecha, pr.nombre, c.total
                       FROM compras c LEFT JOIN proveedores pr ON c.proveedor_id = pr.id
                       WHERE 1=1'''
            params = []
            if desde:
                query += " AND c.fecha >= ?"
                params.append(desde)
            if hasta:
                query += " AND c.fecha <= ?"
                params.append(hasta + " 23:59:59")
            query += " ORDER BY c.fecha DESC"
            c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        if not rows:
            messagebox.showinfo("Info", "No hay datos para exportar")
            return
        # Guardar CSV
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not filename:
            return
        try:
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Cabecera
                if rows:
                    writer.writerow([f"Col{i+1}" for i in range(len(rows[0]))])
                    writer.writerows(rows)
            messagebox.showinfo("Éxito", f"Reporte exportado a {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar CSV: {e}")

    def exportar_excel(self):
        tipo = self.reporte_tipo.get()
        desde = self.reporte_desde.get().strip()
        hasta = self.reporte_hasta.get().strip()
        if desde:
            try:
                datetime.datetime.strptime(desde, "%Y-%m-%d")
            except:
                messagebox.showerror("Error", "Formato desde inválido")
                return
        if hasta:
            try:
                datetime.datetime.strptime(hasta, "%Y-%m-%d")
            except:
                messagebox.showerror("Error", "Formato hasta inválido")
                return
        conn = conectar_bd()
        c = conn.cursor()
        if tipo == "Productos":
            query = '''SELECT p.codigo, p.nombre, p.precio, p.stock, p.categoria, pr.nombre
                       FROM productos p LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                       ORDER BY p.nombre'''
            c.execute(query)
        elif tipo == "Ventas":
            query = '''SELECT v.id, v.fecha, c.nombre, v.total
                       FROM ventas v LEFT JOIN clientes c ON v.cliente_id = c.id
                       WHERE 1=1'''
            params = []
            if desde:
                query += " AND v.fecha >= ?"
                params.append(desde)
            if hasta:
                query += " AND v.fecha <= ?"
                params.append(hasta + " 23:59:59")
            query += " ORDER BY v.fecha DESC"
            c.execute(query, params)
        elif tipo == "Stock bajo":
            umbral = simpledialog.askinteger("Umbral", "Ingresa el stock mínimo:", parent=self.root)
            if umbral is None:
                conn.close()
                return
            query = '''SELECT codigo, nombre, stock, categoria FROM productos WHERE stock < ? ORDER BY stock'''
            c.execute(query, (umbral,))
        elif tipo == "Compras":
            query = '''SELECT c.id, c.fecha, pr.nombre, c.total
                       FROM compras c LEFT JOIN proveedores pr ON c.proveedor_id = pr.id
                       WHERE 1=1'''
            params = []
            if desde:
                query += " AND c.fecha >= ?"
                params.append(desde)
            if hasta:
                query += " AND c.fecha <= ?"
                params.append(hasta + " 23:59:59")
            query += " ORDER BY c.fecha DESC"
            c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        if not rows:
            messagebox.showinfo("Info", "No hay datos para exportar")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if not filename:
            return
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            # Cabeceras
            if rows:
                headers = [f"Col{i+1}" for i in range(len(rows[0]))]
                ws.append(headers)
                for row in rows:
                    ws.append(list(row))
                # Dar formato
                for col in ws.columns:
                    max_len = 0
                    column = col[0].column_letter
                    for cell in col:
                        try:
                            if len(str(cell.value)) > max_len:
                                max_len = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_len + 2, 30)
                    ws.column_dimensions[column].width = adjusted_width
            wb.save(filename)
            messagebox.showinfo("Éxito", f"Reporte exportado a {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar Excel: {e}")

    # ==========================================
    # PESTAÑA GRÁFICOS (matplotlib)
    # ==========================================
    def construir_tab_graficos(self):
        self.frame_grafico = ttk.Frame(self.tab_graficos)
        self.frame_grafico.pack(fill=BOTH, expand=True, padx=5, pady=5)

        botones_frame = ttk.Frame(self.tab_graficos)
        botones_frame.pack(fill=X, pady=5)
        ttk.Button(botones_frame, text="Ventas diarias (7 días)", command=self.grafico_ventas_diarias).pack(side=LEFT, padx=5)
        ttk.Button(botones_frame, text="Ventas por categoría", command=self.grafico_ventas_categoria).pack(side=LEFT, padx=5)
        ttk.Button(botones_frame, text="Evolución mensual", command=self.grafico_evolucion_mensual).pack(side=LEFT, padx=5)

        self.fig = Figure(figsize=(6,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.text(0.5,0.5,"Selecciona un gráfico", ha='center', va='center', transform=self.ax.transAxes)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    def grafico_ventas_diarias(self):
        hoy = datetime.date.today()
        fechas = [(hoy - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        conn = conectar_bd()
        c = conn.cursor()
        totales = []
        for f in fechas:
            c.execute("SELECT SUM(total) FROM ventas WHERE fecha LIKE ?", (f+"%",))
            total = c.fetchone()[0] or 0
            totales.append(total)
        conn.close()
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.bar(fechas, totales, color='skyblue')
        ax.set_title("Ventas diarias (últimos 7 días)")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Total ($)")
        ax.tick_params(axis='x', rotation=45)
        self.fig.tight_layout()
        self.canvas.draw()

    def grafico_ventas_categoria(self):
        conn = conectar_bd()
        c = conn.cursor()
        c.execute('''SELECT p.categoria, SUM(dv.cantidad) 
                     FROM detalle_venta dv 
                     JOIN productos p ON dv.producto_id = p.id 
                     GROUP BY p.categoria''')
        datos = c.fetchall()
        conn.close()
        if not datos:
            messagebox.showinfo("Info", "No hay datos de ventas por categoría")
            return
        categorias = [d[0] or "Sin categoría" for d in datos]
        cantidades = [d[1] for d in datos]
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.pie(cantidades, labels=categorias, autopct='%1.1f%%', startangle=90)
        ax.set_title("Ventas por categoría (cantidad)")
        self.fig.tight_layout()
        self.canvas.draw()

    def grafico_evolucion_mensual(self):
        conn = conectar_bd()
        c = conn.cursor()
        c.execute('''SELECT strftime('%Y-%m', fecha) as mes, SUM(total) 
                     FROM ventas 
                     GROUP BY mes 
                     ORDER BY mes DESC LIMIT 12''')
        datos = c.fetchall()
        conn.close()
        if not datos:
            messagebox.showinfo("Info", "No hay datos mensuales")
            return
        meses = [d[0] for d in datos[::-1]]
        totales = [d[1] for d in datos[::-1]]
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(meses, totales, marker='o', linestyle='-', color='green')
        ax.set_title("Evolución mensual de ventas")
        ax.set_xlabel("Mes")
        ax.set_ylabel("Total ($)")
        ax.tick_params(axis='x', rotation=45)
        self.fig.tight_layout()
        self.canvas.draw()

# ============================================
# EJECUCIÓN
# ============================================
if __name__ == "__main__":
    crear_tablas()
    root = Tk()
    app = QuickMartApp(root)
    root.mainloop()
