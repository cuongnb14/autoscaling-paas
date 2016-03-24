'use strict';

angular.module('WebApp')

.controller('GetAppController',
    ['$scope', '$rootScope', 'RESTfulService', '$cookieStore',
    function ($scope, $rootScope, RESTfulService, $cookieStore) {

      $rootScope.globals = $cookieStore.get('globals') || {};
      if ($rootScope.globals.user) {
          RESTfulService.getApps(function(response) {
              if(response.status != "error") {
                  $scope.apps = response;
              } else {
                  $scope.apps = null;
              }
          });
      }

    }])

.controller('AddAppController',
    ['$scope', '$rootScope', 'RESTfulService', '$cookieStore',
    function ($scope, $rootScope, RESTfulService, $cookieStore) {
      $rootScope.globals = $cookieStore.get('globals') || {};
      if ($rootScope.globals.user) {
          $scope.addApp = function() {
              $scope.dataLoading = true;
              RESTfulService.addApp($scope.app_name, $scope.github_url, $scope.min_instances, $scope.max_instances, function(response){
                  toastr[response.status](response.message)
                  // if(response.status == "error") {
                  //     toastr.error(response.message);
                  // } else {
                  //     toastr.success(response.message);
                  // }
                  $scope.dataLoading = false;
              });
          };
      }
    }]);
