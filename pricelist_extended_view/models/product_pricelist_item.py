# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    product_cost = fields.Float(
        string='Cost',
        compute='_compute_product_cost',
        digits='Product Price',
        search='_search_product_cost',
        store=True,
        compute_sudo=True,
        help='Standard cost of the product variant or template associated with this pricelist item'
    )
    
    profit_amount = fields.Float(
        string='Profit',
        compute='_compute_product_financials',
        digits='Product Price',
        store=True,
        inverse='_inverse_profit_amount',
        help='Profit in monetary value (Price - Cost). It can only be edited if compute_price is set to "Fixed price" or "Discount".'
    )
    
    profit_margin = fields.Float(
        string='Profit Margin (%)',
        compute='_compute_product_financials',
        digits=(16, 2),
        store=True,
        inverse='_inverse_profit_margin',
        help='Profit margin percentage over the selling price: ((Price - Cost) / Price) * 100. It can only be edited if compute_price is set to "Fixed price" or "Discount".'
    )

    markup_percent = fields.Float(
        string='Markup (%)',
        compute='_compute_product_financials',
        digits=(16, 2),
        store=True,
        inverse='_inverse_markup_percent',
        help='Percentage of markup over the cost: ((Price - Cost) / Cost) * 100. It can only be edited if compute_price is set to "Fixed price" or "Discount".'
    )

    currency_id = fields.Many2one(
        related='pricelist_id.currency_id',
        string='Currency',
        readonly=True,
    )

    @api.depends(
        'product_id', 
        'product_id.standard_price', 
        'product_tmpl_id', 
        'product_tmpl_id.standard_price', 
        'applied_on',
        'company_id'  
    )
    def _compute_product_cost(self):
        """Compute standard cost taking into account the active company context."""
        for item in self:
            # 1. Determine the company of the record or the current user's company
            company = item.company_id or item.pricelist_id.company_id or self.env.company

            # 2. Assign the environment with the context of the specific company
            item_with_company = item.with_company(company)

            cost = 0.0

            # Case 1: Product Variant
            if item_with_company.applied_on == '0_product_variant' and item_with_company.product_id:
                cost = item_with_company.product_id.standard_price

            # Case 2: Product Template (product.template)
            elif item_with_company.applied_on == '1_product' and item_with_company.product_tmpl_id:
                cost = item_with_company.product_tmpl_id.standard_price

            # Case 3 (Fallback to template if variant has no direct cost)
            elif item_with_company.product_tmpl_id:
                cost = item_with_company.product_tmpl_id.standard_price

            item.product_cost = cost

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
            product = None
            if item.applied_on == '0_product_variant' and item.product_id:
                product = item.product_id
            elif item.applied_on == '1_product' and item.product_tmpl_id:
                product = item.product_tmpl_id

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
            if price_val and item.product_cost:
                profit = price_val - item.product_cost
                item.profit_amount = profit
                item.profit_margin = (profit / price_val) if price_val > 0 else 0.0
                item.markup_percent = (profit / item.product_cost) if item.product_cost > 0 else 0.0
            elif price_val:
                item.profit_amount = price_val
                item.profit_margin = 1.0
                item.markup_percent = 0.0
            else:
                item.profit_amount = -item.product_cost if item.product_cost else 0.0
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
        """Abre la vista de ventas asociadas a la Variante, Producto o Categoría

        preservando el contexto y filtros activos del usuario.
        """
        self.ensure_one()
        
        # 1. Define the base domain according to the rule type
        domain = [('state', 'not in', ['cancel'])]
        title_name = "Sales analysis"

        if self.applied_on == '0_product_variant' and self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
            title_name = f"{self.product_id.display_name} - Sales analysis"
        elif self.applied_on == '1_product' and self.product_tmpl_id:
            domain.append(('product_tmpl_id', '=', self.product_tmpl_id.id))
            title_name = f"{self.product_tmpl_id.name} - Sales analysis"
        elif self.applied_on == '2_product_category' and self.categ_id:
            item_category = self.categ_id
            domain.append(('categ_id', 'child_of', item_category.id))
            title_name = f"{item_category.name} - Sales analysis"
        else:
            return {'type': 'ir.actions.act_window_close'}

        # 2. Load the base action for the sales report from Odoo
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_order_report_all")
        
        # 3. Preserve the current user context and combine it with the action's context
        ctx = dict(self.env.context)
        # Optional: if the base action has a default context, we combine it
        if action.get('context'):
            eval_ctx = eval(action['context']) if isinstance(action['context'], str) else action['context']
            ctx.update(eval_ctx)

        # set context to the action, including the preserved user context and any additional parameters
        action['name'] = title_name
        action['domain'] = domain
        action['context'] = ctx
        
        # 4. Ensure that the flat list view is the first option in the action's views
        action['views'] = [
            (False, 'list'),
            (self.env.ref('sale.view_order_product_pivot').id, 'pivot'),
            (self.env.ref('sale.view_order_product_graph').id, 'graph'),
        ]
        action['target'] = 'current'
        
        return action

    def _get_base_sales_price(self, item):
        """Auxiliary method to get the base sales price according to the rule."""
        if item.applied_on == '0_product_variant' and item.product_id:
            return item.product_id.list_price
        elif item.applied_on == '1_product' and item.product_tmpl_id:
            return item.product_tmpl_id.list_price
        elif item.applied_on == '2_product_category' and item.categ_id:
            tmpl = self.env['product.template'].search([('categ_id', '=', item.categ_id.id)], limit=1)
            return tmpl.list_price if tmpl else 0.0
        return 0.0

    def _update_rule_price(self, item, target_price):
        """Update the rule based on whether it's Fixed Price or Percentage Discount."""
        if item.compute_price == 'fixed':
            item.fixed_price = target_price
        elif item.compute_price == 'percentage':
            base_price = self._get_base_sales_price(item)
            if base_price > 0:
                # Discount % = (1 - Target_Price / Base_Price) * 100
                discount_percent = (1.0 - (target_price / base_price)) * 100.0
                item.percent_price = round(discount_percent, 2)

    # --- INVERSE LOGIC 1: Profit Margin adjustment ---
    def _inverse_profit_margin(self):
        """Update price or discount based on manually updated profit margin."""
        for item in self:
            cost = item.product_cost
            if item.profit_margin < 1.0 and cost > 0:
                # Price = Cost / (1 - Margin)
                target_price = cost / (1.0 - item.profit_margin)
                self._update_rule_price(item, target_price)
            elif item.profit_margin >= 1.0:
                # Avoid division by zero if 100% or more is entered
                item.profit_margin = 0.9999
        self._compute_product_financials()

    # --- INVERSE LOGIC 2: Markup adjustment ---
    def _inverse_markup_percent(self):
        """Update price or discount based on manually updated markup percentage."""
        for item in self:
            cost = item.product_cost
            if cost > 0:
                # Price = Cost * (1 + Markup)
                target_price = cost * (1.0 + item.markup_percent)
                self._update_rule_price(item, target_price)
        self._compute_product_financials()

    # --- INVERSE LOGIC 3: Profit Amount adjustment ---
    def _inverse_profit_amount(self):
        """Update price or discount based on manually updated profit amount."""
        for item in self:
            cost = item.product_cost
            target_price = cost + item.profit_amount
            self._update_rule_price(item, target_price)
        self._compute_product_financials()


    # --- MÉTODOS DE BÚSQUEDA PERSONALIZADOS ---

    def _search_product_cost(self, operator, value):
        matching_products = self.env['product.product'].search([('standard_price', operator, value)])
        matching_templates = self.env['product.template'].search([('standard_price', operator, value)])
        return [
            '|',
            '&', ('applied_on', '=', '0_product_variant'), ('product_id', 'in', matching_products.ids),
            '&', ('applied_on', '=', '1_product'), ('product_tmpl_id', 'in', matching_templates.ids)
        ]

    def _search_profit_amount(self, operator, value):
        # Permite buscar en la base de datos comparando (precio - costo)
        return [('profit_amount', operator, value)]

    def _search_profit_margin(self, operator, value):
        return [('profit_margin', operator, value)]

    def _search_markup_percent(self, operator, value):
        return [('markup_percent', operator, value)]