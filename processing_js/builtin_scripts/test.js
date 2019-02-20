//#Rename roads=name
//#Sample scripts=group
//#new_road_name=string
function func(feature)
{
  // feature is the geojson feature, return a geojson output features (or collection of features)
  // parameter values will be available here!
  feature.properties.ROAD_NAME = new_road_name;
  return feature;
}