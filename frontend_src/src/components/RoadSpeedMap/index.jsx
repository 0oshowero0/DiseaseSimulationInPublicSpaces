import React from 'react';
import ReactMapboxGl, {Layer, GeoJSONLayer} from 'react-mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

import api from "../../api";
import {MAP_CENTER, MAP_COLLECTION} from "../../consts";
import {addDate} from "../../utils/date";

import styles from './style.module.scss';
import {BUILDINGS_PAINT} from "../../utils/mapbox-paint";
// import {coordObj2arr} from "../../serializers/coord";

const center = MAP_CENTER

const Map = ReactMapboxGl({
  accessToken: process.env.REACT_APP_MAPBOX_API_KEY,
  dragRotate: false,
  pitchWithRotate: false,
  interactive: false,  // 禁止该图所有交互
});

const transRoadArray2Dict = arr => arr.reduce((val, a) => {
  a.speed = 40;
  val[a.key] = a;
  return val
}, {})

const genGeoJsonFromRoad = roads => ({
  "type": "FeatureCollection",
  "features": Object.values(roads).map(road => ({
    "type": "Feature",
    "properties": {
      "key": road.key,
      "name": road.name,
      "level": road.level,
      "speed": road.speed,
    },
    // "geometry": {
    //   "type": "LineString",
    //   "coordinates": road.shape.map(coordObj2arr)
    // },
    "geometry": road.shape,
  }))
})

const isRoadSpeedShowing = (now) => (road) =>
  road.start <= new Date(now) && new Date(now) < road.end

const ROAD_DATA_LIMIT = 300000
const ROAD_LOAD_TIME_SPAN = 10 * 60 * 1000  // 10min

const ROAD_PAINT = {
  "line-width": 1,
  'line-color': [
    "interpolate",
    ["linear"],
    ["get", "speed"],
    0, "#210000",
    5, "#5b0202",
    10, "#ee0202",
    20, "#eec702",
    40, "#55ee02",
    120, "#c7ffa8",
  ],
};

class RoadSpeedMap extends React.Component {
  // static propTypes = {
  //     timeController: TimeController
  // };

  hasInit = false

  state = {
    center,
    roads: {},
    startTime: null,
    endTime: null,
  }

  updateLock = false
  lastTickTime = null
  map = null

  constructor(props) {
    super(props);
    const {timeController} = props;
    this.state.lastLoadTime = timeController.getStartTime();
  }

  componentDidMount() {
    const {timeController} = this.props;
    this._loadAllRoadData().then(() => {
      timeController.register(params => this.onTick(params))
      this._loadInitData(timeController.getStartTime());
    })
  }

  async _loadAllRoadData() {
    const data = await api.loadRoads({
      level: 1,
      collection: MAP_COLLECTION,
    })
    console.log("load road data: ", data)
    this.setState({roads: transRoadArray2Dict(data)})
  }

  updateSpeed(data) {
    const roads = { ...this.state.roads };
    data.forEach(road => {
      roads[road.key].speed = road.speed;
    })
    this.setState({roads})
  }

  async _loadInitData(time) {
    this.updateLock = true
    time = new Date(time)
    const startTime = time;
    const endTime = addDate(time, ROAD_LOAD_TIME_SPAN);
    const data = await api.loadRoadSpeeds({
      startTime, endTime,
      collection: MAP_COLLECTION,
      limit: ROAD_DATA_LIMIT,
    })
    console.log(`load road speed init data (${time}):`, data)
    this.setState({ startTime, endTime })
    this.updateSpeed(data.filter(isRoadSpeedShowing(time)))
    this.updateLock = false
  }

  async _loadUpdatedData(time) {
    time = new Date(time)
    if (this.updateLock) {
      // console.debug("meet update lock:", lng, lat, time)
      return
    }
    this.updateLock = true
    const startTime = time;
    const endTime = addDate(time, ROAD_LOAD_TIME_SPAN);
    const data = await api.loadRoadSpeeds({
      startTime, endTime,
      collection: MAP_COLLECTION,
      limit: ROAD_DATA_LIMIT,
    })
    console.log(`update road speed data (${time}):`, data)

    this.updateLock = false
    this.setState({ startTime, endTime })
    this.updateSpeed(data.filter(isRoadSpeedShowing(time)))
  }

  // timestamp是从0开始算的，基础单位为ms，小数点后还有3位
  onTick({now}) {
    const {startTime, endTime} = this.state
    if (!this.updateLock && (now < startTime.getTime() || now > endTime.getTime())) {
      // debugger
      this._loadUpdatedData(new Date(now)).then()
    }
    // 在有bearing的时候，在requestAnimationFrame使用setState会导致地图无法操作，可能和setState的异步属性有关
  }

  render() {
    const {roads} = this.state;
    const geoJson = genGeoJsonFromRoad(roads);
    return (
      <div className={styles.mapWrapper}>
        <Map
          // eslint-disable-next-line
          style="mapbox://styles/mapbox/dark-v10"
          // style="mapbox://styles/mapbox/streets-v9"
          containerStyle={{
            height: '100%',
            width: '100%'
          }}
          center={center}
          pitch={[30]}
          // bearing={[-17.6]}
          dragRotate={false}
          pitchWithRotate={false}
          // antialias={true}
          onStyleLoad={map => {
            this.map = map;
          }}
        >
          <GeoJSONLayer
            // id="roadStatus"
            linePaint={ROAD_PAINT}
            data={geoJson}
          />
          <Layer
            id="3d-buildings"
            type="fill-extrusion"
            sourceId="composite"
            sourceLayer="building"
            filter={['==', 'extrude', 'true']}
            paint={BUILDINGS_PAINT}
          />
        </Map>
      </div>
    );
  }
}

export default RoadSpeedMap;
