{
    'name': 'Custom Pricelist List View',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Reemplaza la vista estática de reglas de precio por una lista editable',
    'depends': ['product', 'sale'],
    'data': [
        'views/product_pricelist_views.xml',
    ],
    'installable': True,
    'application': False,
}