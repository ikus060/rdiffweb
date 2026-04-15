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

document.addEventListener('DOMContentLoaded', function () {
  
  /* Enable Bootstrap tooltip */
  window.appTooltips = new bootstrap.Tooltip(document.body, {
      selector: '[data-bs-toggle="tooltip"]',
      container: 'body',
      delay:  {'show': 500, 'hide': 500},
  });

});
