const {getTotalDataWithLimit} = require("./utils/total-skip-limit");
const { getCollection } = require("./db");

async function getRoadSpeedCollection() {
    return await getCollection("RoadSpeed")
}

/**
 * 从数据库查询
 * @param collection 数据集
 * @param start {string} 开始时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param end {string} 结束时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param skip 从哪里开始
 * @param limit 单次长度限制
 * @returns {Promise<[]>}
 */
async function queryRoadSpeed(
  collection="test", start, end, skip = 0, limit = 1000
) {
    const roadSpeed = await getRoadSpeedCollection()
    return roadSpeed.find({
        collection,
        start: {$lt: new Date(end)},
        end: {$gte: new Date(start)},
    }).skip(skip).limit(limit).toArray()
}

/**
 * 从数据库查询增量（变动量）
 * @param collection 数据集
 * @param last {string} 上一次查询时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param now {string} 当前查询时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param skip 从哪里开始
 * @param limit 单次长度限制
 * @returns {Promise<[]>}
 */
async function queryRoadSpeedIncrement(
  collection="test", last, now, skip = 0, limit = 1000
) {
    /**
     * (start < now && now < end)&&(!(start<last&&last<end))
     * (start < now && now < end)&&(start>last || last>end))
     * (start <= now && now < end && start>=last) || (start <= now && now < end && last>end)
     * 【(last <= start <= now && now < end) || (now < end < last && start <= now)】
     * 理解：(last <= start <= now < end) || (start <= now < end < last)
     */
    const roadSpeed = await getRoadSpeedCollection()
    const commonQuery = { collection }
    const queries = [
        roadSpeed.find({
            ...commonQuery,
            start: {
                $lte: new Date(now),
                $gte: new Date(last),
            },
            end: {$gt: new Date(now)},
        }),
        roadSpeed.find({
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

exports.getRoadSpeedCollection = getRoadSpeedCollection;
exports.queryRoadSpeed = queryRoadSpeed;
exports.queryRoadSpeedIncrement = queryRoadSpeedIncrement;

if (require.main === module) {
    (async () => {
        const result = await queryRoadSpeed(
            "test", "2021-01-24T21:10:00.000Z","2021-01-24T21:20:00.000Z"
        )
        console.dir(result);
    })()
}
