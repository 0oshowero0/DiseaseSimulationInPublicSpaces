const {date2tsObj} = require("../timestamp");
const {getStartEndRange} = require("../../db/utils/analysis");

const genIncrementSerializer = (resultsSerializer) => (data) => {
  const results = resultsSerializer(data);
  const [validRangeStart, validRangeEnd] = getStartEndRange(data);
  return {
    results,
    validRangeStart: date2tsObj(new Date(validRangeStart)),
    validRangeEnd: date2tsObj(new Date(validRangeEnd))
  }
}

exports.genIncrementSerializer = genIncrementSerializer
