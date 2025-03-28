var adminBoundaries = ee.FeatureCollection("FAO/GAUL/2015/level1");
Map.addLayer(adminBoundaries, {}, 'Boundaries', false);

// Function to handle user click and extract methane data
var handleClick = function(coords) {
  var pointGeometry = ee.Geometry.Point(coords.lon, coords.lat);
  Map.centerObject(pointGeometry, 10);
  Map.addLayer(pointGeometry, {color: 'red'}, 'Selected Location');

  var analysisStartYear = '2020';
  var analysisEndYear = '2024';

  var sentinel5P = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CH4")
    .select(['CH4_column_volume_mixing_ratio_dry_air'], ['methane'])
    .filterDate(analysisStartYear, analysisEndYear)
    .filterBounds(pointGeometry);

  var monthRange = ee.List.sequence(1, 12);

  var monthlyMethaneData = ee.ImageCollection(
    ee.List.sequence(
      ee.Number.parse(analysisStartYear), 
      ee.Number.parse(analysisEndYear).subtract(1)
    ).map(function(year) {
      return monthRange.map(function(month) {
        var monthlyImage = sentinel5P
          .filter(ee.Filter.calendarRange(year, year, 'year'))
          .filter(ee.Filter.calendarRange(month, month, 'month'))
          .mean();

        var date = ee.Date.fromYMD(year, month, 1);
        return monthlyImage
          .set('system:time_start', date.millis())
          .set('system:index', date.format('YYYY-MM-dd'));
      });
    }).flatten()
  );

  var monthlyMethaneAtPoint = monthlyMethaneData.map(function(image) {
    var methaneValue = image.reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: pointGeometry,
      scale: 3000,
      maxPixels: 1e8
    }).get('methane');

    return image.set({
      'methane_value': methaneValue,
      'longitude': coords.lon,
      'latitude': coords.lat
    });
  });

  var methaneFeatureCollection = monthlyMethaneAtPoint.map(function(image) {
    return ee.Feature(null, {
      'date': image.get('system:index'),
      'methane_value': image.get('methane_value'),
      'longitude': image.get('longitude'),
      'latitude': image.get('latitude')
    });
  });

  Export.table.toDrive({
    collection: methaneFeatureCollection,
    description: 'Methane_Emissions_CSV',
    fileFormat: 'CSV',
    folder: 'Methane_Monitoring',
    fileNamePrefix: 'Methane_Emissions'
  });

  Export.table.toDrive({
    collection: methaneFeatureCollection,
    description: 'Methane_Emissions_JSON',
    fileFormat: 'GeoJSON',
    folder: 'Methane_Monitoring',
    fileNamePrefix: 'Methane_Emissions'
  });

};

// Capture click event on the map
Map.onClick(handleClick);

Map.setCenter(0, 0, 2);
