import React from 'react';
import ReactEcharts from "echarts-for-react";
import {calcInfectedGraphData} from "../../../emulator/plague";
import {range} from "../../../utils/range";

class NCovGraph extends React.Component {

  state = {
    times: null,
    numData: null,
    expectData: null,
    numDataCmp: null,
    expectDataCmp: null,
  }

  calcStepAndInterval(start, end) {
    const STEP = 20
    const interval = (end - start) / STEP
    return { interval, step: STEP }
  }

  geneTimes(start, interval, count) {
    return range(count).map(i => {
      const ts = start + interval * i
      return (new Date(ts * 1000)).toLocaleString()
    })
  }

  getOption(
    times,
    exposedData,
    infectedData,
    exposedDataCmp=null,
    infectedDataCmp=null) {
    const LINE_WIDTH = 3
    const series = [
      {
        name: '感染人数',
        type: 'line',
        yAxisIndex: 0,
        smooth: true,
        lineStyle: {
          width: LINE_WIDTH
        },
        symbolSize: LINE_WIDTH,
        symbol: 'circle',
        data: infectedDataCmp || infectedData,
      },
      {
        name: '暴露人数',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        lineStyle: {
          width: LINE_WIDTH
        },
        symbol: 'circle',
        symbolSize: LINE_WIDTH,
        data: exposedDataCmp || exposedData,
      },
    ]
    if (infectedDataCmp) {
      series.push({
        name: '感染人数',
        type: 'line',
        yAxisIndex: 0,
        smooth: true,
        lineStyle: {
          type:'dotted',
          width: LINE_WIDTH
        },
        symbolSize: LINE_WIDTH,
        symbol: 'circle',
        data: infectedData,
      })
    }
    if (exposedDataCmp) {
      series.push({
        name: '暴露人数',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        lineStyle: {
          type:'dotted',
          width: LINE_WIDTH
        },
        symbol: 'circle',
        symbolSize: LINE_WIDTH,
        data: exposedData,
      })
    }

    return {
      title: {
        show: false
      },
      grid: {
        left: '-15%',
        right: '-15%',
        top: '5%',
        bottom: '5%',
        containLabel: true
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['暴露人数', '感染人数'],
        top: 'bottom'
      },
      xAxis: {
        type: 'category',
        show: false,
        boundaryGap: false,
        // data: ['0:01:00', '0:02:00', '0:03:00', '0:04:00', '0:05:00', '0:06:00', '0:07:00']
        data: times
      },
      yAxis: [
        {
          type: 'value',
          show: false,
          axisLabel: {
            formatter: '{value} 人'
          }
        },
        {
          type: 'value',
          show: false,
          axisLabel: {
            formatter: '{value} 人'
          }
        }
      ],
      series
    };
  }

  render() {
    let times, exposedData, infectedData, exposedDataCmp, infectedDataCmp
    const {info, infoCmp, start, end} = this.props

    if (start !== undefined && end !== undefined) {
      const { interval, step } = this.calcStepAndInterval(start, end)
      times = this.geneTimes(start, interval, step)
      if (info) {
        const val = calcInfectedGraphData(info, start, end, interval)
        exposedData = val.exposedCount
        infectedData = val.infectedCount
      }
      if (infoCmp) {
        const val = calcInfectedGraphData(infoCmp, start, end, interval)
        exposedDataCmp = val.exposedCount
        infectedDataCmp = val.infectedCount
      }
    }

    return (
      <ReactEcharts
        option={this.getOption(times, exposedData, infectedData, exposedDataCmp, infectedDataCmp)}
        style={{height: '100%', width: '100%'}}
        className='echarts-for-echarts'
      />
    )
  }
}

export default NCovGraph
