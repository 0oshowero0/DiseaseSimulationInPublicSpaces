const {genIncrementSerializer} = require("./utils/increment");
const {date2tsObj} = require("./timestamp");

const trans2RoadSpeedResponse = (data) =>
  data.map(road => {
    const { start, end, ...rest } = road;
    return {
      start: date2tsObj(new Date(start)),
      end: date2tsObj(new Date(end)),
      ...rest,
    }
  })

exports.trans2RoadSpeedResponse = trans2RoadSpeedResponse
exports.trans2RoadSpeedIncrementResponse = genIncrementSerializer(trans2RoadSpeedResponse)
