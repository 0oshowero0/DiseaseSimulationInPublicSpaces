import React, {Fragment, useEffect, useRef} from "react";
import TimeController from "../../components/TimeController";
import CarRouteMap from "../../components/CarRouteMap";
import RoadSpeedMap from "../../components/RoadSpeedMap";

import styles from "./style.module.scss";
import CarSpeedIntervalGraph from "../../components/CarSpeedIntervalGraph";
import TrafficIndexGraph from "../../components/TrafficIndexGraph";
import CongestionRationxGraph from "../../components/CongestionRationxGraph";
import CongestedRoadList from "../../components/CongestedRoadList";
import Clock from "../../components/Clock";

function MainTrafficPage() {
  const timeControllerRef = useRef();
  const roadSpeedMapRef = useRef();

  useEffect(() => {
    const timeController = timeControllerRef.current;
    if(timeController) {
      console.log("play", timeController)
      timeController.play()
    }
  })

  return (
    <div className={styles.trafficPageContainer}>
      <TimeController ref={timeControllerRef}>
        {
          timeController => (
            <>
              <div className={styles.leftGraph}>
                <div className={styles.roadSpeedMap}>
                  <RoadSpeedMap ref={roadSpeedMapRef} timeController={timeController} />
                </div>
                <div className={styles.carSpeedIntervalGraph}>
                  <CarSpeedIntervalGraph timeController={timeController} />
                </div>
              </div>
              <div className={styles.mainMapWrapper}>
                <Clock className={styles.clock} />
                <CarRouteMap
                  timeController={timeController}
                  onMoved={({lng, lat}) => {
                    if (roadSpeedMapRef.current && roadSpeedMapRef.current.map) {
                      const map = roadSpeedMapRef.current.map;
                      map.jumpTo({center: [lng, lat]});
                    }
                  }}
                />
              </div>
              <div className={styles.rightGraph}>
                <div className={styles.trafficIndexGraph}>
                  <TrafficIndexGraph timeController={timeController} />
                </div>
                <div className={styles.congestionRationxGraph}>
                  <CongestionRationxGraph timeController={timeController} />
                </div>
                <div className={styles.trafficIndexGraph}>
                  <CongestedRoadList timeController={timeController} />
                </div>
              </div>
            </>
          )
        }
      </TimeController>
    </div>
  );
}

export default MainTrafficPage;
