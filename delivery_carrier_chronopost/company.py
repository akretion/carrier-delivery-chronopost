# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Florian da Costa
#    Copyright 2013 Akretion
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


from openerp.osv import orm, fields

CHRONOPOST_FORMATS = [
    ('PDF', 'PDF'),
    ('SPD', 'SPD'),
    ('PPR', 'PPR'),
    ('THE', 'THE'),
    ('ZPL', 'ZPL'),
    ('XML', 'XML')
]


class ResCompany(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'chronopost_ids': fields.many2many('chronopost.config', 'company_chronopost_rel', 'company_id', 'chrono_id', 'Chronopost Accounts'),
        }
