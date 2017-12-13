
require([
    "esri/Map",
    "esri/Basemap",
    "esri/views/MapView",
    "esri/widgets/BasemapToggle",
    "esri/layers/FeatureLayer",
    "esri/tasks/QueryTask",
    "esri/tasks/support/Query",

    "dojo/dom",
    "dojo/on",

    "bootstrap/Collapse",
    "bootstrap/Dropdown",
    "bootstrap/Tab",

    "calcite-maps/calcitemaps-v0.5",
    "calcite-maps/calcitemaps-arcgis-support-v0.5",

    "dojo/domReady!"
  ], function(Map, Basemap, MapView, BasemapToggle, FeatureLayer, QueryTask, Query, CalciteMaps, CalciteMapsArcGIS, dom, on) {

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

    var ghcndUrl = "https://services.arcgis.com/8df8p0NlLFEShl0r/ArcGIS/rest/services/midwest_na_met_stations/FeatureServer"

    var allStationLyr = new FeatureLayer({
      url: ghcndUrl,
      id: "ghcnd",
      outFields: ["*"],
      popupTemplate: pTemplate
    });

    map.add(allStationLyr);

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

    var maxTempToggle = dom.ById("maxTemp");
    var minTempToggle = dom.ById("minTemp");
    var prcpToggle = dom.ById("prcp");

    var nebraskaToggle = dom.ById("nebraskaStations");
    var northdakotaToggle = dom.ById("northdakotaStations");
    var southdakotaToggle = dom.ById("southdakotaStations");
    var illinoisToggle = dom.ById("illinoisStations");
    var iowaToggle = dom.ById("iowaStations");
    var michiganToggle = dom.ById("michiganStations");
    var ontarioToggle = dom.ById("ontarioStations");
    var manitobaToggle = dom.ById("manitobaStations");
    var saskatchewanToggle = dom.ById("saskatchewanStations");
    var minnesotaToggle = dom.ById("minnesotaStations");
    var wisconsinToggle = dom.ById("wisonsinStations");

    // query task for variables.
    var qTask = new QueryTask({
      url: ghcndUrl
    });

    var params = new Query({
      returnGeometry: true,
      outFields: ["*"]
    });

    // listen for changes. When changes occur,
    // doVarQuery() (build the query and execute)
    view.then(function() {
      on(maxTempToggle, "change", doVarQuery);
      on(minTempToggle, "change", doVarQuery);
      on(prcpToggle, "change", doVarQuery);
    })

    // build the query and execute.
    function doVarQuery() {
      // remove features from previous query
      allStationLyr.removeAll();

      paramString = "";
      if (maxTempToggle.checked) {
        paramString += maxTempToggle.value + "=" + "1";
      }
      if (minTempToggle.checked) {
        if (paramString.length() != 0) {
          paramString += " and ";
        }
        paramString += minTempToggle.value + "=" + "1";
      }
      if (prcpToggle.checked) {
        if (paramString.length() != 0) {
          paramString += " and ";
        }
        paramString += prcpToggle.value + "=" + "1";
      }
      params.where = paramString;
      
      qTask.execute(params)
        .then(getResults)
        .otherwise(promiseRejected);
    }

    function getResults(response) {
      allStationLyr.addMany(response.features);
    }

    function promiseRejected(err) {
      console.error("Promise rejected: ", err.message);
    }
    
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