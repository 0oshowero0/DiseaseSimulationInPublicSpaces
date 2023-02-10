const trans = ([x, y]) => [y, x]

export function loadRectAreaFromJson(data) {
  const result = {}
  Object.values(data).forEach(o => result[o["ID"]] = [trans(o["down_left"]), trans(o["down_right"]), trans(o["top_right"]), trans(o["top_left"])])
  return result
}
