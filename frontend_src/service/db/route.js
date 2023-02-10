const _ = require("lodash")
const { getCollection } = require("./db");

async function getPositionCollection() {
    return await getCollection("CarPosition")
}

function preproessRoute(routes) {
    // 检查连续性并分割不连续
    const INTERVAL = 1000;
    const data = []
    const addToData = (obj, route) => data.push({ ...obj, route: [...route] })
    routes.forEach(obj => {
        let route = []
        obj.route.forEach(r => {
            if (!route.length) {
                route.push(r)
                return
            }
            const last = new Date(_.last(route).timestamp)
            const now = new Date(r.timestamp)
            if (now - last === INTERVAL) {
                route.push(r)
            } else {
                addToData(obj, route)
                route = [r]
            }
        })
        addToData(obj, route)
    })
    return data
}

/**
 * 从数据库查询
 * @param lng 经度（100多）
 * @param lat 维度（40左右）
 * @param start {string} 开始时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param end {string} 结束时间 ISO时间字符串 如"2021-01-24T16:01:00.000Z"
 * @param collection 数据集
 * @param maxDistance 最大距离，单位米
 * @param minDistance 最小距离，单位米
 * @param skip
 * @param limit 单次长度限制
 * @returns {Promise<[]>}
 */
async function queryRoute(lng, lat, start, end, collection="test", maxDistance=10000, minDistance=0, skip = 0, limit = 10000) {
    const position = await getPositionCollection()
    const raw = await position.aggregate([
        {
            $geoNear: {
                near: {"type": "Point", "coordinates": [lng, lat]},
                distanceField: "distance",
                maxDistance,  // 单位为米
                minDistance,  // 单位为米
                query: {
                    timestamp: {
                        $gte: start,
                        $lt: end,
                    },
                    collection,
                },
                key: "location",
            }
        },
        {$group: {_id: "$car"}},
        {$group: {_id: null, cars: {$addToSet: "$_id"}}},
        {
            $lookup: {
                from: "CarPosition",
                let: {cars: "$cars"},
                pipeline: [
                    {
                        $match: {
                            collection,
                            timestamp: {
                                $gte: start,
                                $lt: end,
                            },
                            // 这行不能用索引，因为lookup中用到let的参数需要在expr内，但是这又会
                            $expr: {$in: ["$car", "$$cars"]},
                        }
                    },
                ],
                as: "routes",
            }
        },
        { $unwind: "$routes" },
        { $set: {
                _id : "$routes._id",
                car: "$routes.car",
                timestamp: "$routes.timestamp",
                location: "$routes.location",
                speed: "$routes.speed",
                collection: "$routes.collection"
            }
        },
        { $project: { cars: 0, routes: 0 } },
        { $sort: { collection:1, car: 1, timestamp: 1 } },
        { $group : {
                _id : { collection: "$collection", car : "$car" },
                route: { $push: { location: "$location", timestamp: "$timestamp", speed: "$speed" } } },
        },
        { $set: {
                collection : "$_id.collection",
                car: "$_id.car",
            }
        },
        { $project: { _id: 0 } },
    ]).skip(skip).limit(limit).toArray();
    return preproessRoute(raw)
}

exports.getPositionCollection = getPositionCollection;
exports.queryRoute = queryRoute;

if (require.main === module) {
    (async () => {
        const result = await queryRoute(
            116.55117772480727,
            39.82784157034311,
            "2021-01-24T16:00:00.000Z",
            "2021-01-24T16:01:00.000Z",
            "test"
        )
        console.dir(result);
    })()
}
