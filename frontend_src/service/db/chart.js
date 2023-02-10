const _ = require("lodash")
const {getTotalDataWithLimit} = require("./utils/total-skip-limit");
const { getCollection } = require("./db");

async function getRoadChartCollection() {
    return await getCollection("RoadChart")
}

/**
 * 从数据库查询
 * @param collection 数据集
 * @param start {string} 开始时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param end {string} 结束时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param type {string} 图表类型
 * @param skip 从哪里开始
 * @param limit 单次长度限制
 * @returns {Promise<[]>}
 */
async function queryRoadChart(
    collection, start, end, type, skip = 0, limit = 1000
) {
    const roadChart = await getRoadChartCollection()
    return roadChart.find({
        collection,
        type,
        start: {$lt: new Date(end)},
        end: {$gte: new Date(start)},
    }).skip(skip).limit(limit).toArray()
}

/**
 * 从数据库查询增量（变动量）
 * @param collection 数据集
 * @param last {string} 上一次查询时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param now {string} 当前查询时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param type 图表类型
 * @param skip 从哪里开始
 * @param limit 单次长度限制
 * @returns {Promise<[]>}
 */
async function queryRoadChartIncrement(
  collection="test", last, now, type, skip = 0, limit = 1000
) {
    /**
     * (start < now && now < end)&&(!(start<last&&last<end))
     * (start < now && now < end)&&(start>last || last>end))
     * (start <= now && now < end && start>=last) || (start <= now && now < end && last>end)
     * 【(last <= start <= now && now < end) || (now < end < last && start <= now)】
     * 理解：(last <= start <= now < end) || (start <= now < end < last)
     */
    const roadChart = await getRoadChartCollection()
    const commonQuery = { collection, type }
    const queries = [
        roadChart.find({
            ...commonQuery,
            start: {
                $lte: new Date(now),
                $gte: new Date(last),
            },
            end: {$gt: new Date(now)},
        }),
        roadChart.find({
            ...commonQuery,
            end: {
                $lt: new Date(last),
                $gt: new Date(now),
            },
            start: {$gte: new Date(now)},
        }),
    ]

    return await getTotalDataWithLimit({queries, limit, skip})
}


exports.getRoadChartCollection = getRoadChartCollection;
exports.queryRoadChart = queryRoadChart;
exports.queryRoadChartIncrement = queryRoadChartIncrement;

if (require.main === module) {
    (async () => {
        const result = await queryRoadChart(
            "test",
            "2021-01-24T21:10:00.000Z",
            "2021-01-24T21:20:00.000Z",
            "TrafficIndexGraph",
        )
        console.dir(result);
    })()
}
