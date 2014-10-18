'use strict';
module.exports = function(grunt) {

  grunt.initConfig({
    jshint: {
      options: {
        jshintrc: '.jshintrc'
      },
      all: [
        'Gruntfile.js',
        'rdiffWeb/static/js/*.js',
        '!rdiffWeb/static/js/plugins/*.js',
        '!rdiffWeb/static/js/scripts.min.js'
      ]
    },
    less: {
      dist: {
        options: {
          strictMath: true,
          outputSourceFiles: true
        },
        files: {
          'rdiffWeb/static/css/main.min.css': [
            'rdiffWeb/static/less/main.less'
          ]
        }
      }
    },
    uglify: {
      dist: {
        files: {
          'rdiffWeb/static/js/scripts.min.js': [
            'rdiffWeb/static/js/plugins/*.js',
            'rdiffWeb/static/js/_*.js'
          ]
        }
      }
    },
    watch: {
      less: {
        files: [
          'rdiffWeb/static/less/*.less'
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
        'rdiffWeb/static/css/main.min.css',
        'rdiffWeb/static/js/scripts.min.js'
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
