db.RoadSpeed.updateMany({}, [
  { $set: { start: "$timestamp" } },
  {
    $project: {
      _id: 1,
      key: 1,
      speed: 1,
      length: 1,
      collection: 1,
      start: 1,
      lengthByMS: { $multiply:["$length", 1000] },
    }
  },
  {
    $project: {
      _id: 1,
      key: 1,
      speed: 1,
      length: 1,
      collection: 1,
      start: 1,
      end: { $add:["$start", "$lengthByMS"] },
    }
  },
])
