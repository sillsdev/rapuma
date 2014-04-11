'use strict';

angular.module('rapuma.settings', ['ui.bootstrap'])
.controller('mainCtrl', ['$scope', function($scope) {
    $scope.currentProject = {isbn: '978-', settings: {}};

    $scope.projects = [];

    $scope.settingsConfig = {
        sections: [ {
            sectionID: 'ProjectInfo',
            name: 'Project Information',
            description: 'some desc',
            settings: {
                name: 'Project Media ID Code',
                key: 'projectName',
                description: 'desc',
                type: 'string',
                value: 'book'
            }
        },
    
        ]};




    $scope.addProject = function() {
        $scope.projects.push($scope.currentProject);
        $scope.currentProject = {isbn: '978-'};
    };

    $scope.editProject = function(id) {
        console.log(id); 
        angular.forEach($scope.projects, function(p) {
            if (p.id == id) {
                $scope.currentProject = p;
            }
       });
    };

}]);
