import React from 'react';
import styles from "./style.module.scss";
import {Button, Switch} from "antd";
import {CheckOutlined, CloseOutlined, WarningOutlined} from "@ant-design/icons";

const parseDate = ts => new Date(ts * 1000).toLocaleString()

function DetailsPanel({ className, info, id, onInfectedChange }) {
  return (
    <div className={`${styles.detailsPanelContainer} ${className}`}>
      <div className={styles.panelTitle}>详细信息</div>
      {
        !info ? (
          <div className={styles.none}>
            暂无选中项
          </div>
        ) : (<div className={styles.people}>
          <p>序号: &nbsp;{info.ID}</p>
          {/*<p>客票号: &nbsp;{info.passenger_ID2}</p>*/}
          <p>航班号: &nbsp;{info.flight_ID}</p>
          <p>登机口: &nbsp;{info.BGATE_ID}</p>
          {/*<p>最大速度: &nbsp;{info.max_speed}</p>*/}
          <p>检票时间: &nbsp;{parseDate(info.checkin_time)}</p>
          <p>起飞时间: &nbsp;{parseDate(info.flight_time)}</p>
          <p>出现时间: &nbsp;{parseDate(info.start_time)}</p>

          <br />
          {/*<p>{JSON.stringify(info)}</p>*/}
          <p>性别: &nbsp;{+info.gender === 0 ? '男' : '女'}</p>
          <p>年龄: &nbsp;{info.age || 0}</p>
            <p>暴露: &nbsp;<span
                className={`${styles.spanTag} ${info.exposing ? styles.tagDanger : (info.exposed ? styles.tagWarning : styles.tagSafe)}`}
                >{info.exposing ? '暴露中' : (info.exposed ? '有暴露史' : '无')}</span>
            </p>
            <p>感染: &nbsp;<span
                className={`${styles.spanTag} ${info.infecting ? styles.tagDanger : styles.tagSafe}`}
            >{info.infecting ? '已感染' : '无'}</span></p>
          {/*<Button>追踪行程</Button>*/}
        </div>)
      }
    </div>
  )
}

export default DetailsPanel;
