# 🛒 QuickMart Manager 2.0 – Tu súper aliado para gestionar un supermercado

> **Hecho con ❤️ por una Dev Junior que no para de aprender**  
> *Versión 2.0 – Ahora con más funcionalidades que nunca*

---

## 📖 ¿Qué es esto?

**QuickMart Manager** es un sistema de gestión para supermercados que empecé como un proyecto de consola para practicar Python y bases de datos. Pero… ¡se me fue de las manos! Ahora tiene **interfaz gráfica con Tkinter**, **login de usuarios**, **facturas en PDF**, **descuentos y promociones**, **compras a proveedores**, **gráficos estadísticos**, **modo oscuro** y hasta **copias de seguridad automáticas**. 

Lo he diseñado pensando en que sea útil para un negocio real, pero también para que otros devs juniors como yo puedan aprender viendo el código. Está todo en un solo archivo (de momento) y bien comentado. ¡Espero que te sirva!

---

## ✨ ¿Qué puede hacer?

Te cuento las funcionalidades más chulas:

### 🔐 Login y roles
- Pantalla de inicio con usuario y contraseña (las contraseñas se guardan con hash).
- Dos roles: **administrador** (puede hacer todo) y **cajero** (solo ventas y consultas).
- Usuario por defecto: `admin` / `admin123` (cámbialo al primer inicio).

### 📦 Gestión completa de productos
- **CRUD** (Crear, Leer, Actualizar, Eliminar) de productos.
- Cada producto tiene: código, nombre, descripción, precio, stock, categoría, proveedor, **descuento porcentual** y **promoción asociada**.
- **Filtros avanzados**: por nombre, categoría, rango de precios y stock mínimo.
- Búsqueda rápida por código o nombre.

### 🧾 Facturas en PDF
- Al finalizar una venta, se genera automáticamente un PDF con el detalle de la compra.
- Incluye: número de factura, fecha, datos del cliente, productos, cantidades, precios, descuentos aplicados y total.
- Se guardan en la carpeta `facturas/`.

### 🏷️ Descuentos y promociones (¡mi parte favorita!)
- Cada producto puede tener un **descuento porcentual** (ej. 10%).
- Puedes crear **promociones** de tres tipos:
  - **Porcentaje**: descuento adicional sobre el precio.
  - **2x1**: llevas 2 y pagas 1.
  - **Cantidad**: por ejemplo, "3x2" (llevas 3, pagas 2).
- Las promociones tienen fechas de inicio y fin, y se pueden activar/desactivar.
- **En el carrito de ventas, el sistema aplica automáticamente la mejor oferta** (la que más descuento te dé). ¡Así de inteligente!

### 🛒 Ventas con carrito
- Seleccionas un cliente (o usas "genérico").
- Agregas productos al carrito con la cantidad deseada.
- El carrito muestra el precio unitario, el descuento aplicado y el subtotal.
- Al finalizar, se registra la venta, se actualiza el stock, y se genera la factura PDF automáticamente.

### 📦 Compras a proveedores (reposición de stock)
- Seleccionas un proveedor.
- Agregas productos con la cantidad y el costo unitario (puedes tomar el precio de venta como referencia).
- Al confirmar, se registra la compra y **se incrementa el stock** de los productos.
- Historial de compras para controlar gastos.

### 📊 Reportes y exportaciones
- Puedes exportar listados de **productos**, **ventas**, **stock bajo** y **compras**.
- Formatos: **CSV** y **Excel** (con formato bonito, columnas ajustadas, etc.).
- Filtros por rango de fechas en ventas y compras.

### 📈 Gráficos estadísticos (con matplotlib)
- Tres gráficos interactivos:
  - **Ventas diarias** de los últimos 7 días (barras).
  - **Ventas por categoría** (tarta).
  - **Evolución mensual** de ventas (línea).
- Se actualizan con los datos de la base de datos en tiempo real.

### 🌙 Modo oscuro
- Un botón en el menú para alternar entre tema claro y oscuro.
- La preferencia se guarda en un archivo de configuración (`config.ini`) y se mantiene al cerrar y abrir la app.
- ¡Ideal para trabajar de noche sin que te quemen los ojos!

### 💾 Copias de seguridad automáticas
- Cada vez que inicias sesión, se hace una copia de la base de datos en la carpeta `backups/`.
- También puedes hacer copias manuales desde el menú "Herramientas".
- Solo se guardan las últimas 10 copias para no llenar el disco.

### 👥 Gestión de clientes y proveedores
- CRUD completo para ambas entidades.
- Se usan en ventas y compras para asociar datos.

### 🛠️ Interfaz gráfica (Tkinter)
- Pestañas organizadas: Productos, Proveedores, Clientes, Promociones, Ventas, Compras, Reportes y Gráficos.
- Tablas con scroll, botones intuitivos y campos de entrada con validaciones.
- Mensajes de error claros (nada de "error 500", sino "El precio debe ser un número positivo").

---

## 🚀 ¿Cómo lo pongo en marcha?

### Requisitos previos
- Python 3.8 o superior.
- Las librerías que uso (instálalas con pip):

```bash
pip install reportlab openpyxl matplotlib
```

*(Tkinter viene con Python por defecto en Windows y Linux, pero en algunos sistemas como Ubuntu hay que instalarlo con `sudo apt-get install python3-tk`)*

### Pasos
1. **Descarga** el archivo `quickmart_manager.py` (está más abajo).
2. **Ejecuta** en la terminal:

```bash
python quickmart_manager.py
```

3. La primera vez, se creará la base de datos `quickmart.db` y un usuario administrador:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`

4. ¡Ya estás dentro! Empieza a agregar productos, proveedores y clientes. Luego prueba a hacer una venta y verás cómo se genera la factura PDF.

---

## 📁 Estructura de carpetas (se crean solas)

```
quickmart_manager/
├── quickmart_manager.py      # El código principal
├── quickmart.db              # Base de datos SQLite
├── backups/                  # Copias de seguridad automáticas
├── facturas/                 # Facturas PDF generadas
├── reportes/                 # Exportaciones CSV/Excel
├── config.ini                # Preferencias (tema oscuro)
└── README.md                 # Este archivo (que estás leyendo)
```

---

## 🧑‍💻 ¿Cómo está hecho? (para curiosos)

- **Lenguaje**: Python 3 (todo en un solo archivo, pero con funciones bien separadas).
- **Base de datos**: SQLite (no necesita servidor, perfecto para empezar).
- **Interfaz**: Tkinter (nativa, no requiere instalar nada extra).
- **PDFs**: ReportLab (genera documentos profesionales).
- **Excel**: OpenPyXL (da formato a las celdas, ajusta anchos, etc.).
- **Gráficos**: Matplotlib (se integra con Tkinter usando `FigureCanvasTkAgg`).
- **Seguridad**: Hash SHA-256 para contraseñas (con sal, aunque en este caso la sal es fija para simplificar, pero en producción se mejora).
- **Backup**: Uso `shutil.copy2` para copiar la BD con metadatos.

---

## 🤔 ¿Qué aprendí haciendo esto?

- A manejar **eventos y widgets de Tkinter** (me costó entender los `grid`, `pack` y `bind`).
- Cómo **integrar matplotlib** dentro de una ventana de Tkinter (¡fue un reto!).
- A **diseñar una base de datos relacional** con claves foráneas y restricciones.
- A **aplicar lógica de negocio** (descuentos, promociones, actualización de stock) en el código.
- La importancia de **validar entradas** y mostrar mensajes de error amigables.
- A **generar PDFs y Excel** con bibliotecas externas.
- A **mantener el código limpio** y comentado para que otros (y yo mismo dentro de un mes) lo entiendan.

---

## 🚧 ¿Qué podría mejorar en el futuro?

- **Separar el código en módulos** (modelos, vistas, controladores) para que sea más mantenible.
- **Añadir más tipos de promociones** (por ejemplo, "descuento en la segunda unidad").
- **Soporte para múltiples sucursales**.
- **Panel de control** con indicadores (ventas hoy, productos más vendidos, etc.).
- **Envío de facturas por correo electrónico**.
- **Escáner de códigos de barras** (conectar un lector USB).
- **Modo multiusuario** con permisos más granulares.

---

## 🤝 ¿Quieres contribuir?

¡Claro que sí! Si eres dev junior (o no tan junior) y quieres mejorar algo, corregir un bug o añadir una funcionalidad, haz un **fork** del proyecto, crea una rama y envía un **pull request**. Estaré encantado de revisarlo y aprender juntos.

Si encuentras un error, por favor, abre un **issue** en GitHub (aunque de momento no está subido, pero si lo publico, lo haré).

---

## ⭐ ¿Te ha gustado?

Si este proyecto te ha sido útil o te ha inspirado, **dame una estrella** en GitHub (cuando lo suba) y compártelo con otros developers. Cada estrella me motiva a seguir mejorando.

---

## 📬 Contacto

Puedes escribirme a: **devjunior@quickmart.com** (es inventado, pero si realmente quieres contactar, ponte en contacto conmigo a través de LinkedIn o GitHub).

---

## 🙏 Agradecimientos

- A los tutoriales de YouTube que me enseñaron Tkinter.
- A la documentación de Python y SQLite.
- A mi café, que me acompañó en las largas noches de código.
- Y a ti, por leer esto y darle una oportunidad a mi proyecto.

---

**¡Gracias por usar QuickMart Manager!**  
*Hecho con código, café y mucha ilusión.* ☕🐍

---

**Versión**: 2.0  
**Fecha**: Julio 2026  
**Licencia**: MIT (haz lo que quieras con el código, pero si lo mejoras, compártelo).
