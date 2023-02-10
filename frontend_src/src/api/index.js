import { ApiServiceClient } from '../proto/api_grpc_web_pb'
import { GetRoutesRequest, GetRoadsRequest, GetRoadSpeedsRequest, GetRoadChartsRequest, GetRoadChartsIncrementRequest } from '../proto/api_pb'
import {date2ts, tsObj2date} from "../serializers/timestamp";
import {coordObj2arr, createCoord} from "../serializers/coord";

const host = process.env.REACT_APP_API_BASE_URL
console.log("host", process.env.REACT_APP_API_BASE_URL)

const apiService = new ApiServiceClient(host);

const enableDevTools = window.__GRPCWEB_DEVTOOLS__ || (() => {});
enableDevTools([
    apiService,
]);

/**
 * 加载附近的路线点
 * @param lng
 * @param lat
 * @param minDistance
 * @param maxDistance
 * @param startTime {Date}
 * @param endTime {Date}
 * @param collection
 * @param skip
 * @param limit
 */
function loadNearRoute({lng, lat, minDistance, maxDistance, startTime, endTime, collection, skip, limit}) {
    return new Promise((resolve, reject) => {
        const request = new GetRoutesRequest();

        request.setCollection(collection)
        request.setCenter(createCoord(lng, lat))
        request.setMax(maxDistance ?? 10000)
        request.setMin(minDistance)
        request.setStart(date2ts(startTime))
        request.setEnd(date2ts(endTime))
        request.setLimit(limit ?? 1000)
        request.setSkip(skip)

        apiService.getRoutes(request, {}, function (err, response) {
            if(err) {
                reject(err);
                return
            }
            const data = response.toObject().resultsList
            const results = data.map(obj => {
                const { start, routeList, ...rest } = obj
                return {
                    start: tsObj2date(start),
                    route: routeList.map(coordObj2arr),
                    ...rest,
                }
            })
            resolve(results)
        })
    })
}


/**
 * 加载全部道路
 * @param level {Number}
 * @param collection
 * @param skip
 * @param limit
 */
function loadRoads({level, collection, skip, limit}) {
    return new Promise((resolve, reject) => {
        const request = new GetRoadsRequest();
        request.setLevel(level)
        request.setCollection(collection)
        request.setLimit(limit ?? 20000)

        apiService.getRoads(request, {}, function (err, response) {
            if(err) {
                reject(err);
                return
            }
            const data = response.toObject().resultsList
            const results = data.map(obj => {
                const { shapeList, ...rest } = obj
                return {
                    shape: {
                        type: "LineString",
                        coordinates: shapeList.map(coordObj2arr)
                    },
                    ...rest,
                }
            })
            resolve(results)
        })
    })
}


/**
 * 加载道路平均速度
 * @param startTime {Date}
 * @param endTime {Date}
 * @param collection
 * @param skip
 * @param limit
 */
function loadRoadSpeeds({startTime, endTime, collection, skip, limit}) {
    return new Promise((resolve, reject) => {
        const request = new GetRoadSpeedsRequest();

        request.setCollection(collection)
        request.setStart(date2ts(startTime))
        request.setEnd(date2ts(endTime))
        request.setLimit(limit ?? 20000)
        request.setSkip(skip)

        apiService.getRoadSpeeds(request, {}, function (err, response) {
            if(err) {
                reject(err);
                return
            }
            const data = response.toObject().resultsList
            const results = data.map(obj => {
                const { start, end, ...rest } = obj
                return {
                    start: tsObj2date(start),
                    end: tsObj2date(end),
                    ...rest,
                }
            })
            resolve(results)
        })
    })
}


/**
 * 加载道路表格
 * @param type
 * @param startTime {Date}
 * @param endTime {Date}
 * @param collection
 * @param skip
 * @param limit
 */
function loadCharts({type, startTime, endTime, collection, skip, limit}) {
    return new Promise((resolve, reject) => {
        const request = new GetRoadChartsRequest();

        request.setCollection(collection)
        request.setStart(date2ts(startTime))
        request.setEnd(date2ts(endTime))
        request.setLimit(limit ?? 20000)
        request.setSkip(skip)
        request.setType(type)

        apiService.getRoadCharts(request, {}, function (err, response) {
            if(err) {
                reject(err);
                return
            }
            const data = response.toObject().resultsList
            const results = data.map(obj => {
                const { start, end, data, ...rest } = obj
                return {
                    start: tsObj2date(start),
                    end: tsObj2date(end),
                    data: JSON.parse(data),
                    ...rest,
                }
            })
            resolve(results)
        })
    })
}


/**
 * 增量加载道路表格
 * @param type
 * @param now {Date}
 * @param last {Date}
 * @param collection
 * @param skip
 * @param limit
 */
function loadChartsIncrement({type, now, last = 0, collection, skip, limit}) {
    return new Promise((resolve, reject) => {
        const request = new GetRoadChartsIncrementRequest();

        request.setCollection(collection)
        request.setNow(date2ts(new Date(now)))
        request.setLast(date2ts(new Date(last)))
        request.setLimit(limit ?? 20000)
        request.setSkip(skip)
        request.setType(type)

        apiService.getRoadChartsIncrement(request, {}, function (err, response) {
            if(err) {
                reject(err);
                return
            }
            debugger
            // 处理results = [] 的情况还有问题
            let { resultsList: results, validRangeStart, validRangeEnd } = response.toObject()
            results = results.map(obj => {
                const { start, end, data, ...rest } = obj
                return {
                    start: tsObj2date(start),
                    end: tsObj2date(end),
                    data: JSON.parse(data),
                    ...rest,
                }
            })
            resolve({results, start: tsObj2date(validRangeStart), end: tsObj2date(validRangeEnd) })
        })
    })
}

const api = {
    loadNearRoute, loadRoads, loadRoadSpeeds, loadCharts, loadChartsIncrement
}

export default api
