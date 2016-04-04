'use strict';

// declare modules
angular.module("Config", []).constant("appConfig", {
        "host": "localhost",
        "port": "8000"
    })
angular.module('Authentication', ['Config']);
angular.module('RESTful', ['Config']);
angular.module('Login', ['Authentication','Config']);

angular.module('Registration', ['Authentication','Config']);

angular.module('WebApp', ['RESTful','Config']);

angular.module('Database', ['RESTful','Config']);
angular.module('ABModal', ['Config']);
angular.module('BasicHttpAuth', [
    'Authentication',
    'ngRoute',
    'ngCookies',
    'WebApp',
    'Database',
    'angular-loading-bar',
    'ABModal',
    'Config',
])

.run(['$rootScope', '$location', '$cookieStore', '$http', 'appConfig',
    function ($rootScope, $location, $cookieStore, $http, appConfig) {
        // keep user logged in after page refresh
        $rootScope.globals = $cookieStore.get('globals') || {};
        if ($rootScope.globals.user) {
            $http.defaults.headers.common['Authorization'] = 'Basic ' + $rootScope.globals.user.authdata; // jshint ignore:line
        }

        $rootScope.$on('$locationChangeStart', function (event, next, current) {
            // redirect to login page if not logged in
            if (!$rootScope.globals.user && (window.location.href !== 'http://'+appConfig.host+':'+appConfig.port+'/ui/login' && window.location.href !== 'http://'+appConfig.host+':'+appConfig.port+'/ui/registration')) {
                window.location.href = 'http://'+appConfig.host+':'+appConfig.port+'/ui/login';
            }
        });
    }]);
