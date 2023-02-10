import React from 'react';
import styles from "./style.module.scss";
import NCovGraph from "../NCovGraph";
import CrowdGraph from "../CrowdGraph";

function GraphPanel({ className, mode, graphData, time }) {
  return (
    <div className={`${styles.nCovPanelContainer} ${className}`}>
      { mode === 'plague' && (
        <>
          <div className={styles.panelTitle}>疫情模拟</div>
          <NCovGraph
            start={graphData && graphData.start}
            end={graphData && graphData.end}
            info={graphData && graphData.info}
            infoCmp={graphData && graphData.infoCmp}
          />
        </>
      )}
      { mode === 'crowd' && (
        <>
          <div className={styles.panelTitle}>拥塞统计</div>
          <CrowdGraph
            info={graphData && graphData.info}
            infoCmp={graphData && graphData.infoCmp}
            positions={graphData && graphData.positions}
            positionsCmp={graphData && graphData.positionsCmp}
            time={time}
          />
        </>
      )}
    </div>
  )
}

export default GraphPanel;
