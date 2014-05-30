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
from operator import attrgetter

from openerp.osv import orm, fields
from suds.client import Client
from lib.chronopost import Chronopost
from datetime import datetime

#from postlogistics.web_service import PostlogisticsWebService

CHRONOPOST_FORMATS = [
    ('PDF', 'PDF'),
    ('SPD', 'SPD'),
    ('PPR', 'PPR'),
    ('THE', 'THE'),
    ('ZPL', 'ZPL'),
    ('XML', 'XML')
]


class chronopost_config(orm.Model):
    _name = 'chronopost.config'

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'account_num' : fields.char('Account Number', size=8, required=True),
        'sub_account_num' : fields.char('Sub Account Number', size=3),
        'password' : fields.char('Password', size=6, required=True),
        'label_type': fields.selection(
            CHRONOPOST_FORMATS,
            string="Label Format"),
        'use_esd': fields.boolean('Use ESD'),
    }


    def get_chronopost_account(self, cr, uid, chronos, pick, context=None):
        """
            If your company use more than one chronopost account, implement
            your method to return the right one depending of your picking.
        """
        return NotImplementedError


class chronopost_prepare_webservice(orm.Model):
    _name = 'chronopost.prepare.webservice'


    _CHRONOPOST_PRODUCT = {
        'Chrono 8': 75,
        'Chrono 9': 76,
        'Chrono 10': 02,
        'Chrono 13': 01,
        'Chrono 18': 16,
        'Chrono Express': 17,
        'Chrono Classic': 44,
        'Chrono Relais': 86
    }

    def _prepare_address(self, cr, uid, partner, context=None):
        address = {}
        for elm in ['street', 'street2', 'zip', 'city', 'phone', 'mobile', 'email']:
            address[elm] = getattr(partner, elm)
            if partner.country_id:
                address['country_code'] = partner.country_id.code
                address['country_name'] = partner.country_id.name
        return address


    def _prepare_recipient(self, cr, uid, picking, context=None):
        partner = picking.partner_id
        recipient_data = self._prepare_address(cr, uid, partner, context=context)
        recipient_data['name2'] = partner.name
        if partner.is_company and partner.child_ids:
            recipient_data['name'] = partner.child_ids[0].name
        else:
            recipient_data['name'] = ' '
        recipient_data['alert'] = int(self._get_single_option(
                                      picking, 'recipient_alert') or 0)
        
        return recipient_data
        

    def _prepare_shipper(self, cr, uid, picking, context=None):
        partner = picking.company_id.partner_id  #TODO install sale_flow_shop and shop_sender and replace by partner = self._customize_sender_address(cr, uid, pick, context=context) ==> change dependence in openerp.py for sale_flow_shop
        shipper_data = self._prepare_address(cr, uid, partner, context=context)
        if partner.is_company and partner.child_ids:
            shipper_data['name'] = partner.child_ids[0].name
        else:
            shipper_data['name'] = ' '
        shipper_data['civility'] = 'E' #FIXME
        shipper_data['name2'] = partner.name
        print "mmmmmm", self._get_single_option(
                                      picking, 'shipper_alert'), "kk"
        shipper_data['alert'] = int(self._get_single_option(
                                      picking, 'shipper_alert') or 0)
        return shipper_data


    def _prepare_customer(self, cr, uid, picking, context=None):
        """
        Use this method in the case the shipper address is different from the customer address
        """
        return None


    def _prepare_basic_ref(self, cr, uid, picking, context=None):
        ref_data = {
            'shipperRef': "Ref Shipper", #FIXME
            'recipientRef': "Ref Recipient", #FIXME  Code point relais si chrono relais
        }
        return ref_data


    def _get_single_option(self, picking, option):
        option = [opt.code for opt in picking.option_ids
                  if opt.chronopost_type == option]
        assert len(option) <= 1
        return option and option[0]


    def _complete_skybill(self, cr, uid, moves, context=None):
        res = {}
        picking = moves[0].picking_id
        res['weight'] = sum(move.weight for move in moves)
        product_total = int(sum(m.sale_line_id.price_subtotal if m.sale_line_id else 0 for m in moves) * 100)
        print "????????????????", product_total
        if self._get_single_option(picking, 'insurance'):
            res['insuredValue'] = product_total or None
        if picking.carrier_id.name == "Chrono Express":
            res['customsValue'] = product_total or None
        print context, "**"
        return res


    def _prepare_basic_skybill(self, cr, uid, picking, options, context=None):
        skybill_data = {
            'productCode': self._CHRONOPOST_PRODUCT[picking.carrier_id.name],
            'shipDate': datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            'shipHour': datetime.now().strftime("%H"),
            'weightUnit': 'KGM',
            #'codValue': TODO
        }
        skybill_data['service'] = self._get_single_option(
                                      picking, 'service') or '0'
        skybill_data['objectType'] = self._get_single_option(
                                        picking, 'object_type') or 'MAR'
        return skybill_data


    def _prepare_esd(self, cr, uid, track, context=None):
        esd_data = {
            'height': 0,
            'width': 0,
            'length': 0,
            }
        return esd_data


    def _prepare_account(self, cr, uid, chrono_config, picking, context=None):
        header_data =   {
            'accountNumber': chrono_config.account_num,
            'subAccount': chrono_config.sub_account_num or False,
        }
        password = chrono_config.password
        mode = chrono_config.label_type
        return header_data, password, mode



class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _generate_chronopost_label(self, cr, uid, picking,
                                      tracking_ids=None, context=None):
        """ Generate labels and write tracking numbers received """
        chronopost_obj = self.pool['chronopost.prepare.webservice']
        move_obj = self.pool['stock.move']
        company = picking.company_id
        options = [o.tmpl_option_id.name for o in picking.option_ids]
        if company.chronopost_ids:
            if len(company.chronopost_ids) == 1:
                chrono_config = company.chronopost_ids[0]
            else:
                chrono_obj = self.pool['chronopost.config']
                chrono_config = chrono_obj.get_chronopost_account(
                                                cr, uid, company.chronopost_ids, 
                                                picking, context=context)
        else:
            raise orm.except_orm('Error', 'You have to configurate a chronopost account for your company')
        context['chrono_account_name'] = chrono_config.account_name
        if tracking_ids is None:
            # get all the trackings of the picking
            # no tracking_id wil return a False, meaning that
            # we want a label for the picking
            trackings = sorted(set(
                line.tracking_id if line.tracking_id else False \
                    for line in picking.move_lines))
        else:
            # restrict on the provided trackings
            tracking_obj = self.pool['stock.tracking']
            trackings = tracking_obj.browse(cr, uid, tracking_ids,
                                            context=context)

        #get options
        if picking.option_ids:
            options = [o.tmpl_option_id.name for o in picking.option_ids]
        #prepare webservice datas
        recipient_data = chronopost_obj._prepare_recipient(cr, uid, picking, context=context)
        customer_data = chronopost_obj._prepare_customer(cr, uid, picking, context=context)

        shipper_data = chronopost_obj._prepare_shipper(cr, uid, picking, context=context)
        header_data, password, mode = chronopost_obj._prepare_account(cr, uid, chrono_config, picking, context=context)

        ref_data = chronopost_obj._prepare_basic_ref(cr, uid, picking, context=context)
        skybill_data = chronopost_obj._prepare_basic_skybill(cr, uid, picking, options, context=context)
        labels = []
        for track in trackings:
            if not track:
                # ignore lines without tracking when there is tracking
                # in a picking
                # Example: if I have 1 move with a tracking and 1
                # without, I will have [False, a_tracking] in
                # `trackings`. In that case, we are using packs, not the
                # picking for the tracking numbers.
                if len(trackings) > 1:
                    continue
                moves = [move for move in picking.move_lines]
                skybill_data.update(chronopost_obj._complete_skybill(cr, uid, moves, context=context))
                #skybill_data['weight'] += sum(move.weight for move in picking.move_lines)
                print "kk***********fffffffffffff", chronopost_obj._complete_skybill(cr, uid, moves, context=context), "ll", skybill_data
            else:
                moves = track.move_ids
                skybill_data.update(chronopost_obj._complete_skybill(cr, uid, moves, context=context))
                ref_data['customerSkybillNumber'] = track.name
            if chrono_config.use_esd:
                esd_data = chronopost_obj._prepare_esd(cr, uid, track, context=context)
            resp = Chronopost().get_shipping_label(recipient_data, shipper_data,
                                                   header_data, ref_data,
                                                   skybill_data, password,
                                                   esd=esd_data, mode=mode,
                                                   customer=customer_data)
                
            if 'errors' in resp:
                raise orm.except_orm('Error', '\n'.join(resp['errors']))
            label = resp['value']
            if label['errorCode'] != 0:
                raise orm.except_orm('Error', '\n'.join(label['errorMessage']))

            #copy tracking number on picking if only one pack or in tracking if several packs
            tracking_number = label['skybillNumber']
            if not track:
                self.write(cr, uid, picking.id,
                           {'carrier_tracking_ref': tracking_number},
                           context=context)
            else:
                track.write({'serial': tracking_number})

            file_type = 'pdf' if mode != 'ZPL' else 'zpl'
            labels.append({
                'file': label['skybill'].decode('base64'),
                'tracking_id': track.id if track else False,
                'file_type': file_type,
                'name': tracking_number + '.' + file_type,
            })
        return labels
           

    def generate_shipping_labels(self, cr, uid, ids, tracking_ids=None,
                                 context=None):
        """ Add label generation for Postlogistics """
        if isinstance(ids, (long, int)):
            ids = [ids]
        assert len(ids) == 1
        picking = self.browse(cr, uid, ids[0], context=context)
        if picking.carrier_id and picking.carrier_id.type == 'chronopost':
            return self._generate_chronopost_label(
                cr, uid, picking,
                tracking_ids=tracking_ids,
                context=context)
        return super(stock_picking, self).\
            generate_shipping_labels(cr, uid, ids, tracking_ids=tracking_ids,
                                     context=context)


class ShippingLabel(orm.Model):
    """ Child class of ir attachment to identify which are labels """
    _inherit = 'shipping.label'

    def _get_file_type_selection(self, cr, uid, context=None):
        """ Return a concatenated list of extensions of label file format
        plus file format from super

        This will be filtered and sorted in __get_file_type_selection

        :return: list of tuple (code, name)

        """
        file_types = super(ShippingLabel, self
                           )._get_file_type_selection(cr, uid, context=context)
        new_types = [('zpl', 'ZPL')]
        file_types.extend(new_types)
        return file_types



