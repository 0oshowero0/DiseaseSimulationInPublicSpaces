import React from "react";

import {TimeContext} from "../TimeController";
import styles from "./style.module.scss";

function Clock({ className }) {
  return (
    <TimeContext>
      {({now}) => (
        <div className={`${styles.clockContainer} ${className}`}>
          { (new Date(now)).toLocaleString() }
        </div>
      )}
    </TimeContext>
  )
}

export default Clock
