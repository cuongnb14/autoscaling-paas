'use strict';

angular.module('WebApp')

.controller('WebAppController',
    ['$scope', '$rootScope', 'RESTfulService',
    function ($scope, $rootScope, RESTfulService) {
        RESTfulService.getApps(function(response) {
            if(response.status != "error") {
                $scope.apps = response;
            } else {
                $scope.apps = null;
            }
        });
    }]);
