import simpleheat from "simpleheat/simpleheat";
import classifyPoint from "robust-point-in-polygon"
import {range} from "../utils/range";
import {getDistance} from "../utils/distance";
import AirportRegion from "../assets/in-doors/airport/areas/airport_region.json";

export function getCrowdRiskDegree({ gender, age }) {
  if (!gender || (!age && age !== 0)) {
    return 3.5
  }
  if (age < 15 || age >= 65) {
    return gender === 'female' ? 9 : 8
  }
  return gender === 'female' ? 3 : 4
}

function createMat(maxX, maxY) {
  return range(maxX).map(() => range(maxY).map(() => ([])))
}

/**
 * 【暂时不需要了，人群计算换成染色法，但是以后疫情的时候有用】
 * 将坐标分到格子中加速计算
 * @param positions 即刻position片段
 * @param size
 */
export function getCellsMap({ positions, size=[1000, 1000] }) {
  const [maxX, maxY] = size
  const cells = createMat(maxX, maxY)
  Object.entries(positions).forEach(([id, position]) => {
    const [x, y] = position
    const [cellX, cellY] = [x, y].map(a => Math.floor(a))
    if (cellX < 0 || cellX >= maxX || cellY < 0 || cellY >= maxY) {
      console.warn('position out of cells range: ', id, position, 'max ', size)
      return
    }
    cells[cellX][cellY].push({ id, position })
  })
  return cells
}

function getPointsNear(position, influenceRange) {
  const points = []
  const [pX, pY] = position
  const [pCellX, pCellY] = position.map(a => Math.floor(a))
  range(pCellX - influenceRange, pCellX + influenceRange + 1 + 1).forEach(
    x => range(pCellY - influenceRange, pCellY + influenceRange + 1 + 1).forEach(y => {
      if (getDistance([x, y], [pX, pY]) <= influenceRange) {
        points.push([x, y])
      }
    })
  )
  return points
}

function getCellInfluenceMap({ positions, size=[1000, 1000], influenceRange = 1 }) {
  const [maxX, maxY] = size
  const [maxCellX, maxCellY] = size.map(Math.floor)
  const cells = createMat(maxCellX, maxCellY)
  Object.entries(positions).forEach(([id, position]) => {
    const [x, y] = position
    const person = { id, position, x, y }
    getPointsNear(position, influenceRange).forEach(([cX, cY]) => {
      if (cX < 0 || cX >= maxX || cY < 0 || cY >= maxY) {
        return
      }
      cells[cX][cY].push(person)
    })
  })
  return cells
}

/**
 * 计算
 * @param positions 某一时刻的position片段
 * @param size 着色顶点的总大小
 * @param acc 细粒度，即为着色定点的间隔，默认为1m (精度问题以后再说)
 * @param influenceRange 单个个体的影响半径
 */
export function calcCrowdMap({
                               positions,
                               info,
                               size=[1000, 1000],
                               // acc=1,
                               influenceRange=4,
}) {
  // const [maxX, maxY] = size
  // const [maxCellX, maxCellY] = size.map(a => Math.floor(a / acc))
  return getCellInfluenceMap({positions, size, influenceRange})
    .map((arrX, x) => arrX.map((people, y) =>
      people.map(p => {
        const {id} = p
        const {gender, age} = info[id]
        return getCrowdRiskDegree({gender, age})
      }).reduce((a, b) => a + b, 0)
    ))
}

function positions2DisplayHeatmapData({positions, info}) {
  return Object.entries(positions).filter(([id])=>{
    return !!info[id];
  }).map(([id, [x, y]]) => {
    const {gender, age} = info[id]
    const value = getCrowdRiskDegree({gender, age})
    return [x, y, value]
  })
}

export function createCrowdDisplayMap({size=[1000, 1000]}={}) {
  const [x, y] = size
  const canvas = document.createElement('canvas')
  canvas.width = x
  canvas.height = y
  const heat = simpleheat(canvas)
  heat.data([]).max(7).radius(8, 8)
  const minOpacity = 0.05

  const update = ({ positions, info }) => {
    const data = positions2DisplayHeatmapData({ positions, info })
    heat.clear()
    heat.data(data)
    heat.draw(minOpacity);
  }

  return { update, canvas }
}

export function calcCrowdGraphData({positions, info, accFunc=getCrowdRiskDegree, areas=AirportRegion} = {}) {
  const peopleInArea = {}
  Object.keys(areas).forEach(key => peopleInArea[key] = [])
  Object.entries(positions).forEach(([pId, position]) => {
    Object.entries(areas).forEach(([aId, polygon]) => {
      // debugger
      if (classifyPoint(polygon, position) <= 0) {
        peopleInArea[aId].push(pId)
      }
    })
  })
  const areaNames = []
  const values = []
  Object.entries(peopleInArea).forEach(([areaName, arr]) => {
    const val = arr.map(id => accFunc(info[id])).reduce((a, b) => a + b, 0)
    areaNames.push(areaName)
    values.push(val)
  })
  return { areaNames, values }
}

