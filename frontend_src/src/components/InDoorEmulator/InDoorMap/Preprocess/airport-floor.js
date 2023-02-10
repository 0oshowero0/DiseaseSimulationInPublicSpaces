const trans = ([x, y]) => [y, x]

export function loadAirportFloorFromJson(data) {
  return Object.values(data).map(o => o.first).map(trans)
}
