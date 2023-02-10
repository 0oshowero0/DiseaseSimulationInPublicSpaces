const {genIncrementSerializer} = require("./utils/increment");
const {date2tsObj} = require("./timestamp");

const trans2RoadChartResponse = (data) =>
  data.map(road => {
    const { start, end, data, ...rest } = road;
    return {
      start: date2tsObj(new Date(start)),
      end: date2tsObj(new Date(end)),
      data: JSON.stringify(data),
      ...rest,
    }
  })

exports.trans2RoadChartResponse = trans2RoadChartResponse
exports.trans2RoadChartIncrementResponse = genIncrementSerializer(trans2RoadChartResponse)
