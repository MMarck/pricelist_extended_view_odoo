# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    product_cost = fields.Float(
        string='Cost',
        compute='_compute_product_financials',
        digits='Product Price',
        store=True,
        inverse='_inverse_product_cost',
        help='Standard cost of the product variant or template associated with this pricelist item'
    )
    
    profit_amount = fields.Float(
        string='Profit',
        compute='_compute_product_financials',
        digits='Product Price',
        store=True,
        inverse='_inverse_profit_amount',
        help='Profit in monetary value (Price - Cost). It can only be edited if compute_price is set to "Fixed price".'
    )
    
    profit_margin = fields.Float(
        string='Profit Margin (%)',
        compute='_compute_product_financials',
        digits=(16, 2),
        store=True,
        inverse='_inverse_profit_margin',
        help='Profit margin percentage over the selling price: ((Price - Cost) / Price) * 100. It can only be edited if compute_price is set to "Fixed price".'
    )

    markup_percent = fields.Float(
        string='Markup (%)',
        compute='_compute_product_financials',
        digits=(16, 2),
        store=True,
        inverse='_inverse_markup_percent',
        help='Percentage of markup over the cost: ((Price - Cost) / Cost) * 100. It can only be edited if compute_price is set to "Fixed price".'
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
    )
    def _compute_product_financials(self):
        """Compute financial metrics (cost, profit amount, profit margin, and markup percentage)

        for the current pricelist item based on its application rule and price computation method.
        """
        for item in self:
            # 1. Retrieve Standard Cost (standard_price) from variant or template
            cost = 0.0
            product = None
            if item.applied_on == '0_product_variant' and item.product_id:
                product = item.product_id
                cost = item.product_id.standard_price
            elif item.applied_on == '1_product' and item.product_tmpl_id:
                product = item.product_tmpl_id
                cost = item.product_tmpl_id.standard_price

            item.product_cost = cost

            # 2. Extract a safe numerical float price based on rule computation type
            price_val = 0.0
            if item.compute_price == 'fixed':
                price_val = item.fixed_price or 0.0
            elif item.compute_price == 'percentage' and product:
                base_price = product.list_price if hasattr(product, 'list_price') else 0.0
                discount = item.percent_price or 0.0
                price_val = base_price * (1.0 - (discount / 100.0))
            else:
                # Fall back to fixed_price for 'formula' or other unhandled computation types
                price_val = item.fixed_price or 0.0

            # 3. Calculate financial metrics
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

    def action_open_pricelist_item_modal(self):
            """Open the existing rule or a new form in a modal."""
            pricelist_id = self.env.context.get('default_pricelist_id') or self.pricelist_id.id or self.env.context.get('active_id')
            
            res = {
                'name': 'Price Rule (Modal)',
                'type': 'ir.actions.act_window',
                'res_model': 'product.pricelist.item',
                'view_mode': 'form',
                'target': 'new', # <-- Force the form to open in a modal
                'context': {
                    'default_pricelist_id': pricelist_id,
                }
            }
            
            # If the action is triggered from an existing record, we pass its ID to open the modal with that record's data
            if self:
                res['res_id'] = self[0].id
                
            return res

    # --- Action to open sales order lines filtered by current product or variant ---
    def action_view_sales(self):
        """
        Redirects to the Sales Analysis report with native filters applied based on whether the rule applies to a Variant, Product, or Category.
        """
        self.ensure_one()
        
        domain = [('state', 'in', ['sale', 'done'])]
        title_name = "Sales Analysis"

        if self.applied_on == '0_product_variant' and self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
            title_name = f"Sales Analysis - {self.product_id.display_name}"
        elif self.applied_on == '1_product' and self.product_tmpl_id:
            domain.append(('product_tmpl_id', '=', self.product_tmpl_id.id))
            title_name = f"Sales Analysis - {self.product_tmpl_id.name}"
        elif self.applied_on == '2_product_category' and self.categ_id:
            domain.append(('categ_id', '=', self.categ_id.id))
            title_name = f"Sales Analysis - {self.categ_id.name}"
        else:
            return {'type': 'ir.actions.act_window_close'}

        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_order_report_all")
        
        action['name'] = title_name
        action['domain'] = domain
        action['context'] = {
            'search_default_Sales': 1,               
            'search_default_filter_date': 1,          
            'group_by': ['date:month'],               
            'group_by_no_leaf': 1,
        }
        
        action['views'] = [
            (False, 'list'),
            (self.env.ref('sale.view_order_product_pivot').id, 'pivot'),
            (self.env.ref('sale.view_order_product_graph').id, 'graph'),
        ]
        action['target'] = 'current'
        
        return action

    # --- INVERSE LOGIC 1: Profit Margin adjustment ---
    def _inverse_profit_margin(self):
        """Update fixed_price based on manually updated profit margin."""
        for item in self:
            cost = item.product_cost
            if item.profit_margin < 1.0 and cost > 0:
                # Price = Cost / (1 - Margin)
                new_price = cost / (1.0 - item.profit_margin)
                if item.compute_price == 'fixed':
                    item.fixed_price = new_price
            elif item.profit_margin >= 1.0:
                # Prevent division by zero if user enters 100% margin or higher
                item.profit_margin = 0.9999
        # Force immediate recalculation of UI fields
        self._compute_product_financials()

    # --- INVERSE LOGIC 2: Markup adjustment ---
    def _inverse_markup_percent(self):
        """Update fixed_price based on manually updated markup percentage."""
        for item in self:
            cost = item.product_cost
            if cost > 0:
                # Price = Cost * (1 + Markup)
                new_price = cost * (1.0 + item.markup_percent)
                if item.compute_price == 'fixed':
                    item.fixed_price = new_price
        # Force immediate recalculation of UI fields
        self._compute_product_financials()

    # --- INVERSE LOGIC 3: Profit Amount adjustment ---
    def _inverse_profit_amount(self):
        """Update fixed_price based on manually updated profit amount."""
        for item in self:
            cost = item.product_cost
            new_price = cost + item.profit_amount
            if item.compute_price == 'fixed':
                item.fixed_price = new_price
        # Force immediate recalculation of UI fields
        self._compute_product_financials()