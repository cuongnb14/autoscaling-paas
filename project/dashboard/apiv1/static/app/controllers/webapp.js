'use strict';

angular.module('WebApp')

.controller('GetAppsController',
    ['RESTfulService',
    function (RESTfulService) {
        var gas = this;

        gas.init = function() {
            RESTfulService.getApps(function(response) {
                if(response.status != "error") {
                    gas.apps = response;
                } else {
                    gas.apps = null;
                }
            });
        };
        gas.init();

        gas.deleteApp = function(app_name) {
            RESTfulService.deleteApp(app_name, function(response){
                toastr[response.status](response.message)
                gas.init();
            });
        };

        gas.putApp = function(app_name, action) {
            RESTfulService.putApp(app_name, action, function(response){
                toastr[response.status](response.message)
                gas.init();
            });
        };

        gas.scaleApp = function(app_name) {
            RESTfulService.scaleApp(app_name, gas.instances[app_name], function(response){
                toastr[response.status](response.message)
                gas.init();
            });
        };

    }])

    .controller('GetAppController',
        ['$location', 'RESTfulService',
        function ($location, RESTfulService) {
            var ga = this;
            var app_name = $location.search().name;

            ga.getApp = function(app_name) {
              RESTfulService.getApp(app_name, function(response) {
                  if(response.status != "error") {
                      ga.app = response;
                  } else {
                      ga.app = null;
                  }
              });
            };

            ga.getPolicies = function(app_name) {
              RESTfulService.getPolicies(app_name, function(response) {
                  if(response.status != "error") {
                      ga.policies = response;
                  } else {
                      ga.policies = null;
                  }
              });
            };

            ga.updateApp = function() {
                RESTfulService.updateApp(ga.app, function(response) {
                  toastr[response.status](response.message)
                  ga.getApp(app_name);
                });
            };

            ga.disabledPolicy = function(policy_id, disabled) {
                RESTfulService.disabledPolicy(app_name, policy_id, disabled, function(response) {
                  toastr[response.status](response.message)
                  ga.getPolicies(app_name);
                });
            };

            ga.updatePolicy = function(policy) {
                RESTfulService.updatePolicy(app_name, policy, function(response) {
                  toastr[response.status](response.message)
                  ga.getPolicies(app_name);
                });
            };

            ga.addPolicy = function(policy) {
                RESTfulService.addPolicy(app_name, policy, function(response) {
                  toastr[response.status](response.message)
                  ga.getPolicies(app_name);
                });
            };

            ga.deletePolicy = function(policy_id) {
                RESTfulService.deletePolicy(app_name, policy_id, function(response) {
                  toastr[response.status](response.message)
                  ga.getPolicies(app_name);
                });
            };

            ga.getApp(app_name);
            ga.getPolicies(app_name)
        }])

.controller('SetAppController',
    ['$scope', 'RESTfulService',
    function ($scope, RESTfulService) {
          $scope.addApp = function() {
              RESTfulService.addApp($scope.app_name,
                                    $scope.github_url,
                                    $scope.min_instances,
                                    $scope.max_instances,
                                    $scope.env_db_hostname,
                                    $scope.env_db_port,
                                    $scope.env_db_name,
                                    $scope.env_db_username,
                                    $scope.env_db_password,
                                    $scope.cpus,
                                    $scope.mem,
              function(response){
                  toastr[response.status](response.message);
              });
          };
    }])

.controller('MetricController',
    ['$scope', 'RESTfulService',
    function ($scope, RESTfulService) {
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawChart);
      setInterval(drawChart, 10000);
      function drawChart() {
          RESTfulService.getMetrics("app_name", drawFromData);
          function drawFromData(response) {
              /*       cpu_usage       */
              var data = new google.visualization.DataTable();
              data.addColumn('datetime', 'Time');
              data.addColumn('number', 'Cpus');
              function getCpuData(x) {
                  return [new Date(x[0]*1000), x[2]]
              }
              var row = response.data.map(getCpuData)
              data.addRows(row)
              var options = {
                    legend: 'none',
                    height: 200,
                    hAxis: {
                      format: 'MMM dd hh:mm',
                      gridlines: {count: 10, color: '#dfdfdf'}
                    },
                    vAxis: {
                      gridlines: {color: '#dfdfdf'},
                      minValue: 0
                    }
                };
              var chart = new google.visualization.LineChart(document.getElementById('cpu_chart'));
              chart.draw(data, options);
              /*       mem_usage       */
              var data = new google.visualization.DataTable();
              data.addColumn('datetime', 'Time');
              data.addColumn('number', 'Mem');
              function getMemData(x) {
                  return [new Date(x[0]*1000), x[3]]
              }
              var row = response.data.map(getMemData)
              data.addRows(row)
              var chart = new google.visualization.LineChart(document.getElementById('mem_chart'));
              chart.draw(data, options);
              /*       instances       */
              var data = new google.visualization.DataTable();
              data.addColumn('datetime', 'Time');
              data.addColumn('number', 'Instances');
              function getInstancesData(x) {
                  return [new Date(x[0]*1000), x[1]]
              }
              var row = response.data.map(getInstancesData)
              data.addRows(row)
              var chart = new google.visualization.LineChart(document.getElementById('instances_chart'));
              chart.draw(data, options);
          }
      }
    }]);
