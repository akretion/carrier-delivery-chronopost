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
from . company import ResCompany


class CarrierAccount(orm.Model):
    _inherit = 'carrier.account'

    def _get_carrier_type(self, cr, uid, context=None):
        """ To inherit to add carrier type like Chronopost, Postlogistics..."""
        res = super(CarrierAccount, self)._get_carrier_type(cr, uid, context=context)
        res.append(('chronopost', 'Chronopost'))
        return res

    def _get_file_format(self, cr, uid, context=None):
        """ To inherit to add carrier type like Chronopost, Postlogistics..."""
        res = super(CarrierAccount, self)._get_file_format(cr, uid, context=context)
        res.extend((('SPD', 'SPD'),
                   ('PPR', 'PPR'),
                   ('THE', 'THE')))
        return res


class ChronopostAccount(orm.Model):
    _name = 'chronopost.account'
    _inherits = {'carrier.account': 'account_id'}
    _rec_name = 'account_id'
    _columns = {
        'account_id': fields.many2one('carrier.account', 'Main Account'),
        'sub_account' : fields.char('Sub Account Number', size=3),
        'company_id': fields.many2one('res.company', 'Company'),
        'use_esd': fields.boolean('Use ESD'),
    }


class ChronopostConfig(orm.Model):
    _name = 'chronopost.config'
    _inherit = ['res.config.settings', 'abstract.config.settings']
    _prefix = 'chronopost_'
    _companyObject = ResCompany



