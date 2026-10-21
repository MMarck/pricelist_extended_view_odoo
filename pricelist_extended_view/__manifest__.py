{
    'name': 'Pricelist Extended View - Financial Matrix',
    'version': '18.0.1.0.0',
    "author": "MR.Marck",
    "license": "LGPL-3",
    "summary": "Add a new view to the pricing rules to filter and display financial metrics such as cost, profit margin, and markup percentage.",
    "description": "This module extends the functionality of the product pricelist view in Odoo by adding a new view that allows users to filter and display financial metrics such as cost, profit margin, and markup percentage. It provides a more comprehensive overview of pricing rules, enabling better decision-making for sales and pricing strategies.",
    "price": 0.00,
    "currency": "USD",
    'category': 'Sales',
    "website": "https://mrmarck.com/pricelist_extended_view",
    'summary': 'Add a new view to the pricing rules to filter and display financial metrics such as cost, profit margin, and markup percentage.',
    'depends': [
        'product',
        'sale'
    ],
    'post_init_hook': 'enable_pricelist_setting',
    'data': [
        'views/product_pricelist_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pricelist_extended_view/static/src/js/pricelist_list_controller.js',
        ],
    },
    "images": ["static/description/banner.png"],
    'installable': True,
    'application': False,
}