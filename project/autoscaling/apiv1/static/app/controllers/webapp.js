'use strict';

angular.module('WebApp')

.controller('GetAppController',
    ['$scope', '$rootScope', 'RESTfulService', '$cookieStore',
    function ($scope, $rootScope, RESTfulService, $cookieStore) {

      $rootScope.globals = $cookieStore.get('globals') || {};
      if ($rootScope.globals.user) {
          $scope.init = function() {
              RESTfulService.getApps(function(response) {
                  if(response.status != "error") {
                      $scope.apps = response;
                  } else {
                      $scope.apps = null;
                  }
              });
          };
          $scope.init();

          $scope.deleteApp = function(app) {
              RESTfulService.deleteApp(app.name, function(response){
                  toastr[response.status](response.message)
                  $scope.init();
              });
          };
      }



    }])

.controller('AddAppController',
    ['$scope', '$rootScope', 'RESTfulService', '$cookieStore',
    function ($scope, $rootScope, RESTfulService, $cookieStore) {
      $rootScope.globals = $cookieStore.get('globals') || {};
      if ($rootScope.globals.user) {
          $scope.addApp = function() {
              $scope.dataLoading = true;
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
                  toastr[response.status](response.message)
                  $scope.dataLoading = false;
              });
          };

      }
    }]);
