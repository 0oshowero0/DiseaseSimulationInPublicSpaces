import _ from 'lodash'
import {mergeObjToOrigin} from "../utils/merge";
import {range} from "../utils/range";

export function calcExpect({age, gender}) {
  const [MALE, FEMALE] = [0, 1]
  const [M0, F0] = [0.0036 / 100, 0.0018 / 100]
  if (age === undefined || gender === undefined) {
    return 0
  }
  const base = gender === MALE ? M0 : F0
  if (age <= 20) {
    return base
  }
  if (age >= 80) {
    return gender === MALE ? 0.1: 0.05
  }
  return base * Math.pow(2750, (age - 20) / 60)
}

/**
 *
 * @param personInfo 单个个体的信息
 * @param time 当前的时间戳
 * @return {infected: boolean, exposing: boolean, exposed: boolean, infecting: boolean}
 *  exposing 是当下是否暴露
 *  infecting 是当下是否感染
 *  exposed 是否暴露过
 *  infected 为是否感染过
 */
export function getInfectedState(personInfo = {}, time) {
  const result = {
    exposing: false,
    infecting: false,
    exposed: false,
    infected: false,
  }
  if (!personInfo) {
    // throw new Error('no this info')
    console.warn('no this info')
    return result
  }
  const { begin_exposed, end_exposed, infection_time } = personInfo
  let exposedSpans = []
  if (begin_exposed && end_exposed) {
    exposedSpans = _.zip(begin_exposed, end_exposed)
  }
  const isUndefined = x => x === undefined
  result.exposed = exposedSpans.length > 0
  result.infected = !isUndefined(infection_time) && infection_time >= 0
  result.exposing = exposedSpans.findIndex(([start, end]) => time >= start && time <= end) >= 0
  result.infecting = result.infected && time >= infection_time
  return result
}

/**
 * 自动更新状态，很脏的魔法
 * @param info
 * @param time
 */
export function updateInfectedStateInfo(info, time) {
  // debugger
  Object.entries(info).forEach(([id, person]) => {
    const result = getInfectedState(person, time)
    mergeObjToOrigin(person, result)
  })
  return info
}

function calcExposedAccData(info, start, end, interval, accFunc=(info) => 1) {
  const result = range(start, end, interval).map(() => 0)
  Object.entries(info).forEach(([id, pInfo]) => {
    const { begin_exposed, end_exposed } = pInfo
    if (begin_exposed && end_exposed) {
      // const exposedSpans = _.zip([begin_exposed, end_exposed])
      // exposedSpans.forEach(([spanStart, spanEnd]) => {
      //   for(let i = 0; start + i * interval < end; i++) {
      //     const now = start + i * interval
      //     if (spanStart => now && spanEnd < now) {
      //       // debugger
      //       result[i] += accFunc(pInfo)
      //     }
      //   }
      // })
      const min = Math.min(...begin_exposed)
      if (min !== undefined && min >= 0) {
        for(let i = 0; start + i * interval < end; i++) {
          const now = start + i * interval
          if (min <= now) {
            // debugger
            result[i] += accFunc(pInfo)
          }
        }
      }
    }
  })
  return result
}

function calcInfectedAccData(info, start, end, interval, accFunc=(info) => 1) {
  const result = range(start, end, interval).map(() => 0)
  Object.entries(info).forEach(([id, pInfo]) => {
    const { infection_time } = pInfo
    if (infection_time !== undefined && infection_time >= 0) {
      for(let i = 0; start + i * interval < end; i++) {
        const now = start + i * interval
        if (infection_time <= now) {
          // debugger
          result[i] += accFunc(pInfo)
        }
      }
    }
  })
  return result
}

export function calcInfectedGraphData(info, start, end, interval) {
  const exposedCount = calcExposedAccData(info, start, end, interval)
  // const expectCount = calcExposedAccData(info, start, end, interval, calcExpect).map(v => v.toPrecision(7))
  const infectedCount = calcInfectedAccData(info, start, end, interval)
  return { exposedCount, infectedCount }
}
