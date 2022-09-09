from odoo import models, api, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _explode_mrp_bom_fields(self):
        return ['id', 'display_name', 'type']

    @api.model
    def _explode_product_product_fields(self):
        return ['id', 'display_name', 'default_code']

    @api.model
    def _explode_product_uom_fields(self):
        return ['id', 'display_name']

    def explode(self, quantity, picking_type_id=None, company_id=None):
        picking_type = self.env['stock.picking.type'].browse(picking_type_id)
        boms = self.env['mrp.bom']._bom_find(self, picking_type=picking_type, company_id=company_id)
        res = []
        for product in self:
            if product not in boms:
                continue
            bom = boms[product]
            exploded_boms, exploded_bom_lines = bom.explode(product, quantity, picking_type=picking_type)
            components = {}
            for line, data in exploded_bom_lines:
                key = (line.product_id.id, line.product_uom_id.id)
                component_template = {
                    'product': line.product_id.read(self._explode_product_product_fields())[0],
                    'uom': line.product_uom_id.read(self._explode_product_uom_fields())[0],
                    'qty': 0
                }
                components.setdefault(key, component_template)
                components[key]['qty'] += data['qty']

            res.append((product.id, {
                'bom': bom.read(self._explode_mrp_bom_fields())[0],
                'components': list(components.values())
            }))

        return res
