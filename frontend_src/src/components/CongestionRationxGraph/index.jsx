import React from 'react';
import ReactEcharts from "echarts-for-react";
import api from "../../api";
import {MAP_COLLECTION} from "../../consts";

const REFRESH_INTERVAL = 30 * 1000  // 30s
const GRAPH_TYPE_NAME = "CongestionRationxGraph"

class CongestionRationxGraph extends React.Component {
  state = {
    data: 0,
  }

  async update() {
    const { timeController } = this.props

    // let data = await api.loadChartsIncrement({
    //   type: GRAPH_TYPE_NAME,
    //   collection: MAP_COLLECTION,
    //   now: timeController.getNowDate(),
    // })
    const data = await api.loadCharts({
      type: GRAPH_TYPE_NAME,
      collection: MAP_COLLECTION,
      startTime: timeController.getNowDate(),
      endTime: timeController.getNowDate(),
    })
    const rate = data.length ? data[0].data.congestionRatio : 0
    this.setState({ data: rate })
  }

  componentDidMount() {
    // const { timeController } = this.props
    this.update().then();
    setInterval(() => this.update(), REFRESH_INTERVAL)
  }

  getOption(data) {
    return {
      title: {
        text: '交通拥塞比例',
        // subtext: '虚构数据',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 10,
      },
      series: [
        {
          name: '拥堵比例',
          type: 'pie',
          radius: ['50%', '70%'],
          avoidLabelOverlap: false,
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '30',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            {value: data, name: '拥堵'},
            {value: 1 - data, name: '尚可'},
          ]
        }
      ]
    };
  }
  render() {
    const { data } = this.state;
    return (
      <ReactEcharts
        option={this.getOption(data)}
        style={{height: '100%', width: '100%'}}
        className='echarts-for-echarts'
        theme='chalk' />
    )
  }
}

export default CongestionRationxGraph
