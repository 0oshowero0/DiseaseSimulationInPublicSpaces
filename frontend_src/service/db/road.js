const _ = require("lodash")
const { getCollection } = require("./db");

async function getRoadCollection() {
    return await getCollection("Road")
}


/**
 * 从数据库查询
 * @param collection 数据集
 * @param level 街道显示等级
 * @param skip 从哪里开始
 * @param limit 单次长度限制
 * @returns {Promise<[]>}
 */
async function queryRoad(collection="test", level= 1, skip = 0, limit = 1000) {
    const road = await getRoadCollection()
    return road.find({
        collection, level
    }).skip(skip).limit(limit).toArray()
}

exports.getPositionCollection = getRoadCollection;
exports.queryRoad = queryRoad;

if (require.main === module) {
    (async () => {
        const result = await queryRoad(
            "test"
        )
        console.dir(result);
    })()
}
