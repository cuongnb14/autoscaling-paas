'use strict';

angular.module('Authentication')

.controller('LoginController',
    ['$scope', '$rootScope', '$location', 'AuthenticationService', 'appConfig',
    function ($scope, $rootScope, $location, AuthenticationService, appConfig) {
        // reset login status
        AuthenticationService.ClearCredentials();

        $scope.login = function () {
            $scope.dataLoading = true;
            AuthenticationService.Login($scope.username, $scope.password, function(response) {
                if(response.status == "success") {
                    AuthenticationService.SetCredentials(response.user, $scope.password);
                    window.location.href = 'http://'+appConfig.host+':'+appConfig.port+'/ui/dashboard';
                } else {
                    $scope.error = response.message;
                    $scope.dataLoading = false;
                }
            });
        };
    }]);
