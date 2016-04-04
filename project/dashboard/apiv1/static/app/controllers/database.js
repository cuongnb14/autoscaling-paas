'use strict';

angular.module('Database')

.controller('GetDatabasesController',
    ['$scope', '$rootScope', 'RESTfulService',
    function ($scope, $rootScope, RESTfulService) {
      var gds = this;

        gds.init = function () {
            RESTfulService.getDatabases(function(response) {
                if(response.status != "error") {
                    gds.databases = response;
                } else {
                    gds.databases = null;
                }
            });
        }

        gds.updatePassword = function (database) {
          RESTfulService.updatePassword(database.id,gds.new_password[database.id], function(response) {
              toastr[response.status](response.message)
              if(response.status == "success") {
                  gds.init();
              }
          });
        };

        gds.addDatabase = function (database) {

          RESTfulService.addDatabase(gds.root_password, function(response) {
              toastr[response.status](response.message)
              if(response.status == "success") {
                  gds.init();
              }
          });
        };

        gds.deleteDatabase = function (database_id) {

          RESTfulService.deleteDatabase(database_id, function(response) {
              toastr[response.status](response.message)
              if(response.status == "success") {
                  gds.init();
              }
          });
        };

        gds.init();

    }])

.controller('GetDatabaseController',
    ['$scope', '$rootScope', 'RESTfulService',
    function ($scope, $rootScope, RESTfulService) {
      var gd = this;

        gd.init = RESTfulService.getDatabases(function(response) {
            if(response.status != "error") {
                gd.database = response;
            } else {
                gd.database = null;
            }
        });

        gd.init()

    }])

.controller('SetDatabaseController',
    ['$scope', '$rootScope', 'RESTfulService',
    function ($scope, $rootScope, RESTfulService) {
      var sd = this;

      sd.addDatabase = function() {
        RESTfulService.addDatabase(sd.database, function(response) {
              toastr[response.status](response.message);
        });
      }






    }]);
