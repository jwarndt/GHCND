require([
    "esri/Map",
    "esri/views/MapView",

    "calcite-maps/calcitemaps-v0.5",
    "calcite-maps/calcitemaps-arcgis-support-v0.5",

    "dojo/domReady!"
  ], function(Map, MapView, Search, CalciteMaps, CalciteMapsArcGIS) {

    var map = new Map({
      basemap: "topo"
    });

    var view = new MapView({
      container: "viewDiv",
      map: map,
      zoom: 5,
      center: [-93, 42.5] // longitude, latitude
    });
  });