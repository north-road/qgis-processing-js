//#Rename roads=name
//#Sample scripts=group
//#new_road_name=string
function func(feature)
{
  // the global 'feedback' object gives access to a QgsProcessingFeedback object, which can be
  // used to report errors and log messages for the user
  feedback.pushInfo(feature.properties.ROAD_NAME)
  // feature is the geojson feature, return a geojson output features (or collection of features)
  // parameter values will be available here!
  feature.properties.ROAD_NAME = new_road_name;
  return feature;
}