# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug.exceptions import NotFound

from odoo.http import Controller, request, route, content_disposition
import logging

_logger = logging.getLogger(__name__)


class EventController(Controller):

    @route(['''/event/<model("event.event"):event>/ics'''], type='http', auth="public")
    def event_ics_file(self, event, **kwargs):
        lang = request.context.get('lang', request.env.user.lang)
        if request.env.user._is_public():
            lang = request.httprequest.cookies.get('frontend_lang')
        event = event.with_context(lang=lang)
        files = event._get_ics_file()
        if not event.id in files:
            return NotFound()
        content = files[event.id]
        return request.make_response(content, [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Length', len(content)),
            ('Content-Disposition', content_disposition('%s.ics' % event.name))
        ])

    @route('/event/<int:event_id>/export', type='http', auth='user')
    def export_event(self, event_id):
        _logger.info('export_event method called')

        # Get the event
        event = request.env['event.event'].browse(event_id)

        # Export the data to CSV
        data = event.export_all_registrations_to_csv()

        # Create a response
        filename = f'{event.name}_registrations.csv'
        response = request.make_response(data,
                                         headers=[('Content-Type', 'text/csv'),
                                                  ('Content-Disposition', f'attachment; filename={filename}')])

        _logger.info('export_event method finished')

        return response