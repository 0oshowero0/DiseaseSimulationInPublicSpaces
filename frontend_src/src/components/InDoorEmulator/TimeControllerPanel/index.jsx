import React, { useState, useEffect } from 'react';
import {Slider, TimePicker} from "antd";
import moment from 'moment';
import styles from "./style.module.scss";


function TimeControllerPanel({ className, startTime, endTime, instance, onTick=(ts) => {} }) {
  const [time, setTime] = useState(0)
  const [speed, setSpeed] = useState(1)
  // const step = 1000
  const step = 10
  const interval = 100
  useEffect(() => {
    const handler = setInterval(() => {
      if(Array.isArray(instance)){
        for(let ins of instance){
          if (ins.current) {
            const floor = ins.current
            floor.updateTime(time)
          }
        }
      }else{
        if (instance.current) {
          const floor = instance.current
          floor.updateTime(time)
        }
      }
      if (onTick) {
        onTick({time})
      }
      setTime(t => {
        const val = t + interval / 1000 * speed
        if (val < startTime) {
          return startTime
        }
        return val > endTime ? startTime : val
      })
    }, interval)
    return () => {
      clearInterval(handler)
    }
  })
  return (
    <div className={`${styles.timeControllerPanelContainer} ${className}`}>
      <div className={styles.middleAbs}>
        <div className={styles.floatUp}>
          {/*<TimePicker*/}
          {/*  showNow={false}*/}
          {/*  allowClear={false}*/}
          {/*  defautValue={moment("Thu, 01 Jan 1970 00:00:00 GMT")}*/}
          {/*  value={moment(new Date(time).toUTCString())}*/}
          {/*  onChange={time => { setTime((time.hour() * 60 + time.minute()) * 60 + time.second())}}*/}
          {/*/>*/}
        </div>
      </div>
      <div className={styles.startComment}>开始</div>
      <div className={styles.middleSlider}>
        <Slider
          defaultValue={0}
          min={startTime}
          // max={24 * 60 * 60}
          max={endTime}
          dots={true}
          // tooltipVisible={false}
          step={step}
          tipFormatter={val => (<div>{new Date(val * 1000).toLocaleString()}</div>)}
          value={time}
          onChange={setTime}
        />
      </div>
      <div className={styles.endComment}>结束</div>
    </div>
  )
}

export default TimeControllerPanel;
