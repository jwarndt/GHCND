require([
    "esri/Map",
    "esri/Basemap",
    "esri/views/MapView",
    "esri/widgets/Search",
    "esri/core/watchUtils",
    "dojo/query",

    "calcite-maps/calcitemaps-v0.5",
    "calcite-maps/calcitemaps-arcgis-support-v0.5",

    "bootstrap/Collapse",
    "bootstrap/Dropdown",
    "bootstrap/Tab",

    "dojo/domReady!"
  ], function(Map, Basemap, MapView, Search, watchUtils, query, CalciteMaps, CalciteMapsArcGIS) {

    var map = new Map({
      basemap: "topo"
    });


    var view = new MapView({
      container: "viewDiv",
      map: map,
      zoom: 5,
      center: [-93, 42.5] // longitude, latitude
    });

    var searchWidgetNav = new Search({
      container: "searchNavDiv",
      view: view
    });

    // Wire-up expand events
    CalciteMapsArcGIS.setSearchExpandEvents(searchWidgetNav);

    // Search Widget
      function syncSearch(view) {
        searchWidgetNav.view = view;
        if (searchWidgetNav.selectedResult) {
          watchUtils.whenTrueOnce(view,"ready",function(){
            searchWidgetNav.autoSelect = false;
            searchWidgetNav.search(searchWidgetNav.selectedResult.name);
            searchWidgetNav.autoSelect = true;            
          });
        }
      }
  });


