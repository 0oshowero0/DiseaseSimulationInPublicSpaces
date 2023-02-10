import React, {useState} from 'react';
import {Switch} from "antd";
import { CloseOutlined, CheckOutlined } from '@ant-design/icons';

import styles from "./style.module.scss";

function MapSettingsPanel({ className, onChange, instance }) {
  const MySwitch = (props) => (
    <Switch
      checkedChildren={<CheckOutlined />}
      unCheckedChildren={<CloseOutlined />}
      {...props}
    />
  )

  const [options, setOptions] = useState({
    showCheckin: true,
    showDeparture: true,
    showRest: true,
    showSeat: true,
    showSecurityCheck: true,
    showShop: true,
    // showCrowd: true,
  })

  const genOnChange = (item) => (val) => {
    setOptions(opt => {
      const newOpt = ({ ...opt, [item]: val })
      if (onChange) {
        onChange(options)
      }
      if (instance) {
          if(Array.isArray(instance)){
              for(let ins of instance){
                  if( ins.current){
                      const map = ins.current
                      map.updateOptions(newOpt)
                  }
              }
          }else{
              if( instance.current){
                  const map = instance.current
                  map.updateOptions(newOpt)
              }
          }
      }
      return newOpt
    })
  }


  return (
    <div className={`${styles.mapSettingsPanelContainer} ${className}`}>
      <div className={styles.panelTitle}>地图设置</div>
      <div className={styles.switchGroup}>
        <Switch checked={options.showCheckin} onChange={genOnChange('showCheckin')} /> &nbsp; 显示值机口
      </div>
      <div className={styles.switchGroup}>
        <Switch checked={options.showDeparture} onChange={genOnChange('showDeparture')} /> &nbsp; 显示登机口
      </div>
      <div className={styles.switchGroup}>
        <Switch checked={options.showRest} onChange={genOnChange('showRest')} /> &nbsp; 显示休息区域
      </div>
      <div className={styles.switchGroup}>
        <Switch checked={options.showSecurityCheck} onChange={genOnChange('showSecurityCheck')} /> &nbsp; 显示安检区域
      </div>
      <div className={styles.switchGroup}>
        <Switch checked={options.showShop} onChange={genOnChange('showShop')} /> &nbsp; 显示商铺
      </div>
      <div className={styles.switchGroup}>
        <Switch checked={options.showSeat} onChange={genOnChange('showSeat')} /> &nbsp; 显示座位
      </div>
      {/*<div className={styles.switchGroup}>*/}
      {/*  <Switch checked={options.showCrowd} onChange={genOnChange('showCrowd')} /> &nbsp; 显示地区拥挤情况*/}
      {/*</div>*/}
    </div>
  )
}

export default MapSettingsPanel;
