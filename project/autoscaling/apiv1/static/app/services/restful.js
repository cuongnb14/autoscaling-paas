'use strict';

angular.module('RESTful')

.factory('RESTfulService',
    ['$http', 'appConfig',
    function ($http, appConfig) {
        var service = {};

        service.getApps = function (callback) {
            $http.get('http://'+appConfig.host+':'+appConfig.port+'/api/v1/apps')
               .success(function (response) {
                  callback(response);
               });
        };

        service.getApp = function (app_name, callback) {
            $http.get('http://'+appConfig.host+':'+appConfig.port+'/api/v1/apps/'+app_name)
               .success(function (response) {
                  callback(response);
               });
        };

        service.getDatabases = function (callback) {
            $http.get('http://'+appConfig.host+':'+appConfig.port+'/api/v1/databases')
               .success(function (response) {
                  callback(response);
               });
        };

        service.addDatabase = function (root_password, callback) {
            $http.post('http://'+appConfig.host+':'+appConfig.port+'/api/v1/databases', {
                                                                  root_password: root_password
                                                                })
               .success(function (response) {
                  callback(response);
               });
        };

        service.deleteDatabase = function (database_id, callback) {
            $http.delete('http://'+appConfig.host+':'+appConfig.port+'/api/v1/databases/'+database_id)
               .success(function (response) {
                  callback(response);
               });
        };

        service.addApp = function (app_name, github_url, min_instances, max_instances, env_db_hostname='', env_db_port=0,env_db_name='', env_db_username='', env_db_password='',  callback) {
            $http.post('http://'+appConfig.host+':'+appConfig.port+'/api/v1/apps', { name : app_name,
                                                              github_url : github_url,
                                                              min_instances : min_instances,
                                                              max_instances : max_instances,
                                                              env_db_hostname : env_db_hostname,
                                                              env_db_port : env_db_port,
                                                              env_db_name : env_db_name,
                                                              env_db_username : env_db_username,
                                                              env_db_password : env_db_password
                                                              })
               .success(function (response) {
                  callback(response);
               });
        };

        service.updateApp = function (app,  callback) {
            $http.put('http://'+appConfig.host+':'+appConfig.port+'/api/v1/apps/'+app.name, {
                                                              action : "info",
                                                              min_instances : app.min_instances,
                                                              max_instances : app.max_instances,
                                                              env_db_hostname : app.env_db_hostname,
                                                              env_db_port : app.env_db_port,
                                                              env_db_name : app.env_db_name,
                                                              env_db_username : app.env_db_username,
                                                              env_db_password : app.env_db_password
                                                              })
               .success(function (response) {
                  callback(response);
               });
        };

        service.putApp = function (app_name, action,  callback) {
            $http.put('http://'+appConfig.host+':'+appConfig.port+'/api/v1/apps/'+app_name, {
                                                              action : action
                                                              })
               .success(function (response) {
                  callback(response);
               });
        };

        service.scaleApp = function (app_name, instances, callback) {
            $http.put('http://'+appConfig.host+':'+appConfig.port+'/api/v1/apps/'+app_name, {
                                                              action : "scale",
                                                              value : instances
                                                              })
               .success(function (response) {
                  callback(response);
               });
        };

        service.deleteApp = function (app_name, callback) {
            $http.delete('http://'+appConfig.host+':'+appConfig.port+'/api/v1/apps/'+app_name)
               .success(function (response) {
                  callback(response);
               });
        };

        service.updatePassword = function (database_id, new_password, callback) {
            $http.put('http://'+appConfig.host+':'+appConfig.port+'/api/v1/databases/'+database_id, {
                                                                                new_password: new_password
                                                                              })
               .success(function (response) {
                  callback(response);
               });
        };

        return service;
    }]);
