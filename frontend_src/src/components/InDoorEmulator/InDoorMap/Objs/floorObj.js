import {Container} from "@createjs/easeljs";
import {BaseAreaLayerObj, CrowdHeatmapLayerObj, HumanLayerObj, PathLayerObj, StaticAreaLayerObj} from "./layerObj";
import {loadAirportFloorFromJson} from "../Preprocess/airport-floor";
import {loadRectAreaFromJson} from "../Preprocess/rect-area";
import airportJson from "../../../../assets/in-doors/airport/maps/airport_map_255_processed.json";
import checkinJson from "../../../../assets/in-doors/airport/labels/checkin.json";
import departureJson from "../../../../assets/in-doors/airport/labels/departure.json";
import restJson from "../../../../assets/in-doors/airport/labels/rest.json";
import seatJson from "../../../../assets/in-doors/airport/labels/seat.json";
import securityCheckJson from "../../../../assets/in-doors/airport/labels/security_ck.json";
import shopJson from "../../../../assets/in-doors/airport/labels/shop.json";
import peopleJson from "../../../../assets/in-doors/airport/people/people-example.json";
import {getPositionMapFromAllPosition, loadPeopleDataFromJson} from "../Preprocess/people";
import {updateInfectedStateInfo} from "../../../../emulator/plague";


class FloorObj extends Container {
  baseLayer = new BaseAreaLayerObj({data: [loadAirportFloorFromJson(airportJson)]})

  checkinLayer = new StaticAreaLayerObj({data: loadRectAreaFromJson(checkinJson), color:'#9e70ea'})
  departureLayer = new StaticAreaLayerObj({data: loadRectAreaFromJson(departureJson), color:'#a0d754'})
  restLayer = new StaticAreaLayerObj({data: loadRectAreaFromJson(restJson), color:'#d7b154'})
  seatLayer = new StaticAreaLayerObj({data: loadRectAreaFromJson(seatJson), color:'#54c8d7'})
  securityCheckLayer = new StaticAreaLayerObj({data: loadRectAreaFromJson(securityCheckJson), color:'#d75454'})
  shopLayer = new StaticAreaLayerObj({data: loadRectAreaFromJson(shopJson), color:'#d78d54'})
  // wifiLayer = new StaticAreaLayerObj({data: loadRectAreaFromJson(checkinJson)})

  peopleLayer = new HumanLayerObj()
  selectPathLayer = new PathLayerObj()
  crowdedHeatmapLayer = new CrowdHeatmapLayerObj()

  positions = {}
  info = {}
  time = 0

  constructor({ allPosition, initTime, onSelect, info }={}) {
    super();

    if (allPosition) {
      this.updatePositions(allPosition)
    }

    if (initTime) {
      this.updateTime(initTime)
    }

    if (info) {
      this.updateInfo(info)
    }

    this.peopleLayer.onSelect = (id, color) => {
      this.selectPathLayer.setData({
        data: this.positions[id].data, color
      })
      if (onSelect) {
        onSelect(id)
      }
    }

    this.addChild(
      this.baseLayer,

      this.departureLayer,
      this.restLayer,
      this.seatLayer,
      this.securityCheckLayer,
      this.shopLayer,
      this.checkinLayer,
      // this.wifiLayer,

      this.crowdedHeatmapLayer,
      this.selectPathLayer,
      this.peopleLayer
    )
  }

  refresh() {
    const positions = getPositionMapFromAllPosition(this.positions, this.time)
    if (this.peopleLayer.visible) {
      updateInfectedStateInfo(this.info, this.time)
      this.peopleLayer.setData({data: positions, info: this.info})
    }
    if (this.crowdedHeatmapLayer.visible) {
      this.crowdedHeatmapLayer.setData({positions, info: this.info})
    }
  }

  updateTime(time) {
    this.time = time
    this.refresh()
  }

  updatePositions(allPosition) {
    this.positions = allPosition
    this.refresh()
  }

  updateInfo(info) {
    this.info = info
    this.refresh()
  }

  setOptions({
                  showCheckin=true,
                  showDeparture=true,
                  showRest=true,
                  showSeat=true,
                  showSecurityCheck=true,
                  showShop=true,
                  showCrowd=true,
                }) {
    this.checkinLayer.visible = showCheckin
    this.departureLayer.visible = showDeparture
    this.restLayer.visible = showRest
    this.seatLayer.visible = showSeat
    this.securityCheckLayer.visible = showSecurityCheck
    this.shopLayer.visible = showShop
    this.crowdedHeatmapLayer.visible = showCrowd

    this.refresh()
  }

  updateOptions({
                  showCheckin,
                  showDeparture,
                  showRest,
                  showSeat,
                  showSecurityCheck,
                  showShop,
                  showCrowd,
                }) {
    const changeVisible = (obj, val) => {
      if (val !== undefined) {
        obj.visible = val
      }
    }
    changeVisible(this.checkinLayer, showCheckin)
    changeVisible(this.departureLayer, showDeparture)
    changeVisible(this.restLayer, showRest)
    changeVisible(this.seatLayer, showSeat)
    changeVisible(this.securityCheckLayer, showSecurityCheck)
    changeVisible(this.shopLayer, showShop)
    changeVisible(this.crowdedHeatmapLayer, showCrowd)

    this.refresh()
  }
}

export default FloorObj;
