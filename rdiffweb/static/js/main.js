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

/**
 * Convert a value to a date.
 */
const DATE_PATTERN = /^(\d\d\d\d)(\-)?(\d\d)(\-)?(\d\d)$/i;
function toDate(n) {
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

$(document).ready(function () {
  
  /* Enable Bootstrap tooltip */
  $('[data-toggle="tooltip"]').tooltip();

  /**
   * Handle flexible Ajax form submit.
   */
  $('form[data-async]').on('submit', function (event) {
    const $form = $(this);
    const $target = $($form.attr('data-target'));
    $.ajax({
      headers: {
        Accept: "text/plain; charset=utf-8",
      },
      type: $form.attr('method'),
      url: $form.attr('action'),
      data: $form.serialize(),
      success: function (data, status) {
        $target.html('<i class="fa fa-check text-success" aria-hidden="true"></i> ' + data);
      },
      error: function (data, status, e) {
        $target.html('<i class="fa-exclamation-circle" aria-hidden="true"></i> ' + data.responseText);
      },
    });
    event.preventDefault();
  })

  /**
   * Handle local datetime using <time datetime="value"></time>. 
   * Uses the value of `datetime` to converted it into local timezone. 
   * Class `js-date` could be used to only display the date portion. e.g.: 2021-05-28
   * Class `js-datetime` could be used to display the date and time portion e.g.: 2021-05-28 1:04pm
   * Class `js-time` could be used to display the time portion. e.g.: 1:04 pm
   */
  $('time[datetime]').each(function () {
    const t = $(this);
    const d = toDate(t.attr('datetime'));
    if (t.hasClass("js-date")) {
      t.attr('title', d.toLocaleDateString());
      t.text(d.toLocaleDateString());
    } else if ($(this).hasClass("js-datetime")) {
      t.attr('title', d.toLocaleString());
      t.text(d.toLocaleString());
    } else if ($(this).hasClass("js-time")) {
      t.attr('title', d.toLocaleString());
      t.text(d.toLocaleTimeString());
    } else {
      t.attr('title', d.toLocaleString());
    }
  })

});

/** Filter button for DataTables */
$.fn.dataTable.ext.buttons.filter = {
  text: 'Filter',
  init: function (dt, node, config) {
    const that = this;
    dt.on('search.dt', function () {
      const activate = dt.column(config.column).search() === config.search;
      that.active(activate);
    });
  },
  action: function (e, dt, node, config) {
    if (node.hasClass('active')) {
      dt.column(config.column).search(config.search_off || '', config.regex);
    } else {
      dt.column(config.column).search(config.search, config.regex);
    }
    dt.draw(true);
  }
};

/** Button to clear filter and reset the state of the table. */
$.fn.dataTable.ext.buttons.clear = {
  text: 'All',
  action: function (e, dt, node, config) {
    dt.search('');
    if (dt.init().aoSearchCols) {
      const searchCols = dt.init().aoSearchCols;
      for (let i = 0; i < searchCols.length; i++) {
        const search = searchCols[i].search || "";
        dt.column(i).search(search);
      }
    } else {
      dt.columns().search('');
    }
    dt.draw(true);
  }
};

/** Render string as safe value for html. */
function safe(value) {
  return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/** Date time value */
$.fn.dataTable.render.datetime = function () {
  return {
    display: function (data, type, row, meta) {
      return toDate(data).toLocaleString();
    },
    sort: function (data, type, row, meta) {
      return toDate(data).getTime();
    }
  };
}

$.fn.dataTable.render.choices = function (choices) {
  return {
    display: function (data, type, row, meta) {
      for (const choice of choices) {
        if (choice[0] == data) {
          return choice[1];
        }
      }
      return data;
    },
  };
}

$.fn.dataTable.render.filesize = function () {
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
                        if(values[1] !== null ) {
                            const new_value = safe(api.settings().i18n(`rdiffweb.value.${key}.${values[1]}`, `${values[1]}` )) ;
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
                            const old_value = safe(api.settings().i18n(`rdiffweb.value.${key}.${values[0]}`, `${values[0] !== null ? values[0] : undefined }`)) ;
                            const new_value = safe(api.settings().i18n(`rdiffweb.value.${key}.${values[1]}`, `${values[1] !== null ? values[1] : undefined }`)) ;
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

    const datetime = $.fn.dataTable.render.datetime().display;

    const changes = $.fn.dataTable.render.changes().display;

    return {
        display: function (data, type, row, meta) {
            const api = new $.fn.dataTable.Api(meta.settings);
            let html = '';

            const type_idx = api.column('type:name').index();
            if (type_idx) {
                const type = row[type_idx];
                html += api.settings().i18n(`rdiffweb.value.type.${type}`, type);
            }

            const author_idx = api.column('author:name').index();
            if (author_idx) {
                html += ' <em>' + row[author_idx] + '</em> • ';
            }

            const date_idx = api.column('date:name').index();
            if (date_idx) {
                html += datetime(row[date_idx], type, row, meta);
            }

            html += '<br />' + changes(data, type, row, meta);
            return html;
        },
        sort: function (data, type, row, meta) {
            const api = new $.fn.dataTable.Api(meta.settings);
            const date_idx = api.column('date:name').index();
            const value = toDate(row[date_idx]);
            return value ? value.getTime() : 0;
        },
    };
}

jQuery(function () {
  $('table[data-ajax]').each(function (_idx) {
    /* Load column properties */
    let columns = $(this).attr('data-columns');
    $(this).removeAttr('data-columns');
    columns = JSON.parse(columns);
    $.each(columns, function (_index, item) {
      /* process the render attribute as a function. */
      if (item['render']) {
        if (item['render_arg']) {
          item['render'] = $.fn.dataTable.render[item['render']](item['render_arg']);
        } else {
          item['render'] = $.fn.dataTable.render[item['render']]();
        }
      }
      /* 
       * Patch column visibility for responsive<2.0.0 
       * Ref:https://datatables.net/extensions/responsive/classes
       */
      if ('visible' in item && !item['visible']) {
        item['className'] = 'never';
      }
    });
    let searchCols = columns.map(function (item, _index) {
      if (item.search) {
        return { "search": item.search };
      }
      return null;
    });
    let dt = $(this).DataTable({
      columns: columns,
      searchCols: searchCols,
      drawCallback: function (_settings) {
        // Remove sorting class
        this.removeClass(function (_index, className) {
          return className.split(/\s+/).filter(function (c) {
            return c.startsWith('sorted-');
          }).join(' ');
        });
        // Add sorting class when sorting without filter
        if (this.api().order() && this.api().order()[0] && this.api().order()[0][1] === 'asc' && this.api().order()[0][0] >= 0 && this.api().search() === '') {
          this.addClass('sorted-' + this.api().order()[0][0]);
        }
      },
      initComplete: function () {
        $(this).removeClass("no-footer");
      },
      processing: true,
      stateSave: true,
      deferRender: true,
    });
    // Update each buttons status
    dt.on('search.dt', function (e, settings) {
      dt.buttons().each(function (data, idx) {
        let conf = data.inst.s.buttons[idx].conf;
        if (conf && conf.column) {
          dt.button(idx).active(dt.column(conf.column).search() === conf.search);
        }
      });
    });
  });
});