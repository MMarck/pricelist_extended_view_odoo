{
    'name': 'Pricelist Extended View - Financial Matrix',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Add a new view to the pricing rules to filter and display financial metrics such as cost, profit margin, and markup percentage.',
    'depends': ['product', 'sale'],
    'data': [
        'views/product_pricelist_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pricelist_extended_view/static/src/js/pricelist_list_controller.js',
        ],
    },
    'installable': True,
    'application': False,
}