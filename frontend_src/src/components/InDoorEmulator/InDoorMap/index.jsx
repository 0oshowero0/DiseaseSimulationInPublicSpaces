import React from 'react';
import { Stage, Touch, Ticker } from "@createjs/easeljs";

import styles from "./style.module.scss";
import FloorObj from "./Objs/floorObj";
import PerspectiveController from "./Controllers/PerspectiveController";

class InDoorMap extends React.Component {

  canvasRef = React.createRef()
  stage = null
  floor = null
  info = {}
  halfScreen = false

  state = {
    canvasWidth: 1920,
    canvasHeight: 1080,
  }

  constructor({ onSelect, className, info, halfScreen, ...rest }) {
    super(rest);
    this.info = info
    this.halfScreen = halfScreen
    console.log('halfScreen',halfScreen)
  }

  componentDidMount() {
    console.log(this.halfScreen)
    this.setState({
      canvasWidth: this.halfScreen? window.innerWidth/2:window.innerWidth,
      canvasHeight: window.innerHeight,
    })
    setImmediate(() => {
      const canvasDom = this.canvasRef.current
      this.stage = new Stage(canvasDom)
      Touch.enable(this.stage)
      // Enabled mouse over / out events
      this.stage.enableMouseOver(10);
      this.stage.mouseMoveOutside = true;
      const { onSelect, positions, info } = this.props
      this.floor = new FloorObj({
        onSelect: id => onSelect && onSelect(id),
        allPosition: positions, info
      })
      const controller = new PerspectiveController({gameObject: this.floor})
      this.stage.addChild(controller)
      this.stage.update()
      Ticker.addEventListener('tick', (e) => this.stage.update(e))
    })
  }

  updatePositions(positions){
    if (this.floor) {
      this.floor.updatePositions(positions)
    }
  }

  updateTime(time){
    if (this.floor) {
      this.floor.updateTime(time)
    }
  }

  updateOptions(options){
    if (this.floor) {
      this.floor.updateOptions(options)
    }
  }

  updateInfo(info){
    if (this.floor) {
      this.floor.updateInfo(info)
    }
  }

  render() {
    const { className } = this.props
    const { canvasWidth, canvasHeight } = this.state

    return (
      <div className={`${styles.inDoorMapContainer} ${className}`}>
        <canvas className={styles.canvas} width={canvasWidth} height={canvasHeight} ref={this.canvasRef} />
      </div>
    )
  }
}

export default InDoorMap;
