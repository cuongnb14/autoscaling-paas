'use strict';

angular.module('RESTful')

.factory('RESTfulService',
    ['$http',
    function ($http) {
        var service = {};

        service.getApps = function (callback) {
            $http.get('http://localhost:8000/api/v1/apps')
               .success(function (response) {
                  callback(response);
               });
        };

        service.getDatabases = function (callback) {
            $http.get('http://localhost:8000/api/v1/databases')
               .success(function (response) {
                  callback(response);
               });
        };
        return service;
    }]);
