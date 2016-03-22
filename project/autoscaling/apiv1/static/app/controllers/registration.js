'use strict';

angular.module('Authentication')

.controller('RegistrationController',
    ['$scope', '$rootScope', '$location', 'AuthenticationService',
    function ($scope, $rootScope, $location, AuthenticationService) {

        $scope.register = function () {
            $scope.dataLoading = true;
            AuthenticationService.Register($scope.username, $scope.password, $scope.email, $scope.first_name, $scope.last_name, function(response) {
                if(response.status == "success") {
                    window.location.href = 'http://localhost:8000/ui/login';
                } else {
                    $scope.error = response.message;
                    $scope.dataLoading = false;
                }
            });
        };
    }]);
