// rdiffweb, A web interface to rdiff-backup repositories
// Copyright (C) 2012-2021 rdiffweb contributors
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
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Convert a value to a date.
 */
var DATE_PATTERN = /^(\d\d\d\d)(\-)?(\d\d)(\-)?(\d\d)$/i;
function toDate(n) {
  var matches, year, month, day;
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

  /**
   * Handle flexible Ajax form submit.
   */
  $('form[data-async]').on('submit', function (event) {
    var $form = $(this);
    var $target = $($form.attr('data-target'));
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
    var t = $(this);
    var d = toDate(t.attr('datetime'));
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
  action: function (e, dt, node, config) {
    if (node.hasClass('active')) {
      dt.column(config.column).search('');
    } else {
      dt.column(config.column).search(config.search);
    }
    // Update each buttons status
    dt.buttons().each(function (data, idx) {
      let conf = data.inst.s.buttons[idx].conf;
      if (conf && conf.column) {
        dt.button(idx).active(dt.column(conf.column).search() === conf.search);
      }
    });
    dt.draw(true);
  }
};