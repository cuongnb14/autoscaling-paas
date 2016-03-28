'use strict';

angular.module('WebApp')

.controller('GetAppsController',
    ['RESTfulService',
    function (RESTfulService) {
        var gas = this;

        gas.init = function() {
            RESTfulService.getApps(function(response) {
                if(response.status != "error") {
                    gas.apps = response;
                } else {
                    gas.apps = null;
                }
            });
        };
        gas.init();

        gas.deleteApp = function(app_name) {
            RESTfulService.deleteApp(app_name, function(response){
                toastr[response.status](response.message)
                gas.init();
            });
        };

        gas.putApp = function(app_name, action) {
            RESTfulService.putApp(app_name, action, function(response){
                toastr[response.status](response.message)
                gas.init();
            });
        };

        gas.scaleApp = function(app_name) {
            RESTfulService.scaleApp(app_name, gas.instances[app_name], function(response){
                toastr[response.status](response.message)
                gas.init();
            });
        };

    }])

    .controller('GetAppController',
        ['$location', 'RESTfulService',
        function ($location, RESTfulService) {
            var ga = this;
            var app_name = $location.search().name;
            ga.init = function(app_name) {
                RESTfulService.getApp(app_name, function(response) {
                    if(response.status != "error") {
                        ga.app = response;
                    } else {
                        ga.app = null;
                    }
                });
            };

            ga.updateApp = function() {
                RESTfulService.updateApp(ga.app, function(response) {
                  toastr[response.status](response.message)
                  ga.init(app_name);
                });
            };

            ga.init(app_name);
        }])

.controller('SetAppController',
    ['RESTfulService',
    function (RESTfulService) {
          $scope.addApp = function() {
              RESTfulService.addApp($scope.app_name,
                                    $scope.github_url,
                                    $scope.min_instances,
                                    $scope.max_instances,
                                    $scope.env_db_hostname,
                                    $scope.env_db_port,
                                    $scope.env_db_name,
                                    $scope.env_db_username,
                                    $scope.env_db_password,
              function(response){
                  toastr[response.status](response.message);
              });
          };
    }]);
