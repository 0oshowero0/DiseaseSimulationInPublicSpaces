import {lerpCoord} from "../../../../utils/animation";
import {genPersonality} from "../../../../emulator/personality";
import {evalJSONObjectWithShit} from "../../../../utils/ployfill";

export function loadPeopleDataFromJson(data) {
  const positions = {}
  const info = {}
  Object.values(data).forEach(json => {
    // 这。。。
    const d = (typeof json==='string') ?evalJSONObjectWithShit(json):json;

    const id = d.state['passenger_ID2']
    positions[id] = {
      start: d.state['start_time'],
      data: d.trajectory.map(([x, y]) => [x, 822 - y]),
    }
    let pInfo = d.state
    if (pInfo.gender === undefined || pInfo.age === undefined) {
      pInfo = { ...pInfo, ...genPersonality() }
    }
    info[id] = pInfo
  })
  return [positions, info]
}

export function getPositionMapFromAllPosition(positions, now, period=1) {
  const result = {}
  Object.entries(positions).forEach(([id, p]) => {
    const time = (now - p.start) / period
    if(time < 0 || time + 1 >= p.data.length || p.data.length < 2) {
      return
    }
    const index = Math.floor(time)
    const degree = time - index
    // if (!p.data[index] || !p.data[index + 1]) {
    //   debugger
    // }
    result[id] = lerpCoord(p.data[index], p.data[index + 1], degree)
  })
  return result
}
