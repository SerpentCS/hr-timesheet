# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
#    Copyright (C) 2015 SerpentCS
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tests import common
from datetime import datetime
from openerp.osv.orm import except_orm


class TestHrTimesheetSheetPeriod(common.TransactionCase):

    def setUp(self):
        super(TestHrTimesheetSheetPeriod, self).setUp()
        self.data_model = self.registry('ir.model.data')
        self.user_model = self.registry("res.users")
        self.company_model = self.registry('res.company')
        self.timeheet_model = self.registry('hr_timesheet_sheet.sheet')
        self.fiscal_year_model = self.registry('hr.fiscalyear')
        self.employee_model = self.registry('hr.employee')

        self.today_date = datetime.today().date()
        self.date_start = datetime.today().strftime('%Y-01-01')
        self.date_stop = datetime.today().strftime('%Y-12-31')
        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context
        self.company_id = self.company_model.\
            create(cr, uid, {'name': 'Test Company'}, context=context)

        self.user = self.data_model.get_object(cr, uid, 'base', 'user_root')
        fiscal_year = self.create_fiscal_year()
        fiscal_year.create_periods()
        fiscal_year.button_confirm()
        self.hts = self.create_hr_timesheet_sheet()
        self.hts.button_confirm()

    def create_fiscal_year(self, vals=None):
        cr, uid, context = self.cr, self.uid, self.context
        self.vals = {
            'company_id': self.company_id,
            'date_start': self.date_start,
            'date_stop': self.date_stop,
            'schedule_pay': 'monthly',
            'payment_day': '2',
            'name': 'Test Fiscal Year 2017',
        }
        if vals is None:
            vals = {}

        self.vals.update(vals)
        fy_id = self.fiscal_year_model.create(cr, uid, self.vals,
                                              context=context)

        return self.fiscal_year_model.browse(cr, uid, fy_id, context=context)

    def create_hr_timesheet_sheet(self, vals=None):
        cr, uid, context = self.cr, self.uid, self.context
        employee_id = self.employee_model.create(cr, uid,
                                                 {'name': 'Test Employee',
                                                  'user_id': self.user.id},
                                                 context=context)
        self.vals = {'employee_id': employee_id}
        if vals is None:
            vals = {}

        self.vals.update(vals)
        self.hts_id = self.timeheet_model.create(cr, uid, self.vals,
                                                 context=context)
        return self.timeheet_model.browse(cr, uid, self.hts_id,
                                          context=context)

    def test_hr_timesheet_period(self):
        self.assertEqual(self.hts.hr_period_id.date_start, self.hts.date_from)
        self.assertEqual(self.hts.hr_period_id.date_stop, self.hts.date_to)
        self.assertEqual(self.today_date.month, self.hts.hr_period_id.number)
        self.assertRaises(except_orm, self.timeheet_model.write,
                          self.cr, self.uid, [self.hts_id],
                          {'date_to': '2015-12-31'}, context=self.context)
