## About
This Odoo ERP module enables the ability to use the `explode` method of `mrp.bom` model via rpc. Traditionally this method would require a `product.product` recordset that is not possible via RPC. To reduce the amount of rpc calls, this method is now accessible via the `product.product` model, and it accepts multiple records.

## Usage

```python
# Get all product records
products = env['product.product'].search([])

products.explode( quantity = 1 )
```

## RPC Usage

```python
from xmlrpc import client

class OdooConnection:
    def __init__(self, host, database, username, password):
        self._host = host
        self._common_endpoint = client.ServerProxy(host + '/xmlrpc/2/common')
        self._object_endpoint = client.ServerProxy(host + '/xmlrpc/2/object')
        self._db = database
        self._pwd = password

        try:
            self._common_endpoint.version()
        except:
            print('Failed to connect to Odoo.')
            raise

        try:
            self._uid = self._common_endpoint.authenticate(database, username, password, {})
        except:
            print('Failed to authenticate with Odoo.')
            raise

    def execute_kw(self, model, method, *args, **kwargs):
        return self._object_endpoint.execute_kw(self._db, self._uid, self._pwd, model, method, args, kwargs)

def main():
    connection = OdooConnection(host=..., database=..., username=..., password=...)

    products = connection.execute_kw('product.product', 'search_read', [], ['id', 'display_name'])
    products_dict = {p['id']: p for p in products}

    exploded_products = connection.execute_kw('product.product', 'explode', [p['id'] for p in products], 1)

    for product_id, data in exploded_products:
        product = products_dict[product_id]
        print(f"{data['bom']['type']} - {product['display_name']}:")
        for component in data['components']:
            print(f"\t{component['qty']} {component['uom']['display_name']} of {component['product']['display_name']}")


if __name__ == '__main__':
    main()


```


## Example Output

```python
{
    '<Product ID>':{
        'bom': {
            'id': ..., 'display_name': ..., 'type': ...,
            # More fields can be configured via the (product.product)._explode_bom_fields method
        },
        'components':[{
            'product': {
                'id': ..., 'display_name': ..., 'default_code': ...,
                # More fields can be configured via the (product.product)._explode_product_product method
            },
            'uom': {
                'id': ..., 'display_name': ...,
                # More fields can be configured via the (product.product)._explode_product_uom method
            },
            'qty': ...
        }]
    },
}
```

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
