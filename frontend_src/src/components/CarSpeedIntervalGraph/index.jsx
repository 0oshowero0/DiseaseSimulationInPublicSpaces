import React from 'react';
import ReactEcharts from "echarts-for-react";
import _ from 'lodash';
import api from "../../api";
import {MAP_COLLECTION} from "../../consts";
import {addDate} from "../../utils/date";

const SHOW_DATA_RANGE = 30 * 60 * 1000  // 30min
const REFRESH_INTERVAL = 30 * 1000  // 30s
const GRAPH_TYPE_NAME = "CarSpeedIntervalGraph"

class CarSpeedIntervalGraph extends React.Component {

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
    data = data.map(obj => obj.data.speedCount)
    this.setState({ data, serials })
  }

  componentDidMount() {
    // const { timeController } = this.props
    this.update().then();
    setInterval(() => this.update(), REFRESH_INTERVAL)
  }

  getOption(data, serials) {
    data = _.zip(...data)
    return {
      title: {
        text: '车速情况统计',
        // subtext: '虚构数据',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {  // 坐标轴指示器
          type: 'shadow'
        }
      },
      legend: {
        top: 'bottom'
      },
      grid: {
        top: '10%',
        width: '90%',
        bottom: '10%',
        left: 10,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        // data: data.map((_, i) => !i ? '当前' : `-${i * 5}min`),
        data: serials.map(d => `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`),
        axisLabel: {
          interval: 0,
          rotate: 45,
        },
      },
      yAxis: {
        type: 'value'
      },
      series: data.map((d, i) => ({
        name: `${i * 10}-${(i + 1) * 10}`,
        type: 'bar',
        stack: '总量',
        barWidth: 20,
        // label: {
        //   show: true,
        //   // position: 'insideRight'
        // },
        data: d
      })),
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

export default CarSpeedIntervalGraph
