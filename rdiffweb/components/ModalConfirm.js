// rdiffweb, A web interface to rdiff-backup repositories
// Copyright (C) 2026 rdiffweb contributors
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

$(function () {
    $('.rdw-modal-confirm').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var modal = $(this);
        var url = button.data('url');
        modal.find("form").attr('action', url);

        // Extract info from data-* attributes and update matching input fields
        var data = button.data();
        $.each(data, function (key, value) {
            var input = modal.find(".modal-body input[name='" + key + "']");
            if (input.length) {
                input.val(value);
            }
        });
    });
});