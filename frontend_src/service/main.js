const path = require('path');
const assert = require('assert');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const Sentry = require("@sentry/node");
const Tracing = require("@sentry/tracing");
const {trans2RoadChartIncrementResponse} = require("./serializer/chart");
const {queryRoadChartIncrement} = require("./db/chart");
const {trans2RoadSpeedIncrementResponse} = require("./serializer/road-speed");
const {queryRoadSpeedIncrement} = require("./db/road-speed");
const {trans2RoadChartResponse} = require("./serializer/chart");
const {trans2RoadSpeedResponse} = require("./serializer/road-speed");
const {queryRoadChart} = require("./db/chart");
const {queryRoadSpeed} = require("./db/road-speed");
const {trans2RoadResponse} = require("./serializer/road");
const {queryRoad} = require("./db/road");
const {trans2CarRouteResponse} = require("./serializer/route");
const {tsObj2date} = require("./serializer/timestamp");
const {queryRoute} = require("./db/route");

const PROTO_PATH = path.resolve('../protocol/api.proto');

const packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true
    });
const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
const api = protoDescriptor.fiblab.api;

Sentry.init({
    dsn: process.env.NODEJS_SENTRY_SDN ?? "https://c067961ba3a44fbc9ab43bea9d778bb5@o487764.ingest.sentry.io/5546876",
    environment: process.env.NODEJS_SENTRY_ENV ?? "local",
    // We recommend adjusting this value in production, or using tracesSampler
    // for finer control
    // tracesSampleRate: 1.0,
});

/**
 * @param {!Object} call
 * @return {!Object} metadata
 */
function copyMetadata(call) {
    const metadata = call.metadata.getMap();
    const response_metadata = new grpc.Metadata();
    for (const key in metadata) {
        response_metadata.set(key, metadata[key]);
    }
    return response_metadata;
}

/**
 * @param {!Object} call
 * @param {function(any, any, any):?} callback
 */
function doTest(call, callback) {
    console.log("receive test request:", call.request)
    callback(null, {
        msg: call.request.msg
    }, copyMetadata(call));
}


/**
 * @param {!Object} call
 * @param {function(any, any, any):?} callback
 */
async function doGetRoutes(call, callback) {
    const { center, min, max, start, end, collection, skip, limit } = call.request;
    const data = await queryRoute(
        center.lng, center.lat,
        tsObj2date(start).toISOString(),
        tsObj2date(end).toISOString(),
        collection,
        max, min,
        skip, limit
    )
    const results = trans2CarRouteResponse(data)
    callback(null, { results }, copyMetadata(call));
}


/**
 * @param {!Object} call
 * @param {function(any, any, any):?} callback
 */
async function doGetRoad(call, callback) {
    const { level, collection, limit, skip } = call.request;
    const data = await queryRoad(collection, level, skip, limit);
    const results = trans2RoadResponse(data)
    callback(null, { results }, copyMetadata(call));
}


/**
 * @param {!Object} call
 * @param {function(any, any, any):?} callback
 */
async function doGetRoadSpeeds(call, callback) {
    const { collection, start, end, limit, skip } = call.request;
    const data = await queryRoadSpeed(
      collection,
      tsObj2date(start).toISOString(),
      tsObj2date(end).toISOString(),
      skip,
      limit,
    );
    const results = trans2RoadSpeedResponse(data)
    callback(null, { results }, copyMetadata(call));
}


/**
 * @param {!Object} call
 * @param {function(any, any, any):?} callback
 */
async function doGetRoadSpeedsIncrement(call, callback) {
    const { collection, last, now, limit, skip } = call.request;
    const data = await queryRoadSpeedIncrement(
      collection,
      tsObj2date(last).toISOString(),
      tsObj2date(now).toISOString(),
      skip,
      limit,
    );
    const results = trans2RoadSpeedIncrementResponse(data)
    callback(null, results, copyMetadata(call));
}


/**
 * @param {!Object} call
 * @param {function(any, any, any):?} callback
 */
async function doGetRoadCharts(call, callback) {
    const { collection, type, start, end, limit, skip } = call.request;
    const data = await queryRoadChart(
        collection,
        tsObj2date(start).toISOString(),
        tsObj2date(end).toISOString(),
        type,
        skip,
        limit,
    );
    const results = trans2RoadChartResponse(data)
    callback(null, { results }, copyMetadata(call));
}


/**
 * @param {!Object} call
 * @param {function(any, any, any):?} callback
 */
async function doGetRoadChartsIncrement(call, callback) {
    const { collection, type, last, now, limit, skip } = call.request;
    const data = await queryRoadChartIncrement(
      collection, type,
      tsObj2date(last).toISOString(),
      tsObj2date(now).toISOString(),
      skip, limit,
    );
    const results = trans2RoadChartIncrementResponse(data)
    callback(null, results, copyMetadata(call));
}

/**
 * Get a new server with the handler functions in this file bound to the
 * methods it serves.
 * @return {!Server} The new server object
 */
function getServer() {
    const server = new grpc.Server();
    server.addService(api.ApiService.service, {
        test: doTest,
        getRoutes: doGetRoutes,
        getRoads: doGetRoad,
        getRoadSpeeds: doGetRoadSpeeds,
        getRoadSpeedsIncrement: doGetRoadSpeedsIncrement,
        getRoadCharts: doGetRoadCharts,
        getRoadChartsIncrement: doGetRoadChartsIncrement,
    });
    return server;
}

if (require.main === module) {
    setImmediate(() => {
        try {
            const apiServer = getServer();
            apiServer.bindAsync(
              process.env.NODEJS_HOST ?? '0.0.0.0:9090', grpc.ServerCredentials.createInsecure(), (err, port) => {
                  assert.ifError(err);
                  apiServer.start();
              });
            console.log("Service Started...")
        } catch (e) {
            Sentry.captureException(e);
        }
    })
}

exports.getServer = getServer;
