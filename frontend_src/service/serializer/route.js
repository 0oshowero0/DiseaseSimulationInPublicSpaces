const {arr2coord} = require("./coord");
const {date2tsObj} = require("./timestamp");

const transPosition = position => arr2coord(position.location.coordinates)

const trans2CarRouteResponse = (data) =>
    data.map(car => {
        const name = car.car;
        const start = date2tsObj(new Date(car.route.length ? car.route[0].timestamp : 0));
        const initSpeed = car.route.length ? car.route[0].speed : 0;
        const lastSpeed = car.route.length ? car.route[car.route.length - 1].speed : 0;
        const route = car.route.map(transPosition)
        return { name, start, route, initSpeed, lastSpeed }
    })

exports.trans2CarRouteResponse = trans2CarRouteResponse
