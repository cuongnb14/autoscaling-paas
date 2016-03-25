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
