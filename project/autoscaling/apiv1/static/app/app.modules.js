'use strict';

// declare modules
angular.module('Authentication', []);
angular.module('RESTful', []);
angular.module('Login', ['Authentication']);

angular.module('Registration', ['Authentication']);

angular.module('WebApp', ['RESTful']);

angular.module('Database', ['RESTful']);

angular.module('BasicHttpAuth', [
    'Authentication',
    'ngRoute',
    'ngCookies',
    'WebApp',
    'Database',
])

.run(['$rootScope', '$location', '$cookieStore', '$http',
    function ($rootScope, $location, $cookieStore, $http) {
        // keep user logged in after page refresh
        $rootScope.globals = $cookieStore.get('globals') || {};
        if ($rootScope.globals.user) {
            $http.defaults.headers.common['Authorization'] = 'Basic ' + $rootScope.globals.user.authdata; // jshint ignore:line
        }

        $rootScope.$on('$locationChangeStart', function (event, next, current) {
            // redirect to login page if not logged in
            if (!$rootScope.globals.user && (window.location.href !== 'http://localhost:8000/ui/login' && window.location.href !== 'http://localhost:8000/ui/registration')) {
                window.location.href = 'http://localhost:8000/ui/login';
            }
        });


    }]);
