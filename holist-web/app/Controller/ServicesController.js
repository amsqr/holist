angular.
module('App')
    .controller('ServicesController', function($scope) {
        $scope.ServicesSlides = [
            {
                "image":'assets/img/about/slider/newyork.png',
                "title":"Don't Listen to Your Gut Feeling!",
                "caption":""
            },
            {
                "image":'assets/img/about/slider/servers.png',
                "title":"Reliable and High-Efficient Server Infrastructure",
                "caption":"Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            },
            {
                "image":'assets/img/about/slider/world.png',
                "title":"Linguistic Models Runnin On World New",
                "caption":"Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            }
        ]
    });
