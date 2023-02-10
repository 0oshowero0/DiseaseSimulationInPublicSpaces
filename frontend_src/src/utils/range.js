export function range (...size) {
  if (size.length === 0) {
    return []
  }
  if (size.length === 1) {
    if (size[0] <= 0)
      return []
    return [...Array(size[0]).keys()]
  }
  let [start, end, skip] = [0, 0, 1]
  if (size.length === 2) {
    [start, end] = size
  }
  if (size.length === 3) {
    [start, end, skip] = size
  }
  return range(Math.floor((end - start) / skip)).map(i => start + i * skip)
}
