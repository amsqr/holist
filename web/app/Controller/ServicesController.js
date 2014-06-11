angular.
module('App')
    .controller('ServicesController', function($scope) {
        $scope.ServicesSlides = [
            {
                "image":'assets/img/about/slider/newyork.png',
                "title":"Don't Listen On Your Gut Feeling!",
                "caption":"holist is a Big Data, Computer Linguistic and Visual Analytics company<br/>providing insights from global science, patents, press, web, and social media for your strategy."
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
