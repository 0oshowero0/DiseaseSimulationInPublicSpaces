import {Shape, Container} from "@createjs/easeljs";
import {Stateful} from "../../../../utils/stateful";
import {randomColor} from "../../../../utils/random";

export default class HumanObj extends Container {
  shape = new Shape()
  info = new Stateful()

  constructor({
    id = '',
    color= '',
    alpha = 0.8,
    size = 2,
    onClick = null,
    info = {},
              }) {
    super();
    if (!color) {
      color = randomColor()
    }
    this.color = color
    this.alpha = alpha
    this.shape.graphics.setStrokeStyle(0.8).beginStroke('black');
    this.shape.graphics.beginFill(color);
    this.shape.graphics.drawCircle(0,0, size);
    this.addChild(this.shape)
    this.addEventListener("mousedown", (e) => onClick && onClick(id, this.info, this, e))

    this.info.set(info)
  }
}
