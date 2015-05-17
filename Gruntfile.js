// rdiffweb, A web interface to rdiff-backup repositories
// Copyright (C) 2014 rdiffweb contributors
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


module.exports = function(grunt) {

  grunt.initConfig({
    jshint: {
      all: [
        'Gruntfile.js',
        'rdiffweb/static/js/*.js',
        '!rdiffweb/static/js/plugins/*.js',
        '!rdiffweb/static/js/scripts.min.js'
      ]
    },
    less: {
      dist: {
        options: {
          strictMath: true,
          outputSourceFiles: true
        },
        files: {
          'rdiffweb/static/css/main.min.css': [
            'rdiffweb/static/less/main.less'
          ]
        }
      }
    },
    uglify: {
      dist: {
        files: {
          'rdiffweb/static/js/scripts.min.js': [
            'rdiffweb/static/js/plugins/*.js',
            'rdiffweb/static/js/_*.js'
          ]
        }
      }
    },
    watch: {
      less: {
        files: [
          'rdiffweb/static/less/*.less'
        ],
        tasks: ['less']
      },
      js: {
        files: [
          '<%= jshint.all %>'
        ],
        tasks: ['jshint','uglify']
      }
    },
    clean: {
      dist: [
        'rdiffweb/static/css/main.min.css',
        'rdiffweb/static/js/scripts.min.js'
      ]
    }
  });

  // Load tasks
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-less');

  // Register tasks
  grunt.registerTask('default', [
    'clean',
    'less',
    'uglify'
  ]);
  grunt.registerTask('dev', [
    'watch'
  ]);

};
