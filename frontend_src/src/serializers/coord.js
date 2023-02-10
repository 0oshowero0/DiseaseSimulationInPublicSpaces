import { Coordinate } from '../proto/api_pb'

export function createCoord(lng, lat) {
    const coord = new Coordinate();
    coord.setLng(lng)
    coord.setLat(lat)
    return coord
}

export const arr2coordObj = ([lng, lat]) => ({lng, lat})
export const coordObj2arr = ({lng, lat}) => ([lng, lat])
