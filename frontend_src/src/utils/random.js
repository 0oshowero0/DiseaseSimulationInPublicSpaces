export const randomColor = () => {
  const single = () => Math.floor(Math.random() * 256)
  return `rgb(${single()}, ${single()}, ${single()})`
}

export function randomColorAround(base, round) {
  const single = (std) => Math.min(Math.max(Math.floor(std + Math.random() * round - round / 2), 0), 255)
  return `rgb(${single(base[0])}, ${single(base[1])}, ${single(base[2])})`
}
