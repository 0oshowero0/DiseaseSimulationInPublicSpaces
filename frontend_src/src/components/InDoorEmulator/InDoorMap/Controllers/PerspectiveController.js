import {Container} from "@createjs/easeljs";

export default class PerspectiveController extends Container {
  gameObject = null

  constructor({ gameObject }) {
    super();
    this.gameObject = gameObject
    this.addChild(gameObject)
    this.addEventListener("mouseover", this);
    // this.addEventListener("mouseout", this);
    this.addEventListener("mousedown", this);
    // console.log("controller loaded")
    window.addEventListener("keydown", e => this.handleKeyPress(e));
  }
  handleKeyPress(event) {
    console.log(event.key)
    const STEP = 10;
    const SCROLL_STEP = 0.1;
    const ROTATE_STEP = 5;
    // eslint-disable-next-line default-case
    switch (event.key) {
      case 'ArrowUp':
      case 'w':
        this.y = this.y - STEP
        break;
      case 'ArrowDown':
      case 's':
        this.y = this.y + STEP
        break;
      case 'ArrowLeft':
      case 'a':
        this.x = this.x - STEP
        break;
      case 'ArrowRight':
      case 'd':
        this.x = this.x + STEP
        break;
      case '=': // +
        this.scale = this.scale + SCROLL_STEP
        break;
      case '-':
        this.scale = this.scale - SCROLL_STEP
        break;
      case 'q':
        this.rotation = this.rotation - ROTATE_STEP
        break;
      case 'e':
        this.rotation = this.rotation + ROTATE_STEP
        break;
    }
  }

  handleEvent(e) { this[e.type] && this[e.type](e) }

  mousedown(e) {
    // this.parent.addChild(this);
    const offset = {
      x: this.x - e.stageX,
      y: this.y - e.stageY
    };

    // console.log("mouse down")
    this.addEventListener("pressmove", (event) => {
      this.x = event.stageX + offset.x;
      this.y = event.stageY + offset.y;
      // console.log("mouse move")
      // updated on the next tick.
      // update = true;
    });
  }
}
