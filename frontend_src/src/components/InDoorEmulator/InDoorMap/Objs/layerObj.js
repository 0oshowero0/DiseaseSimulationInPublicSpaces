import {Container, Shape, Bitmap} from "@createjs/easeljs";
import AreaObj from "./areaObj";
import HumanObj from "./humanObj";
import {randomColorAround} from "../../../../utils/random";
import {createCrowdDisplayMap} from "../../../../emulator/crowd";

export class LayerObj extends Container {}

export class BaseAreaLayerObj extends LayerObj {
  areas = []
  /**
   *
   * @param data Array<Array<[Number, Number]>>
   */
  constructor({data}) {
    super();
    this.areas = data.map(arr => new AreaObj({shape: arr}))
    this.addChild(...this.areas)
  }
}

export class StaticAreaLayerObj extends LayerObj {
  areas = {}
  /**
   *
   * @param data Dict<String, Array<[Number, Number]>>
   * @param color String
   */
  constructor({data, color}) {
    super();
    Object.entries(data).forEach(
      ([name, arr]) => this.areas[name] = new AreaObj({shape: arr, fillColor: color})
    )
    this.addChild(...Object.values(this.areas))
  }
}

const getPersonStateWithPriority = (pInfo) => {
  let now = 'normal'
  let skip = false
  const priority = ['infecting', 'exposing', 'exposed']
  priority.forEach(key => {
    if (!skip && pInfo[key]) {
      now = key
      skip = true
    }
  })
  return now
}

const randomNewColor = state => {
  const baseColorArgs = {
    infecting: [[0xff, 0x63, 0x63], 30],
    exposing: [[0xff, 0xf2, 0x86], 30],
    exposed: [[0xcd, 0x90, 0xf8], 30],
    normal: [[0x2b, 0x7e, 0xfc], 100],
  }
  // "#ff6363"
  // "#fff286"
  // "#cd90f8"
  // "#2b7efc"
  return randomColorAround(...baseColorArgs[state])
}

export class HumanLayerObj extends LayerObj {
  humanObjs = {}
  selected = []
  onSelected = () => {}
  handleSelect(id, color) {
    this.selected = [id]
    if (this.onSelect) {
      this.onSelect(id, color)
    }
  }
  setData({data, onSelect, info={}}) {
    if (onSelect) {
      this.onSelect = onSelect
    }
    const newHumanObjs = {}
    Object.entries(data).forEach(([id, position]) => {
      if(!info[id]){
        console.log(info[id])
        return;
      }
      const selected = this.selected.includes(id)
      const infectedState = getPersonStateWithPriority(info[id])
      const old = this.humanObjs[id]
      const color = (old && old.info.get('infectedState') === infectedState) ?
        old.info.get('color') : randomNewColor(infectedState)
      const hash = { id, selected, infectedState, color }
      let humanObj = id in this.humanObjs
      && this.humanObjs[id].info.compare(hash)
        ? this.humanObjs[id] : new HumanObj({
          id,
          onClick: (id, s, obj) => this.handleSelect(id, obj.color),
          color,
          alpha: selected ? 1 : 0.8,
          size: selected ? 6 : 2,
          info: hash,
        })
      humanObj.x = position[0]
      humanObj.y = position[1]
      newHumanObjs[id] = humanObj
    })
    this.humanObjs = newHumanObjs
    this.removeAllChildren()
    this.addChild(...Object.values(newHumanObjs))
  }
}

export class CrowdHeatmapLayerObj extends LayerObj {
  canvas = null
  updateHeatmap = null
  bitmapObj = null

  constructor() {
    super();
    const { canvas, update } = createCrowdDisplayMap()
    this.canvas = canvas
    this.updateHeatmap = update
    this.bitmapObj = new Bitmap(canvas)
    this.addChild(this.bitmapObj)
  }

  setData({positions, info}) {
    this.updateHeatmap({positions, info})
  }
}

export class PathLayerObj extends LayerObj {
  line = null
  setData({data, color="#ff7c7c"}) {
    this.removeAllChildren()
    this.line = new Shape()
    const g = this.line.graphics
    if (data.length > 1) {
      const [first, ...last] = data
      g.setStrokeStyle(1).beginStroke(color).moveTo(first[0], first[1]);
      last.forEach(point => g.lineTo(point[0], point[1]))
      this.addChild(this.line)
    }
  }
}
