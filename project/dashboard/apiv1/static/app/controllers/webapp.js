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

            ga.getApp = function(app_name) {
              RESTfulService.getApp(app_name, function(response) {
                  if(response.status != "error") {
                      ga.app = response;
                  } else {
                      ga.app = null;
                  }
              });
            };

            ga.getPolicies = function(app_name) {
              RESTfulService.getPolicies(app_name, function(response) {
                  if(response.status != "error") {
                      ga.policies = response;
                  } else {
                      ga.policies = null;
                  }
              });
            };

            ga.updateApp = function() {
                RESTfulService.updateApp(ga.app, function(response) {
                  toastr[response.status](response.message)
                  ga.getApp(app_name);
                });
            };

            ga.disabledPolicy = function(policy_id, disabled) {
                RESTfulService.disabledPolicy(app_name, policy_id, disabled, function(response) {
                  toastr[response.status](response.message)
                  ga.getPolicies(app_name);
                });
            };

            ga.updatePolicy = function(policy) {
                RESTfulService.updatePolicy(app_name, policy, function(response) {
                  toastr[response.status](response.message)
                  ga.getPolicies(app_name);
                });
            };

            ga.addPolicy = function(policy) {
                RESTfulService.addPolicy(app_name, policy, function(response) {
                  toastr[response.status](response.message)
                  ga.getPolicies(app_name);
                });
            };

            ga.deletePolicy = function(policy_id) {
                RESTfulService.deletePolicy(app_name, policy_id, function(response) {
                  toastr[response.status](response.message)
                  ga.getPolicies(app_name);
                });
            };

            ga.getApp(app_name);
            ga.getPolicies(app_name)
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
