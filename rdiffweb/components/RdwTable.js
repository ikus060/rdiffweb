// rdiffweb, A web interface to rdiff-backup repositories
// Copyright (C) 2012-2025 rdiffweb contributors
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

const DATE_PATTERN = /^(\d\d\d\d)(\-)?(\d\d)(\-)?(\d\d)$/i;
function rdwToDate(n) {
    let matches, year, month, day;
    if (typeof n === "number") {
        n = new Date(n * 1000); // epoch
    } else if ((matches = n.match(DATE_PATTERN))) {
        year = parseInt(matches[1], 10);
        month = parseInt(matches[3], 10) - 1;
        day = parseInt(matches[5], 10);
        return new Date(year, month, day);
    } else { // str
        n = isNaN(n) ? new Date(n) : new Date(parseInt(n) * 1000);
    }
    return n;
}

$(document).ready(function () {
    /** Render string as safe value for html. */
    function safe(value) {
        return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    /** Date time value */
    $.fn.dataTable.render.datetime = function () {
        return {
            display: function (data, type, row, meta) {
                return rdwToDate(data).toLocaleString();
            },
            sort: function (data, type, row, meta) {
                return rdwToDate(data).getTime();
            }
        };
    }

    $.fn.dataTable.render.filesize = function () {
        const UNITS = [' bytes', ' KiB', ' MiB', ' GiB', ' TiB'];
        function toFileSize(value) {
            value = parseInt(value);
            if (isNaN(value)) {
                return data;
            }
            let i = 0;
            while (value > 1024 && i < UNITS.length) {
                value /= 1024;
                i++;
            }
            return value.toFixed(1).replace('.0', '') + UNITS[i];
        }

        return {
            display: function (data, type, row, meta) {
                if (!data || data == '' || data == 'NA') {
                    return data
                }
                return toFileSize(data);
            },
            sort: function (data, type, row, meta) {
                const value = parseInt(data);
                return isNaN(value) ? -1 : value;
            }
        };
    }

    $.fn.dataTable.render.summary = function (render_arg) {
        let icon_table = {
            'user': 'bi-person-fill',
            'repo': 'bi-archive'
        };

        const model_name = typeof render_arg === 'string' ? render_arg : null;
        const model_name_column = render_arg?.model_name_column || 'model_name:name';
        const url_column = render_arg?.url_column || 'url:name';

        return {
            display: function (data, type, row, meta) {
                if (!data) return '-';
                const api = new $.fn.dataTable.Api(meta.settings);
                /* Get model_name from arguments or from row data */
                let effective_model_name = model_name;
                if (effective_model_name == null) {
                    const model_idx = api.column(model_name_column).index();
                    if (model_idx) {
                        effective_model_name = row[model_idx];
                    }
                }

                /* Define the URL */
                let url = "#";
                const url_idx = api.column(url_column).index();
                if (url_idx) {
                    url = encodeURI(row[url_idx])
                }

                let html = '<a href="' + url + '">' +
                    '<i class="bi ' + icon_table[effective_model_name] + ' me-1" aria-hidden="true"></i>' +
                    '<strong>' + safe(data) + '</strong>' +
                    '</a>';

                return html;
            },
            sort: function (data, type, row, meta) {
                return data;
            }
        };
    }

    $.fn.dataTable.render.changes = function () {
        return {
            display: function (data, type, row, meta) {
                const api = new $.fn.dataTable.Api(meta.settings);
                let html = '';
                const body_idx = api.column('body:name').index();
                if (body_idx && row[body_idx]) {
                    html += safe(row[body_idx]);
                }
                const type_idx = api.column('type:name').index();
                if (data) {
                    const null_value = api.settings().i18n(`rdiffweb.null`, 'undefined')
                    html += '<ul class="mb-0">';
                    if (row[type_idx] === 'new') {
                        /* For new record display only the new value. */
                        for (const [key, values] of Object.entries(data)) {
                            const field_name = safe(api.settings().i18n(`rdiffweb.field.${key}`, key));
                            if (values[1] !== null) {
                                const new_value = safe(api.settings().i18n(`rdiffweb.value.${key}.${values[1]}`, `${values[1]}`));
                                html += '<li><strong>' + field_name + '</strong>: ' + new_value + ' </li>';
                            }
                        }
                    } else {
                        /* For updates, display old and new value */
                        for (const [key, values] of Object.entries(data)) {
                            const field_name = safe(api.settings().i18n(`rdiffweb.field.${key}`, key));
                            html += '<li><strong>' + field_name + '</strong>: '
                            if (Array.isArray(values[0])) {
                                for (const deleted of values[0]) {
                                    html += '<br/> - ' + safe(deleted);
                                }
                                for (const added of values[1]) {
                                    html += '<br/> + ' + safe(added);
                                }
                            } else {
                                const old_value = safe(api.settings().i18n(`rdiffweb.value.${key}.${values[0]}`, `${values[0] !== null ? values[0] : undefined}`));
                                const new_value = safe(api.settings().i18n(`rdiffweb.value.${key}.${values[1]}`, `${values[1] !== null ? values[1] : undefined}`));
                                html += old_value + ' → ' + new_value + '</li>';
                            }
                        }
                    }
                    html += '</ul>';
                }
                return html;
            }
        };
    }

    $.fn.dataTable.render.message_body = function () {

        const changes = $.fn.dataTable.render.changes().display;

        const datetime = $.fn.dataTable.render.datetime().display;

        return {
            display: function (data, type, row, meta) {
                const api = new $.fn.dataTable.Api(meta.settings);
                let html = '';

                const type_idx = api.column('type:name').index();
                if (type_idx !== undefined) {
                    const type = row[type_idx];
                    html += api.settings().i18n(`rdiffweb.value.type.${type}`, type);
                }

                const author_idx = api.column('author:name').index();
                if (author_idx !== undefined) {
                    html += ' <em>' + row[author_idx] + '</em>';
                }

                const date_idx = api.column('date:name').index();
                if (date_idx !== undefined) {
                    html += ' • ' + datetime(row[date_idx], type, row, meta);
                }

                html += '<br />'

                html += changes(data, type, row, meta);

                return html;
            },
            sort: function (data, type, row, meta) {
                const api = new $.fn.dataTable.Api(meta.settings);
                const date_idx = api.column('date:name').index();
                const value = rdwToDate(row[date_idx]);
                return value ? value.getTime() : 0;
            },
        };
    }
});