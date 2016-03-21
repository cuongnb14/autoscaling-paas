'use strict';

angular.module('Database')

.controller('DatabaseController',
    ['$scope', '$rootScope', 'RESTfulService',
    function ($scope, $rootScope, RESTfulService) {
        RESTfulService.getDatabases(function(response) {
            if(response.status != "error") {
                $scope.databases = response;
            } else {
                $scope.databases = null;
            }
        });
    }]);
