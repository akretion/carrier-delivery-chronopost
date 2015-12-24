# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Florian da Costa
#    Copyright 2014-2015 Akretion (http://www.akretion.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Chronopost Labels WebService',
    'version': '7.0.1.1.0',
    'author': 'Akretion',
    'category': 'Carrier',
    'depends': [
        'base_delivery_carrier_label',
        'configuration_helper',
        ],
    'description': """
With this module, you will be able to generate Chronopost labels directly via a webservice call and attach the ZPL files (or other formats) on the picking.

This module requires the chronopost_api python lib, available here: https://github.com/florian-dacosta/chronopost

Together with this module, you may be interested by the module *delivery_carrier_zpl_label_print* which adds a button *Print Delivery Labels* on delivery order form view to easily send the ZPL file to your label printer. This module requires the module *base_report_to_printer* with the code of this PR : https://github.com/OCA/report-print-send/pull/44

Contributors
------------

* Florian da Costa <florian.dacosta@akretion.com> (Main author)
* Alexis de Lattre <alexis.delattre@akretion.com>
""",
    'website': 'http://www.akretion.com/',
    'data': [
        "company_view.xml",
        "res_partner_data.xml",
        "product_data.xml",
        "delivery_data.xml",
        "config_view.xml",
        "security/ir.model.access.csv"
        ],
    'installable': True,
    'license': 'AGPL-3',
    'application': True,
    'external_dependencies': {
        #'python': ['suds', 'chronopost_api'],  # FIXME Unable to upgrade module "delivery_carrier_chronopost" because an external dependency is not met: No module named chronopost_api
        'python': ['suds'],
    }
}
