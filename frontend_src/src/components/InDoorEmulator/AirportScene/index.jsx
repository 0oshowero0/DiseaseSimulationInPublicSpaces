import React from 'react';
import styles from "./style.module.scss";
import InDoorMap from "../InDoorMap";
import TimeControllerPanel from "../TimeControllerPanel";
import FunctionalPanel from "../FunctionalPanel";
import MapSettingsPanel from "../MapSettingsPanel";
import GraphPanel from "../GraphPanel";
import DetailsPanel from "../DetailsPanel";
import {getPositionMapFromAllPosition, loadPeopleDataFromJson} from "../InDoorMap/Preprocess/people";

// import peopleJson from "../../../assets/in-doors/airport/people/people-example.json";
import peopleJson from "../../../assets/in-doors/airport/people/people-with-control.json";
import peopleExampleJson from "../../../assets/in-doors/airport/people/people-example.json";
import peoplePlagueJson from "../../../assets/in-doors/airport/people/people-with-plague.json";
import {exportToFile} from "../../../utils/fuckingFile";
import {calcCrowdMap} from "../../../emulator/crowd";

class AirportScene extends React.Component {
  state = {
    showCompare:false,
    info: {},
    positions: {},
    options: {},
    infoCmp:{},
    positionsCmp:{},
    selected: null,
    // startTime: 0,
    // endTime: 1000,
    startTime: 1473638400,
    // endTime: 1473652800,
    endTime: 1473638400 + 10 * 60,
    graphData: null,
    // mode: 'none', // 拥挤模式：'crowd'  疫情模式：'plague'
    mode: 'none', // 拥挤模式：'crowd'  疫情模式：'plague'
    now: null,
  }

  map = React.createRef()
  mapCmp = React.createRef()

  componentDidMount() {
    this.loadFromLocal()
  }

  switchCrowdHeatmap(val) {
    if (this.map.current) {
      this.map.current.updateOptions({showCrowd: val})
    }
    if (this.mapCmp.current) {
      this.mapCmp.current.updateOptions({showCrowd: val})
    }
  }

  genPlagueGraphData({
                       start = this.state.startTime,
                       end = this.state.endTime,
                       info, infoCmp
                     }) {
    return {
      start, end, info, infoCmp
    }
  }

  genCrowdGraphData({
                       info, positions,
                       infoCmp, positionsCmp
                     }) {
    return {
      info, infoCmp, positions, positionsCmp
    }
  }

  genInitGraphData() {
    const { startTime, endTime, info, infoCmp, positions, positionsCmp, mode, showCompare } = this.state
    if (mode === 'plague') {
      let data = {start: startTime, end: endTime, info}
      if (showCompare) {
        data.infoCmp = infoCmp
      }
      const graphData = this.genPlagueGraphData(data)
      this.setState({graphData})
    }
    if (mode === 'crowd') {
      let data = { info, positions }
      if (showCompare) {
        data = { ...data, infoCmp, positionsCmp }
      }
      const graphData = this.genCrowdGraphData(data)
      this.setState({graphData})
    }
  }

  genOnTickGraphData({ time }) {
    // const { info, infoCmp, positions, positionsCmp, mode } = this.state
    // if (mode === 'crowd') {
    //   const graphData = this.genCrowdGraphData({ time, info, positions, infoCmp, positionsCmp })
    //   this.setState({graphData})
    // }
  }

  loadFromLocal() {
    const [positions, info] = loadPeopleDataFromJson(peoplePlagueJson)
    const [positionsCmp,infoCmp]=loadPeopleDataFromJson(peoplePlagueJson)

    this.setState({positions, info,positionsCmp,infoCmp})

    setImmediate(() => this.genInitGraphData())
  }

  handleOnLoadFromNet(data, options, forCompare) {
    const parseMoment = momentTime => Math.round(momentTime.valueOf() / 1000)
    const [positions, info] = loadPeopleDataFromJson(data)
    const startTime = parseMoment(options.time[0])
    const endTime = parseMoment(options.time[1])
    const mode = options.risk_choice
    console.log('forCompare',forCompare)
    this.switchCrowdHeatmap(mode === 'crowd')
    if(forCompare && this.mapCmp.current){
      this.mapCmp.current.updateInfo(info)
      this.mapCmp.current.updatePositions(positions)
    }
    if (!forCompare && this.map.current) {
      this.map.current.updateInfo(info)
      this.map.current.updatePositions(positions)
    }
    if(forCompare){
      this.setState({positionsCmp:positions, infoCmp:info, options, startTime, endTime, mode})
    }else{
      this.setState({positions, info, options, startTime, endTime, mode})
    }
    setImmediate(() => this.genInitGraphData())
  }

  handleInfectedChange(id, value) {
    const { info } = this.state
    if (info[id]) {
      info[id].infected = value
    }
    this.setState({ info })
  }

  handleSelect(id) {
    this.setState({selected: id})
  }

  exportData() {
    const { graphData, mode, positions, info, now } = this.state
    if (mode === 'none') {
      alert('普通模式无可导出项')
      return
    }
    let crowdMap
    if (mode === 'crowd') {
      const insPositions = getPositionMapFromAllPosition(positions, now)
      crowdMap = calcCrowdMap({positions: insPositions, info})
    }
    const data = { graphData, crowdMap }
    exportToFile(JSON.stringify(data), 'data.json')
  }

  render() {
    const {className} = this.props
    const {
      positions, info, infoCmp, positionsCmp,
      startTime, endTime, selected,
      showCompare, mode, graphData, now
    } = this.state
    return (
      <div className={`${styles.airportSceneContainer} ${className}`}>
        <div className={styles.panels}>
          <div className={styles.topPanel}>
            <FunctionalPanel
                className={styles.panel}
                onLoad={(...args) => this.handleOnLoadFromNet(...args)}
                onSwitchView={(state)=>{this.setState({showCompare:state})}}
                onExport={()=>this.exportData()}
                canExport={mode !== 'none'}
            />
          </div>
          <div className={styles.center}>
            <div className={styles.leftPanel}>
              <MapSettingsPanel
                className={styles.panel}
                instance={[this.map,this.mapCmp]}
              />
            </div>
            <div className={styles.rightPanel}>
              {
                 mode !== 'none' && (
                   <GraphPanel
                     className={`${styles.panel} ${styles.graphPanel}`}
                     mode={mode}
                     graphData={graphData}
                     time={now}
                   />
                 )
              }
              <DetailsPanel
                className={`${styles.panel} ${styles.detailsPanel}`}
                info={selected && info[selected]}
                id={selected}
                onInfectedChange={(id, val) => this.handleInfectedChange(id, val)}
              />
            </div>
          </div>
          <div className={styles.bottomPanel}>
            <TimeControllerPanel
              className={styles.panel}
              startTime={startTime}
              endTime={endTime}
              instance={[this.map,this.mapCmp]}
              onTick={({time}) => {
                // debugger
                this.genOnTickGraphData({time})
                this.setState({now: time})
              }}
            />
          </div>
        </div>
        <div className={styles.full}>
          <div className={showCompare ? styles.halfScreen : styles.full}>
            <InDoorMap
                ref={this.map}
                className={styles.panel}
                positions={positions}
                info={info}
                halfScreen={showCompare}
                onSelect={id => this.handleSelect(id)}
            />
          </div>
          {
            showCompare && (
              <div className={styles.halfScreen}>
                <InDoorMap
                    ref={this.mapCmp}
                    className={styles.panel}
                    positions={positionsCmp}
                    info={infoCmp}
                    halfScreen={showCompare}
                    onSelect={id => this.handleSelect(id)}
                />
              </div>
            )
          }
        </div>

      </div>
    )
  }
}

export default AirportScene;
