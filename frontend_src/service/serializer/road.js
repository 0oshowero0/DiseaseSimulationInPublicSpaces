const {arr2coord} = require("./coord");
const trans2RoadResponse = (data) =>
    data.map(road => {
        const { location, ...rest } = road;
        return {
            shape: location.coordinates
                .map(([lat, lng]) => ([lng, lat]))
                .map(arr2coord),
            ...rest,
        }
    })

exports.trans2RoadResponse = trans2RoadResponse
