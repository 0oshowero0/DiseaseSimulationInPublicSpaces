import {Shape, Container, Text} from "@createjs/easeljs";

class AreaObj extends Container {
  polygon = new Shape()
  text = new Text()

  constructor({
                shape,
                borderColor='',
                fillColor='#b5b5b5',
                text='',
                textColor='#aaa',
                textFont='normal 36px Arial',
              }) {
    super();
    if (borderColor) {
      this.polygon.graphics.beginStroke(borderColor);
    }
    if (fillColor) {
      this.polygon.graphics.beginFill(fillColor);
    }
    if (shape.length < 3) {
      console.warn('shape point under 3:', shape)
    }
    const [first, ...last] = shape
    this.polygon.graphics.moveTo(first[0], first[1])
    last.forEach(point => this.polygon.graphics.lineTo(point[0], point[1]))
    this.polygon.graphics.closePath()
    this.addChild(this.polygon)
    if (text) {
      const average = arr => arr.reduce((a, b) => a + b) / arr.length
      const center = [average(shape.map(point => point[0])), average(shape.map(point => point[1]))]
      this.text = new Text(text, textFont, textColor)
      this.text.x = center[0]
      this.text.y = center[1]
      this.addChild(this.text)
    }
  }
}

export default AreaObj;
