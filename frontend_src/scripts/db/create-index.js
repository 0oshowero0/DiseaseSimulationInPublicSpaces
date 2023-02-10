/* disable-eslint */

db.getCollection("CarPosition").createIndex({
  car: NumberInt("1")
}, {
  name: "CarPosition_car_index"
});

db.getCollection("CarPosition").createIndex({
  collection: NumberInt("1"),
  car: NumberInt("1"),
  timestamp: NumberInt("1")
}, {
  name: "CarPosition_car_time_index"
});

db.getCollection("CarPosition").createIndex({
  collection: NumberInt("1"),
  timestamp: NumberInt("1")
}, {
  name: "CarPosition_col_ts_index"
});

db.getCollection("CarPosition").createIndex({
  collection: NumberInt("1"),
  timestamp: NumberInt("1"),
  location: "2dsphere"
}, {
  name: "CarPosition_col_ts_loc_index",
  "2dsphereIndexVersion": NumberInt("3")
});

db.getCollection("CarPosition").createIndex({
  location: "2dsphere"
}, {
  name: "CarPosition_loc_index",
  "2dsphereIndexVersion": NumberInt("3")
});

db.getCollection("RoadChart").createIndex({
  collection: NumberInt("1"),
  start: NumberInt("1"),
  end: NumberInt("1"),
  type: NumberInt("1")
}, {
  name: "RoadChart_col_time_index"
});

db.getCollection("RoadSpeed").createIndex({
  collection: NumberInt("1"),
  start: NumberInt("1"),
  end: NumberInt("1")
}, {
  name: "RoadSpeed_col_time_index"
});
