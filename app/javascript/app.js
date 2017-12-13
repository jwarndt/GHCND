
require([
    "esri/Map",
    "esri/Basemap",
    "esri/views/MapView",
    "esri/widgets/BasemapToggle",
    "esri/layers/FeatureLayer",

    "calcite-maps/calcitemaps-v0.5",
    "calcite-maps/calcitemaps-arcgis-support-v0.5",

    "bootstrap/Collapse",
    "bootstrap/Dropdown",
    "bootstrap/Tab",

    "dojo/dom",
    "dojo/on",
    "dojo/domReady!"
  ], function(Map, Basemap, MapView, BasemapToggle, FeatureLayer, dom, on, CalciteMaps, CalciteMapsArcGIS) {

    // Set up popup template for the layer
      var pTemplate = {
        title: "Station ID: {stationID}",
        content: [{
          type: "fields",
          fieldInfos: [{
            fieldName: "name",
            label: "Station name",
            visible: true
          }, {
            fieldName: "country",
            label: "Country",
            visible: true
          }, {
            fieldName: "state",
            label: "State/Province/Territory",
            visible: true
          }, {
            fieldName: "elev",
            label: "Elevation",
            visible: true
          }]
        }]
      };

     var map = new Map({
      basemap: "topo",
    });

    var ghcndLyr = new FeatureLayer({
      url: "https://services.arcgis.com/8df8p0NlLFEShl0r/ArcGIS/rest/services/midwest_na_met_stations/FeatureServer",
      id: "ghcnd",
      outFields: ["*"],
      popupTemplate: pTemplate
    });

    map.add(ghcndLyr);

    var view = new MapView({
      container: "viewDiv",
      map: map,
      zoom: 5,
      center: [-93, 42.5],
      padding: {
        top: 50,
        right: 0,
        bottom: 0,
        left: 0
      }, // longitude, latitude 
      uiPadding: {
        components:["zoom"],
        padding: {
          top: 15,
          right: 15,
          bottom: 30,
          left: 15
        }
      }
    });

    var bmapToggle = new BasemapToggle({
      view: view,
      nextBasemap: "satellite"
    });

    view.ui.add(bmapToggle, "bottom-right");

    /*view.on("layerview-create", function(event) {
      if (event.layer.id === "ghcnd") {
        console.log("LayerView for meteorological stations created!", event.layerView);
      }
    });

    view.then(function() {
      ghcndLyr.then(function() {
        view.goTo(ghcndLyr.fullExtent);
      });
    });*/
  });