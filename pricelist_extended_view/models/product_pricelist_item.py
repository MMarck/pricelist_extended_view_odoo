# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    product_cost = fields.Float(
        string='Cost',
        compute='_compute_product_financials',
        digits='Product Price',
        store=True,
        # help='Costo estándar de la variante o plantilla de producto asociada a este elemento de lista de precios'
        help='Standard cost of the product variant or template associated with this pricelist item'
    )
    
    profit_amount = fields.Float(
        string='Profit',
        compute='_compute_product_financials',
        digits='Product Price',
        store=True,
        # help='Ganancia en valor monetario (Precio - Costo)'
        help='Profit in monetary value (Price - Cost)'
    )
    
    profit_margin = fields.Float(
        string='Profit Margin (%)',
        compute='_compute_product_financials',
        digits=(16, 2),
        store=True,
        # help='Margen de ganancia sobre el precio de venta: ((Precio - Costo) / Precio) * 100'
        help='Profit margin percentage over the selling price: ((Price - Cost) / Price) * 100'
    )

    markup_percent = fields.Float(
        string='Markup (%)',
        compute='_compute_product_financials',
        digits=(16, 2),
        store=True,
        # help='Porcentaje de remargo sobre el costo: ((Precio - Costo) / Costo) * 100'
        help='Percentage of markup over the cost: ((Price - Cost) / Cost) * 100'
    )

    @api.depends(
        'product_id', 
        'product_id.standard_price', 
        'product_id.list_price',
        'product_tmpl_id', 
        'product_tmpl_id.standard_price', 
        'product_tmpl_id.list_price',
        'applied_on', 
        'compute_price', 
        'fixed_price', 
        'percent_price'
    )
    def _compute_product_financials(self):
        for item in self:
            # 1. Obtener Costo (standard_price) de la variante o plantilla
            cost = 0.0
            product = None
            if item.applied_on == '0_product_variant' and item.product_id:
                product = item.product_id
                cost = item.product_id.standard_price
            elif item.applied_on == '1_product' and item.product_tmpl_id:
                product = item.product_tmpl_id
                cost = item.product_tmpl_id.standard_price

            item.product_cost = cost

            # 2. Obtener un precio numérico flotante seguro según el tipo de regla
            price_val = 0.0
            if item.compute_price == 'fixed':
                price_val = item.fixed_price or 0.0
            elif item.compute_price == 'percentage' and product:
                base_price = product.list_price if hasattr(product, 'list_price') else 0.0
                discount = item.percent_price or 0.0
                price_val = base_price * (1.0 - (discount / 100.0))
            else:
                # Si es de tipo 'formula' u otro, intentamos tomar fixed_price como fallback
                price_val = item.fixed_price or 0.0

            # 3. Cálculos de Financiera
            if price_val and cost:
                profit = price_val - cost
                item.profit_amount = profit
                item.profit_margin = (profit / price_val) if price_val > 0 else 0.0
                item.markup_percent = (profit / cost) if cost > 0 else 0.0
            elif price_val:
                item.profit_amount = price_val
                item.profit_margin = 1.0
                item.markup_percent = 0.0
            else:
                item.profit_amount = -cost if cost else 0.0
                item.profit_margin = 0.0
                item.markup_percent = 0.0