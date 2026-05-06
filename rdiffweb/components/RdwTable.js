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

// reuse DataTables' built-in text escaper
const escapeHtml = DataTable.render.text().display; 

// Used to format i18n string
function rdwFormat(str, params) {
    return str.replace(/\{(\w+)\}/g, (match, key) => 
        params[key] !== undefined 
            ? `<strong>${escapeHtml(String(params[key]))}</strong>` 
            : match
    );
}

$(document).ready(function () {

    /** Date time value */
    $.fn.dataTable.render.datetime = function () {
        return {
            display(data) {
                const d = rdwToDate(data);
                const date = d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
                const time = d.toLocaleTimeString();
                return `<span class="fw-semibold small">${date}</span><br>
                        <span class="text-muted small">${time}</span>`;
            },
            sort(data) {
                return rdwToDate(data).getTime();
            },
        };
    };

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

    $.fn.dataTable.render.changes = function () {

        return {
            display: function (data, type, row, meta) {
                const api = new $.fn.dataTable.Api(meta.settings);
                const i18n = (key, fallback) => api.settings().i18n(key, fallback);
                let html = '';

                const body_idx = api.column('body:name').index();
                if (body_idx && row[body_idx]) {
                    html += escapeHtml(row[body_idx]);
                }

                if (data) {
                    const type_idx = api.column('type:name').index();
                    html += '<ul class="mb-0">';

                    for (const [key, values] of Object.entries(data)) {
                        const field_name = escapeHtml(i18n(`rdiffweb.field.${key}`, key));

                        if (row[type_idx] === 'new') {
                            if (values[1] !== null) {
                                const new_value = escapeHtml(i18n(`rdiffweb.value.${key}.${values[1]}`, `${values[1]}`));
                                html += `<li><strong>${field_name}</strong>: ${new_value}</li>`;
                            }
                        } else if (Array.isArray(values[0])) {
                            html += `<li><strong>${field_name}</strong>:`;
                            for (const deleted of values[0]) {
                                html += `<br/> - ${escapeHtml(deleted)}`;
                            }
                            for (const added of values[1]) {
                                html += `<br/> + ${escapeHtml(added)}`;
                            }
                            html += `</li>`;
                        } else {
                            const old_value = escapeHtml(i18n(`rdiffweb.value.${key}.${values[0]}`, `${values[0] ?? undefined}`));
                            const new_value = escapeHtml(i18n(`rdiffweb.value.${key}.${values[1]}`, `${values[1] ?? undefined}`));
                            html += `<li><strong>${field_name}</strong>: ${old_value} → ${new_value}</li>`;
                        }
                    }

                    html += '</ul>';
                }

                return html;
            }
        };
    };

    $.fn.dataTable.render.message_details = function () {

        const changes = $.fn.dataTable.render.changes().display;

        const datetime = $.fn.dataTable.render.datetime().display;

        return {
            display: function (data, type, row, meta) {
                const api = new $.fn.dataTable.Api(meta.settings);
                let html = '';

                // Provide detault string for modification, creation, etc.
                if(row.type) {
                    const message_subject = api.settings().i18n(`rdiffweb.message_details.${row.model_name}.${row.type}`);
                    if(message_subject) {
                        html += rdwFormat(message_subject, {model_name: escapeHtml(row.model_name), model_summary: escapeHtml(row.model_summary), author_username: escapeHtml(row.author_username)})
                    }
                }
                
                if(row.body) {
                    html += escapeHtml(row.body)
                }

                const changes_html = changes(data, type, row, meta)
                if(changes_html) {
                    html += '<br />'
                    html += changes_html;
                }
                return html;
            },
        };
    }

    $.fn.dataTable.render.actor = function () {

        return {
            display(data) {
                if (!data) {
                    return `<span class="text-muted">&mdash;</span>`;
                }
                const safe = escapeHtml(data);
                return `<span class="badge text-bg-secondary">
                            <i class="bi bi-person-fill me-1"></i>${safe}
                        </span>`;
            },
        };
    };

});