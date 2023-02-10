/**
 * @fileoverview gRPC-Web generated client stub for fiblab.api
 * @enhanceable
 * @public
 */

// GENERATED CODE -- DO NOT EDIT!


/* eslint-disable */
// @ts-nocheck



const grpc = {};
grpc.web = require('grpc-web');


var google_protobuf_timestamp_pb = require('google-protobuf/google/protobuf/timestamp_pb.js')

var google_protobuf_struct_pb = require('google-protobuf/google/protobuf/struct_pb.js')
const proto = {};
proto.fiblab = {};
proto.fiblab.api = require('./api_pb.js');

/**
 * @param {string} hostname
 * @param {?Object} credentials
 * @param {?Object} options
 * @constructor
 * @struct
 * @final
 */
proto.fiblab.api.ApiServiceClient =
    function(hostname, credentials, options) {
  if (!options) options = {};
  options['format'] = 'text';

  /**
   * @private @const {!grpc.web.GrpcWebClientBase} The client
   */
  this.client_ = new grpc.web.GrpcWebClientBase(options);

  /**
   * @private @const {string} The hostname
   */
  this.hostname_ = hostname;

};


/**
 * @param {string} hostname
 * @param {?Object} credentials
 * @param {?Object} options
 * @constructor
 * @struct
 * @final
 */
proto.fiblab.api.ApiServicePromiseClient =
    function(hostname, credentials, options) {
  if (!options) options = {};
  options['format'] = 'text';

  /**
   * @private @const {!grpc.web.GrpcWebClientBase} The client
   */
  this.client_ = new grpc.web.GrpcWebClientBase(options);

  /**
   * @private @const {string} The hostname
   */
  this.hostname_ = hostname;

};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.fiblab.api.Test,
 *   !proto.fiblab.api.Test>}
 */
const methodDescriptor_ApiService_test = new grpc.web.MethodDescriptor(
  '/fiblab.api.ApiService/test',
  grpc.web.MethodType.UNARY,
  proto.fiblab.api.Test,
  proto.fiblab.api.Test,
  /**
   * @param {!proto.fiblab.api.Test} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.Test.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.fiblab.api.Test,
 *   !proto.fiblab.api.Test>}
 */
const methodInfo_ApiService_test = new grpc.web.AbstractClientBase.MethodInfo(
  proto.fiblab.api.Test,
  /**
   * @param {!proto.fiblab.api.Test} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.Test.deserializeBinary
);


/**
 * @param {!proto.fiblab.api.Test} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.fiblab.api.Test)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.fiblab.api.Test>|undefined}
 *     The XHR Node Readable Stream
 */
proto.fiblab.api.ApiServiceClient.prototype.test =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/fiblab.api.ApiService/test',
      request,
      metadata || {},
      methodDescriptor_ApiService_test,
      callback);
};


/**
 * @param {!proto.fiblab.api.Test} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.fiblab.api.Test>}
 *     A native promise that resolves to the response
 */
proto.fiblab.api.ApiServicePromiseClient.prototype.test =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/fiblab.api.ApiService/test',
      request,
      metadata || {},
      methodDescriptor_ApiService_test);
};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.fiblab.api.GetRoutesRequest,
 *   !proto.fiblab.api.GetRoutesResponse>}
 */
const methodDescriptor_ApiService_getRoutes = new grpc.web.MethodDescriptor(
  '/fiblab.api.ApiService/getRoutes',
  grpc.web.MethodType.UNARY,
  proto.fiblab.api.GetRoutesRequest,
  proto.fiblab.api.GetRoutesResponse,
  /**
   * @param {!proto.fiblab.api.GetRoutesRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoutesResponse.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.fiblab.api.GetRoutesRequest,
 *   !proto.fiblab.api.GetRoutesResponse>}
 */
const methodInfo_ApiService_getRoutes = new grpc.web.AbstractClientBase.MethodInfo(
  proto.fiblab.api.GetRoutesResponse,
  /**
   * @param {!proto.fiblab.api.GetRoutesRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoutesResponse.deserializeBinary
);


/**
 * @param {!proto.fiblab.api.GetRoutesRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.fiblab.api.GetRoutesResponse)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.fiblab.api.GetRoutesResponse>|undefined}
 *     The XHR Node Readable Stream
 */
proto.fiblab.api.ApiServiceClient.prototype.getRoutes =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoutes',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoutes,
      callback);
};


/**
 * @param {!proto.fiblab.api.GetRoutesRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.fiblab.api.GetRoutesResponse>}
 *     A native promise that resolves to the response
 */
proto.fiblab.api.ApiServicePromiseClient.prototype.getRoutes =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoutes',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoutes);
};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.fiblab.api.GetRoadsRequest,
 *   !proto.fiblab.api.GetRoadsResponse>}
 */
const methodDescriptor_ApiService_getRoads = new grpc.web.MethodDescriptor(
  '/fiblab.api.ApiService/getRoads',
  grpc.web.MethodType.UNARY,
  proto.fiblab.api.GetRoadsRequest,
  proto.fiblab.api.GetRoadsResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadsRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadsResponse.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.fiblab.api.GetRoadsRequest,
 *   !proto.fiblab.api.GetRoadsResponse>}
 */
const methodInfo_ApiService_getRoads = new grpc.web.AbstractClientBase.MethodInfo(
  proto.fiblab.api.GetRoadsResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadsRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadsResponse.deserializeBinary
);


/**
 * @param {!proto.fiblab.api.GetRoadsRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.fiblab.api.GetRoadsResponse)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.fiblab.api.GetRoadsResponse>|undefined}
 *     The XHR Node Readable Stream
 */
proto.fiblab.api.ApiServiceClient.prototype.getRoads =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoads',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoads,
      callback);
};


/**
 * @param {!proto.fiblab.api.GetRoadsRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.fiblab.api.GetRoadsResponse>}
 *     A native promise that resolves to the response
 */
proto.fiblab.api.ApiServicePromiseClient.prototype.getRoads =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoads',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoads);
};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.fiblab.api.GetRoadSpeedsRequest,
 *   !proto.fiblab.api.GetRoadSpeedsResponse>}
 */
const methodDescriptor_ApiService_getRoadSpeeds = new grpc.web.MethodDescriptor(
  '/fiblab.api.ApiService/getRoadSpeeds',
  grpc.web.MethodType.UNARY,
  proto.fiblab.api.GetRoadSpeedsRequest,
  proto.fiblab.api.GetRoadSpeedsResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadSpeedsRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadSpeedsResponse.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.fiblab.api.GetRoadSpeedsRequest,
 *   !proto.fiblab.api.GetRoadSpeedsResponse>}
 */
const methodInfo_ApiService_getRoadSpeeds = new grpc.web.AbstractClientBase.MethodInfo(
  proto.fiblab.api.GetRoadSpeedsResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadSpeedsRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadSpeedsResponse.deserializeBinary
);


/**
 * @param {!proto.fiblab.api.GetRoadSpeedsRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.fiblab.api.GetRoadSpeedsResponse)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.fiblab.api.GetRoadSpeedsResponse>|undefined}
 *     The XHR Node Readable Stream
 */
proto.fiblab.api.ApiServiceClient.prototype.getRoadSpeeds =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoadSpeeds',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoadSpeeds,
      callback);
};


/**
 * @param {!proto.fiblab.api.GetRoadSpeedsRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.fiblab.api.GetRoadSpeedsResponse>}
 *     A native promise that resolves to the response
 */
proto.fiblab.api.ApiServicePromiseClient.prototype.getRoadSpeeds =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoadSpeeds',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoadSpeeds);
};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.fiblab.api.GetRoadSpeedsIncrementRequest,
 *   !proto.fiblab.api.GetRoadSpeedsIncrementResponse>}
 */
const methodDescriptor_ApiService_getRoadSpeedsIncrement = new grpc.web.MethodDescriptor(
  '/fiblab.api.ApiService/getRoadSpeedsIncrement',
  grpc.web.MethodType.UNARY,
  proto.fiblab.api.GetRoadSpeedsIncrementRequest,
  proto.fiblab.api.GetRoadSpeedsIncrementResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadSpeedsIncrementRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadSpeedsIncrementResponse.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.fiblab.api.GetRoadSpeedsIncrementRequest,
 *   !proto.fiblab.api.GetRoadSpeedsIncrementResponse>}
 */
const methodInfo_ApiService_getRoadSpeedsIncrement = new grpc.web.AbstractClientBase.MethodInfo(
  proto.fiblab.api.GetRoadSpeedsIncrementResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadSpeedsIncrementRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadSpeedsIncrementResponse.deserializeBinary
);


/**
 * @param {!proto.fiblab.api.GetRoadSpeedsIncrementRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.fiblab.api.GetRoadSpeedsIncrementResponse)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.fiblab.api.GetRoadSpeedsIncrementResponse>|undefined}
 *     The XHR Node Readable Stream
 */
proto.fiblab.api.ApiServiceClient.prototype.getRoadSpeedsIncrement =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoadSpeedsIncrement',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoadSpeedsIncrement,
      callback);
};


/**
 * @param {!proto.fiblab.api.GetRoadSpeedsIncrementRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.fiblab.api.GetRoadSpeedsIncrementResponse>}
 *     A native promise that resolves to the response
 */
proto.fiblab.api.ApiServicePromiseClient.prototype.getRoadSpeedsIncrement =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoadSpeedsIncrement',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoadSpeedsIncrement);
};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.fiblab.api.GetRoadChartsRequest,
 *   !proto.fiblab.api.GetRoadChartsResponse>}
 */
const methodDescriptor_ApiService_getRoadCharts = new grpc.web.MethodDescriptor(
  '/fiblab.api.ApiService/getRoadCharts',
  grpc.web.MethodType.UNARY,
  proto.fiblab.api.GetRoadChartsRequest,
  proto.fiblab.api.GetRoadChartsResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadChartsRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadChartsResponse.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.fiblab.api.GetRoadChartsRequest,
 *   !proto.fiblab.api.GetRoadChartsResponse>}
 */
const methodInfo_ApiService_getRoadCharts = new grpc.web.AbstractClientBase.MethodInfo(
  proto.fiblab.api.GetRoadChartsResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadChartsRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadChartsResponse.deserializeBinary
);


/**
 * @param {!proto.fiblab.api.GetRoadChartsRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.fiblab.api.GetRoadChartsResponse)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.fiblab.api.GetRoadChartsResponse>|undefined}
 *     The XHR Node Readable Stream
 */
proto.fiblab.api.ApiServiceClient.prototype.getRoadCharts =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoadCharts',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoadCharts,
      callback);
};


/**
 * @param {!proto.fiblab.api.GetRoadChartsRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.fiblab.api.GetRoadChartsResponse>}
 *     A native promise that resolves to the response
 */
proto.fiblab.api.ApiServicePromiseClient.prototype.getRoadCharts =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoadCharts',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoadCharts);
};


/**
 * @const
 * @type {!grpc.web.MethodDescriptor<
 *   !proto.fiblab.api.GetRoadChartsIncrementRequest,
 *   !proto.fiblab.api.GetRoadChartsIncrementResponse>}
 */
const methodDescriptor_ApiService_getRoadChartsIncrement = new grpc.web.MethodDescriptor(
  '/fiblab.api.ApiService/getRoadChartsIncrement',
  grpc.web.MethodType.UNARY,
  proto.fiblab.api.GetRoadChartsIncrementRequest,
  proto.fiblab.api.GetRoadChartsIncrementResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadChartsIncrementRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadChartsIncrementResponse.deserializeBinary
);


/**
 * @const
 * @type {!grpc.web.AbstractClientBase.MethodInfo<
 *   !proto.fiblab.api.GetRoadChartsIncrementRequest,
 *   !proto.fiblab.api.GetRoadChartsIncrementResponse>}
 */
const methodInfo_ApiService_getRoadChartsIncrement = new grpc.web.AbstractClientBase.MethodInfo(
  proto.fiblab.api.GetRoadChartsIncrementResponse,
  /**
   * @param {!proto.fiblab.api.GetRoadChartsIncrementRequest} request
   * @return {!Uint8Array}
   */
  function(request) {
    return request.serializeBinary();
  },
  proto.fiblab.api.GetRoadChartsIncrementResponse.deserializeBinary
);


/**
 * @param {!proto.fiblab.api.GetRoadChartsIncrementRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @param {function(?grpc.web.Error, ?proto.fiblab.api.GetRoadChartsIncrementResponse)}
 *     callback The callback function(error, response)
 * @return {!grpc.web.ClientReadableStream<!proto.fiblab.api.GetRoadChartsIncrementResponse>|undefined}
 *     The XHR Node Readable Stream
 */
proto.fiblab.api.ApiServiceClient.prototype.getRoadChartsIncrement =
    function(request, metadata, callback) {
  return this.client_.rpcCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoadChartsIncrement',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoadChartsIncrement,
      callback);
};


/**
 * @param {!proto.fiblab.api.GetRoadChartsIncrementRequest} request The
 *     request proto
 * @param {?Object<string, string>} metadata User defined
 *     call metadata
 * @return {!Promise<!proto.fiblab.api.GetRoadChartsIncrementResponse>}
 *     A native promise that resolves to the response
 */
proto.fiblab.api.ApiServicePromiseClient.prototype.getRoadChartsIncrement =
    function(request, metadata) {
  return this.client_.unaryCall(this.hostname_ +
      '/fiblab.api.ApiService/getRoadChartsIncrement',
      request,
      metadata || {},
      methodDescriptor_ApiService_getRoadChartsIncrement);
};


module.exports = proto.fiblab.api;

