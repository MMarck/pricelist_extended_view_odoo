# Odoo 18 - Pricelist Items Financial Matrix / Matriz Financiera de Tarifa de Precios

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-8f8f8f.svg)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0.html)

---

### Language / Idioma
* 🇪🇸 [Español](#español)
* 🇬🇧 [English](#english)

---

<a name="español"></a>
## 🇪🇸 Español

### Descripción
Este módulo extiende las funcionalidades nativas de `product.pricelist.item` en **Odoo 18**, agregando métricas financieras en tiempo real y una vista editable en matriz para facilitar la gestión de márgenes, costos y precios de venta directamente desde las reglas de tarifa.

### Características Principales
* **Cálculo Financiero en Tiempo Real:** Calcula costo estándar (`product_cost`), ganancia monetaria (`profit_amount`), margen de ganancia (`profit_margin`) y remargo (`markup_percent`).
* **Edición Bidireccional (Inverse Logic):** Permite modificar el Margen, el Markup o la Ganancia directamente en la lista, recalculando automáticamente el `fixed_price` de la regla.
* **Vista en Matriz Editable:** Convierte la vista de lista de reglas en `editable="bottom"` con soporte para `multi_edit`.
* **Smart Button Integrado:** Acceso directo desde el formulario de la Tarifa de Precios (`product.pricelist`) a sus reglas dedicadas.
* **Acción de Histórico de Ventas:** Botón directo por regla para consultar las líneas de pedido de venta (`sale.order.line`) filtradas por producto, variante o categoría.

### Estructura de Campos Calculados
| Campo | Tipo | Fórmula / Lógica |
| :--- | :--- | :--- |
| **Cost** | `Float` | `product_id.standard_price` o `product_tmpl_id.standard_price` |
| **Profit** | `Float` | $\text{Price} - \text{Cost}$ |
| **Profit Margin (%)** | `Float` | $\frac{\text{Price} - \text{Cost}}{\text{Price}} \times 100$ |
| **Markup (%)** | `Float` | $\frac{\text{Price} - \text{Cost}}{\text{Cost}} \times 100$ |

### Instalación
1. Copia la carpeta del módulo dentro de tu directorio de `addons`.
2. Actualiza la lista de aplicaciones en modo desarrollador (`Apps > Update Apps List`).
3. Busca el módulo e instálalo.

---

<a name="english"></a>
## 🇬🇧 English

### Description
This module extends the native `product.pricelist.item` functionality in **Odoo 18**, providing real-time financial metrics and an inline editable matrix view to streamline margin, cost, and selling price management directly within pricelist rules.

### Key Features
* **Real-time Financial Calculations:** Automatically computes standard cost (`product_cost`), profit amount (`profit_amount`), profit margin (`profit_margin`), and markup percentage (`markup_percent`).
* **Two-Way Field Editing (Inverse Methods):** Updating Margin, Markup, or Profit directly in the tree view dynamically recalculates the rule's `fixed_price`.
* **Inline Editable Matrix View:** Converts the pricelist item tree view to `editable="bottom"` with full `multi_edit` support.
* **Integrated Smart Button:** Direct access from the Pricelist form view (`product.pricelist`) to its dedicated rules.
* **Sales History Action:** Dedicated button per rule to view filtered sale order lines (`sale.order.line`) by product, variant, or category.

### Computed Fields Structure
| Field | Type | Formula / Logic |
| :--- | :--- | :--- |
| **Cost** | `Float` | `product_id.standard_price` or `product_tmpl_id.standard_price` |
| **Profit** | `Float` | $\text{Price} - \text{Cost}$ |
| **Profit Margin (%)** | `Float` | $\frac{\text{Price} - \text{Cost}}{\text{Price}} \times 100$ |
| **Markup (%)** | `Float` | $\frac{\text{Price} - \text{Cost}}{\text{Cost}} \times 100$ |

### Installation
1. Place the module directory inside your custom `addons` path.
2. Update the app list in developer mode (`Apps > Update Apps List`).
3. Locate the module and click **Install**.

---

### Author / Autor
* **MR.Marck**