export function mergeObjToOrigin(origin, ...rest) {
  rest.forEach(merged => {
    Object.entries(merged).forEach(([key, value]) => {
      origin[key] = value
    })
  })
  return origin
}
