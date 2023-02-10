function sum(...arr) {
  return  arr.reduce((a, b) => a + b)
}

export function getDistance(coord1, coord2) {
  const [x1, y1] = coord1
  const [x2, y2] = coord2
  return Math.sqrt(sum(...[x2 - x1, y2 - y1].map(Math.abs).map(a => a * a)))
}
