db.CarPosition.aggregate([
    { $geoNear: {
            near: { "type": "Point", "coordinates": [116.55117772480727, 39.82784157034311] },
            distanceField: "distance",
            maxDistance: 10000,  // 单位为米
            query: {
                timestamp: {
                    $gte: "2021-01-24T16:00:00.000Z",
                    $lt: "2021-01-24T16:01:00.000Z",
                },
                collection: "test",
            },
            key: "location",
        }
    },
    { $group : { _id : { "car": "$car", "collection": "$collection" } } },
    { $project: { "_id": 0, "car": "$_id.car", "collection": "$_id.collection" } },

//【方法一：纯Lookup法开始】
// 本来以为会有优化，实际没卵用的方法
//  { $lookup: {
//			from: "CarPosition",
//			localField: "car",
//			foreignField: "car",
//			as: "routes"
//		}
//	},
//	{
//      $project: {
//         routes: {
//            $filter: {
//               input: "$routes",
//               as: "item",
//               cond: { $and:
//								 [
//									 { $eq: [ "$$item.collection",  "test" ] },
//									 { $gte: [ "$$item.timestamp", "2021-01-24T16:00:00.000Z" ] },
//									 { $lt: [ "$$item.timestamp", "2021-01-24T16:01:00.000Z" ] },
//								 ]
//							}
//            }
//         }
//      }
//   },
//【纯Lookup法结束】

//【方法二：Lookup Pipeline法开始】
// 代码上最优雅的方法，但是傻逼的地方是expr不会走索引，智障吧！
//  { $lookup: {
//			 from: "CarPosition",
//			 let: { car: "$car", collection: "$collection" },
//			 pipeline: [
//					{ $match:
//						 { $expr:
//								{ $and:
//									 [
//										 { $eq: [ "$collection",  "$$collection" ] },
//										 { $eq: [ "$car",  "$$car" ] },
//										 { $gte: [ "$timestamp", "2021-01-24T16:00:00.000Z" ] },
//										 { $lt: [ "$timestamp", "2021-01-24T16:01:00.000Z" ] },
//									 ]
//								}
//						 }
//					},
//					{ $project: { _id: 0, collection: 0, car: 0, timestamp: 1, location: 1, speed: 1 } },
//					{ $sort: { timestamp: 1 } },
//			 ],
//			 as: "routes"
//		}
//	},
//【Lookup Pipeline法结束】

//【方法三：Lookup Pipeline 半优化法开始】
//  { $lookup: {
//			 from: "CarPosition",
//			 let: { car: "$car", collection: "$collection" },
//			 pipeline: [
//					{ $match:{
//							collection: "test",
//							timestamp: {
//								$gte: "2021-01-24T16:00:00.000Z",
//								$lt: "2021-01-24T16:01:00.000Z",
//							},
//							// 这行不能用索引，因为lookup中用到let的参数需要在expr内，但是这又会
//							$expr: { $eq: ["$car", "$$car"] },
//						}
//					},
//					{ $project: { _id: 0, collection: 0, car: 0 } },
//					{ $sort: { timestamp: 1 } },
//			 ],
//			 as: "routes"
//		}
//	},
//【Lookup Pipeline 半优化法结束】

// 方法四，拆分后分次查询法
])

//【方法五：数组法】
db.CarPosition.aggregate([
    { $geoNear: {
            near: { "type": "Point", "coordinates": [116.55117772480727, 39.82784157034311] },
            distanceField: "distance",
            maxDistance: 10000,  // 单位为米
            query: {
                timestamp: {
                    $gte: "2021-01-24T16:00:00.000Z",
                    $lt: "2021-01-24T16:01:00.000Z",
                },
                collection: "test",
            },
            key: "location",
        }
    },
    { $group : { _id : "$car" } },
    { $group : { _id : null, cars: { $addToSet: "$_id" } } },
    { $lookup: {
            from: "CarPosition",
            let: { cars: "$cars" },
            pipeline: [
                { $match:{
                        collection: "test",
                        timestamp: {
                            $gte: "2021-01-24T16:00:00.000Z",
                            $lt: "2021-01-24T16:01:00.000Z",
                        },
                        // 这行不能用索引，因为lookup中用到let的参数需要在expr内，但是这又会
                        $expr: { $in: ["$car", "$$cars"] },
                    }
                },
            ],
            as: "routes"
        }
    },
    { $unwind: "$routes" },
    { $project: { _id: 0, cars: 0, "routes.car": "$car" } },
])
//【数组法结束】
