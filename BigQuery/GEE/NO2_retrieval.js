var adminBoundaries = ee.FeatureCollection("FAO/GAUL/2015/level1");
Map.addLayer(adminBoundaries, {}, 'Boundaries', false);

// Function to handle user click and extract data for NO2 (and CO if available)
var handleClick = function(coords) {
  var pointGeometry = ee.Geometry.Point(coords.lon, coords.lat);
  Map.centerObject(pointGeometry, 10);
  Map.addLayer(pointGeometry, {color: 'red'}, 'Selected Location');

  var analysisStartYear = '2020';
  var analysisEndYear = '2024';

  // Sentinel-5P image collection for NO2 (CO is not directly available from S5P)
  var sentinel5P = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
    .select(['NO2_column_number_density'], ['NO2'])
    .filterDate(analysisStartYear, analysisEndYear)
    .filterBounds(pointGeometry);

  var monthRange = ee.List.sequence(1, 12);

  var monthlyNO2Data = ee.ImageCollection(
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

  var monthlyNO2AtPoint = monthlyNO2Data.map(function(image) {
    var NO2Value = image.reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: pointGeometry,
      scale: 3000,
      maxPixels: 1e8
    }).get('NO2');

    return image.set({
      'NO2_value': NO2Value,
      'longitude': coords.lon,
      'latitude': coords.lat
    });
  });

  var NO2FeatureCollection = monthlyNO2AtPoint.map(function(image) {
    return ee.Feature(null, {
      'date': image.get('system:index'),
      'NO2_value': image.get('NO2_value'),
      'longitude': image.get('longitude'),
      'latitude': image.get('latitude')
    });
  });

  // Exporting the results as CSV and GeoJSON
  Export.table.toDrive({
    collection: NO2FeatureCollection,
    description: 'NO2_Emissions_CSV',
    fileFormat: 'CSV',
    folder: 'Gas_Monitoring',
    fileNamePrefix: 'NO2_Emissions'
  });

  Export.table.toDrive({
    collection: NO2FeatureCollection,
    description: 'NO2_Emissions_JSON',
    fileFormat: 'GeoJSON',
    folder: 'Gas_Monitoring',
    fileNamePrefix: 'NO2_Emissions'
  });

};

// Capture click event on the map
Map.onClick(handleClick);

Map.setCenter(0, 0, 2);
