# 🛒 QuickMart Manager 2.0 – README (Español / English)

---

## 🇪🇸 Español

### 📖 ¿Qué es esto?

**QuickMart Manager** es un sistema de gestión para supermercados que empecé como un proyecto de consola para practicar Python y bases de datos. Pero… ¡se me fue de las manos! Ahora tiene **interfaz gráfica con Tkinter**, **login de usuarios**, **facturas en PDF**, **descuentos y promociones**, **compras a proveedores**, **gráficos estadísticos**, **modo oscuro** y hasta **copias de seguridad automáticas**.

Lo he diseñado pensando en que sea útil para un negocio real, pero también para que otros devs juniors como yo puedan aprender viendo el código. Está todo en un solo archivo (de momento) y bien comentado. ¡Espero que te sirva!

---

### ✨ ¿Qué puede hacer?

- **🔐 Login y roles**: Pantalla de inicio con usuario y contraseña (hash SHA‑256). Dos roles: **administrador** (todo) y **cajero** (ventas y consultas). Usuario por defecto: `admin` / `admin123`.

- **📦 Gestión de productos**: CRUD completo. Cada producto tiene: código, nombre, descripción, precio, stock, categoría, proveedor, **descuento porcentual** y **promoción asociada**. **Filtros avanzados** por nombre, categoría, rango de precios y stock mínimo.

- **🧾 Facturas en PDF**: Al finalizar una venta, se genera automáticamente un PDF con el detalle de la compra (número de factura, fecha, cliente, productos, cantidades, precios, descuentos y total). Se guardan en `facturas/`.

- **🏷️ Descuentos y promociones**: Cada producto puede tener un descuento porcentual. Puedes crear promociones de tipo **porcentaje**, **2x1** o **cantidad** (ej. "3x2"). Tienen fechas de inicio/fin y se activan/desactivan. **En el carrito, el sistema aplica automáticamente la mejor oferta**.

- **🛒 Ventas con carrito**: Seleccionas cliente, agregas productos, el carrito muestra precios, descuentos y subtotales. Al finalizar, se registra la venta, se actualiza el stock y se genera la factura PDF.

- **📦 Compras a proveedores**: Seleccionas proveedor, agregas productos con cantidad y costo unitario. Al confirmar, se registra la compra y **se incrementa el stock**. Historial de compras.

- **📊 Reportes y exportaciones**: Exporta listados de **productos**, **ventas**, **stock bajo** y **compras** a **CSV** o **Excel** (con formato bonito y columnas ajustadas). Filtros por fechas.

- **📈 Gráficos estadísticos**: Tres gráficos con matplotlib: ventas diarias (7 días), ventas por categoría (tarta) y evolución mensual (línea). Se actualizan en tiempo real.

- **🌙 Modo oscuro**: Alterna entre tema claro y oscuro. La preferencia se guarda en `config.ini`.

- **💾 Copias de seguridad automáticas**: Al iniciar sesión se hace una copia de la BD en `backups/`. También manual desde el menú. Solo se guardan las últimas 10 copias.

- **👥 Clientes y proveedores**: CRUD completo para ambas entidades.

- **🛠️ Interfaz gráfica (Tkinter)**: Pestañas organizadas, tablas con scroll, botones intuitivos y mensajes de error claros.

---

### 🚀 ¿Cómo lo pongo en marcha?

**Requisitos**: Python 3.8+, instalar dependencias:

```bash
pip install reportlab openpyxl matplotlib
```

*(En algunos Linux, instalar Tkinter con `sudo apt-get install python3-tk`)*

**Pasos**:
1. Descarga `quickmart_manager.py`.
2. Ejecuta: `python quickmart_manager.py`.
3. Usuario por defecto: `admin` / `admin123`.

---

### 📁 Estructura de carpetas (se crean solas)

```
quickmart_manager/
├── quickmart_manager.py
├── quickmart.db
├── backups/
├── facturas/
├── reportes/
├── config.ini
└── README.md
```

---

### 🧑‍💻 ¿Cómo está hecho?

- **Python 3**, **SQLite**, **Tkinter**, **ReportLab**, **OpenPyXL**, **Matplotlib**.
- Contraseñas con hash SHA‑256.
- Código modular, comentado y con validaciones en todos los campos.

---

### 🤝 ¿Quieres contribuir?

¡Claro! Haz fork, crea una rama y envía un pull request. Si encuentras un error, abre un issue.

---

### ⭐ ¿Te gusta? ¡Dale una estrella!

---

### 📬 Contacto

(Inventado) devjunior@quickmart.com – o por GitHub/LinkedIn.

---

### 🙏 Gracias por usar QuickMart Manager. ¡Hecho con código, café y mucha ilusión! ☕🐍

---

---

## 🇬🇧 English

### 📖 What is this?

**QuickMart Manager** is a supermarket management system I started as a console project to practice Python and databases. But… it got out of hand! Now it has a **graphical interface with Tkinter**, **user login**, **PDF invoices**, **discounts and promotions**, **supplier purchases**, **statistical charts**, **dark mode**, and even **automatic database backups**.

I designed it to be useful for a real business, but also for other junior devs like me to learn from the code. It's all in one file (for now) and well commented. I hope you find it useful!

---

### ✨ What can it do?

- **🔐 Login & roles**: Login screen with username/password (SHA‑256 hash). Two roles: **admin** (everything) and **cashier** (sales and queries). Default user: `admin` / `admin123`.

- **📦 Product management**: Full CRUD. Each product has: code, name, description, price, stock, category, supplier, **percentage discount** and **associated promotion**. **Advanced filters** by name, category, price range and minimum stock.

- **🧾 PDF invoices**: When a sale is completed, a PDF is automatically generated with purchase details (invoice number, date, customer, products, quantities, prices, discounts and total). Saved in `facturas/`.

- **🏷️ Discounts & promotions**: Each product can have a percentage discount. You can create promotions of type **percentage**, **2x1** or **quantity** (e.g. "3x2"). They have start/end dates and can be toggled on/off. **In the shopping cart, the system automatically applies the best deal**.

- **🛒 Shopping cart sales**: Select a customer, add products, the cart shows prices, discounts and subtotals. On checkout, the sale is recorded, stock is updated and the PDF invoice is generated.

- **📦 Supplier purchases**: Select a supplier, add products with quantity and unit cost. On confirmation, the purchase is recorded and **stock increases**. Purchase history is kept.

- **📊 Reports & exports**: Export lists of **products**, **sales**, **low stock** and **purchases** to **CSV** or **Excel** (with nice formatting and auto‑adjusted columns). Date filters available.

- **📈 Statistical charts**: Three matplotlib charts: daily sales (7 days), sales by category (pie) and monthly evolution (line). They update in real time.

- **🌙 Dark mode**: Toggle between light and dark themes. Preference saved in `config.ini`.

- **💾 Automatic backups**: A DB backup is made on login in `backups/`. Also manual from the menu. Only the last 10 copies are kept.

- **👥 Customers & suppliers**: Full CRUD for both.

- **🛠️ GUI (Tkinter)**: Organised tabs, scrollable tables, intuitive buttons and clear error messages.

---

### 🚀 How to run it?

**Requirements**: Python 3.8+, install dependencies:

```bash
pip install reportlab openpyxl matplotlib
```

*(On some Linux, install Tkinter with `sudo apt-get install python3-tk`)*

**Steps**:
1. Download `quickmart_manager.py`.
2. Run: `python quickmart_manager.py`.
3. Default user: `admin` / `admin123`.

---

### 📁 Folder structure (auto‑created)

```
quickmart_manager/
├── quickmart_manager.py
├── quickmart.db
├── backups/
├── facturas/
├── reportes/
├── config.ini
└── README.md
```

---

### 🧑‍💻 How is it built?

- **Python 3**, **SQLite**, **Tkinter**, **ReportLab**, **OpenPyXL**, **Matplotlib**.
- Passwords hashed with SHA‑256.
- Modular, commented code with input validation everywhere.

---

### 🤝 Want to contribute?

Sure! Fork it, create a branch and send a pull request. If you find a bug, open an issue.

---

### ⭐ Like it? Give it a star!

---

### 📬 Contact

visintinitech@gmail.com – or via GitHub/LinkedIn.

---

### 🙏 Thanks for using QuickMart Manager. Made with code, coffee, and lots of enthusiasm! ☕🐍

---

**Versión / Version**: 2.0  
**Fecha / Date**: Julio 2026 / July 2026  
**Licencia / License**: MIT (do whatever you want with the code, but if you improve it, share it).
