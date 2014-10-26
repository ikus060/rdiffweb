'use strict';
module.exports = function(grunt) {

  grunt.initConfig({
    jshint: {
      options: {
        jshintrc: '.jshintrc'
      },
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
