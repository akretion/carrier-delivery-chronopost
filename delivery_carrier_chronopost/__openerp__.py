# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Florian da Costa
#    Copyright 2014 Akretion
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
{'name': 'Chronopost Labels WebService',
 'version': '1.1',
 'author': 'Akretion',
 'maintainer': 'Akretion',
 'category': 'version',
 'complexity': 'normal',
 'depends': [
        'base_delivery_carrier_label',
        'configuration_helper',],
 'description': """

Contributors
------------

* Florian da Costa <florian.dacosta@akretion.com>
""",
 'website': 'http://www.akretion.com/',
 'data': [
    "company_view.xml",
    "res_partner_data.xml",
    "product_data.xml",
    "delivery_data.xml",
    "config_view.xml",
    "stock_view.xml",
          ],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True,
 'external_dependencies': {
     'python': ['suds'],
 }
 }
