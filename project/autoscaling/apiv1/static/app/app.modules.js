'use strict';

// declare modules
angular.module('Authentication', []);
// angular.module('Home', []);
angular.module('Login', ['Authentication']);

angular.module('Registration', ['Authentication']);

angular.module('BasicHttpAuthExample', [
    'Authentication',
    'ngRoute',
    'ngCookies'
])

.run(['$rootScope', '$location', '$cookieStore', '$http',
    function ($rootScope, $location, $cookieStore, $http) {
        // keep user logged in after page refresh
        $rootScope.globals = $cookieStore.get('globals') || {};
        if ($rootScope.globals.currentUser) {
            $http.defaults.headers.common['Authorization'] = 'Basic ' + $rootScope.globals.currentUser.authdata; // jshint ignore:line
        }

        // $rootScope.$on('$locationChangeStart', function (event, next, current) {
        //     // redirect to login page if not logged in
        //     if ($location.path() !== '/login' && !$rootScope.globals.currentUser) {
        //         $location.path('/login');
        //     }
        // });

        $rootScope.$on('$locationChangeStart', function (event, next, current) {
            // redirect to login page if not logged in
            if (window.location.href !== 'http://localhost:8000/login' && !$rootScope.globals.currentUser) {
                window.location.href = 'http://localhost:8000/login';
            }
        });


    }]);
