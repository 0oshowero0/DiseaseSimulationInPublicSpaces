import React from 'react';
import ReactEcharts from "echarts-for-react";
import api from "../../api";
import {MAP_COLLECTION} from "../../consts";
import {addDate} from "../../utils/date";

const SHOW_DATA_RANGE = 5 * 60 * 1000  // 5min
const REFRESH_INTERVAL = 30 * 1000  // 30s
const GRAPH_TYPE_NAME = "TrafficIndexGraph"

class TrafficIndexGraph extends React.Component {
  state = {
    // data: [9.9, 6.1, 6, 3.9, 4.2, 3.7],
    data: [],
    serials: [],
  }

  async update() {
    const { timeController } = this.props

    let data = await api.loadCharts({
      type: GRAPH_TYPE_NAME,
      collection: MAP_COLLECTION,
      startTime: addDate(timeController.getNowDate(), -SHOW_DATA_RANGE),
      endTime: timeController.getNowDate(),
    })
    data = data.sort((a, b) => a.start - b.start)
    const serials = data.map(obj => obj.start)
    data = data.map(obj => obj.data.trafficIndex)
    this.setState({ data, serials })
  }

  componentDidMount() {
    // const { timeController } = this.props
    this.update().then();
    setInterval(() => this.update(), REFRESH_INTERVAL)
  }

  getOption(data, serials) {
    // data: [9.9, 6.1, 6, 3.9, 4.2, 3.7]
    return {
      title: {
        text: '交通指数变化',
        // subtext: '虚构数据',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'line'
        }
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        axisLabel: {
          interval: 0,
          rotate: 45,
        },
        // data: data.map((_, i, d) => d.length === i + 1 ? '当前' : `-${d.length - i - 1}min`)
        data: serials.map(d => `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`),
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        data,
        type: 'line',
        areaStyle: {}
      }]
    };
  }

  render() {
    const { data, serials } = this.state;
    return (
      <ReactEcharts
        option={this.getOption(data, serials)}
        style={{height: '100%', width: '100%'}}
        className='echarts-for-echarts'
        theme='chalk' />
    )
  }
}

export default TrafficIndexGraph
