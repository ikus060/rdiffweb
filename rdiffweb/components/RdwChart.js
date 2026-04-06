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

/*
 * Define a custom datetime scale.
 */
const BackupDateScale = class extends Chart.CategoryScale {

  static _getLabelForValue(value) {
    const labels = this.getLabels();

    if (value >= 0 && value < labels.length) {
      const epoch = labels[value]; 
      if( typeof epoch  === "number") {
        return new Date(epoch * 1000).toLocaleString();
      }
      return epoch;
    }

    return value;
  }

  // Format date time
  getLabelForValue(value) {
    return BackupDateScale._getLabelForValue.call(this, value);
  }

}

BackupDateScale.id = 'backupdate';
BackupDateScale.defaults = {
  ticks: {
    maxTicksLimit: 10,
    callback: function(value) {
      return BackupDateScale._getLabelForValue.call(this, value);
    }
  },
};

Chart.register(BackupDateScale);

/*
 * Define onClick callback
 */
onClickCallback = function(url) {
    return function(event, elements) {
        // No bar clicked
        if (elements.length === 0) return;

        const index   = elements[0].index;
        const label   = this.data.labels[index]; // Backup date
        const value   = this.data.datasets[0].data[index];

        let target = url.replace('[[label]]', label);

        window.open(target, '_blank')
    }
}
onHoverCallback = function(event, elements){
    event.native.target.style.cursor = elements.length ? 'pointer' : 'default';
}