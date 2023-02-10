import React from 'react';
import {MAP_END_TIME, MAP_START_TIME} from "../../consts";

export const TIME_STATUS = Object.freeze({
  NOT_START: Symbol("not start"),
  RUNNING: Symbol("running"),
  STOPPED: Symbol("stopped"),
});

export const TimeContext = React.createContext({
  now: 0,
  status: TIME_STATUS.NOT_START,
  startTime: MAP_START_TIME,
  endTime: MAP_END_TIME,
  controller: null,
});

// 全局统一时间控制器
export class TimeController extends React.Component {

  onTickCallbacks = []
  lastTickTime = 0

  props = {
    startTime: Date,
  }

  state = {
    status: TIME_STATUS.NOT_START,
    now: MAP_START_TIME.getTime(),
    startTime: MAP_START_TIME,
    endTime: MAP_END_TIME,
  }

  componentDidMount() {

  }

  register(onTick) {
    this.onTickCallbacks.push(onTick)
  }

  play() {
    if (this.state.status === TIME_STATUS.RUNNING) return
    this.setState({status: TIME_STATUS.RUNNING})
    this.lastTickTime = 0
    requestAnimationFrame(t => this.onTick(t))
  }

  pause() {
    this.setState({status: TIME_STATUS.STOPPED})
    this.lastTickTime = 0
  }

  stop() {
    this.setState(state => ({
      status: TIME_STATUS.NOT_START,
      now: state.startTime,
    }))
    this.lastTickTime = 0
  }

  onTick(timestamp) {
    // console.log("onTick", timestamp)
    if (this.state.status !== TIME_STATUS.RUNNING) return
    const {now, status, startTime, endTime} = this.state;
    const {onTick} = this.props;
    const deltaTime = this.lastTickTime ? timestamp - this.lastTickTime : 0;
    this.lastTickTime = timestamp;
    this.setState(({now}) => ({now: now + deltaTime}))
    this.onTickCallbacks.forEach(
      t => t({
        timestamp, deltaTime, now, status,
        startTime, endTime, controller: this,
      })
    )
    requestAnimationFrame(t => this.onTick(t))
  }

  getStartTime() {
    return this.state.startTime
  }

  getEndTime() {
    return this.state.startTime
  }

  getNow() {
    return this.state.now
  }

  getNowDate() {
    return new Date(this.state.now)
  }

  render() {
    const {children} = this.props;
    const {now, status, startTime, endTime} = this.state;
    return (
      <TimeContext.Provider
        value={{now, status, startTime, endTime, controller: this}}
      >
        {children(this)}
      </TimeContext.Provider>
    )
  }
}

export default TimeController;
