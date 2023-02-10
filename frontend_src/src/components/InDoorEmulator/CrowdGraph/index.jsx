import React from 'react';
import ReactEcharts from "echarts-for-react";
import {calcInfectedGraphData} from "../../../emulator/plague";
import {range} from "../../../utils/range";
import {calcCrowdGraphData} from "../../../emulator/crowd";
import {getPositionMapFromAllPosition} from "../InDoorMap/Preprocess/people";

class CrowdGraph extends React.Component {

  geneAreas(count) {
    return range(count).map(i => `区域${i}`)
  }

  getOption({ areas, riskData, riskDataCmp=null }) {
    const series = []
    if (riskData) {
      series.push({
        name: '区域风险',
        type: 'bar',
        yAxisIndex: 0,
        smooth: true,
        data: riskData,
      })
    }
    if (riskDataCmp) {
      series.push({
        name: '区域风险(对比)',
        type: 'bar',
        yAxisIndex: 0,
        smooth: true,
        data: riskDataCmp,
      })
    }

    return {
      title: {
        show: false
      },
      grid: {
        left: '0%',
        right: '5%',
        top: '8%',
        bottom: '18%',
        containLabel: true
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        // data: ['区域人数', '区域风险'],
        data: ['区域风险'],
        top: 'bottom'
      },
      xAxis: {
        type: 'category',
        // show: false,
        // boundaryGap: false,
        // data: ['区域一', '区域二',]
        data: areas
      },
      yAxis: [
        {
          type: 'value',
          // show: false,
          axisLabel: {
            formatter: '{value}'
          }
        },
      ],
      series
    };
  }

  render() {
    const {info, infoCmp, positions, positionsCmp, time} = this.props


    let areas, riskData, riskDataCmp
    if (time && info && positions) {
      const nowPosition = getPositionMapFromAllPosition(positions, time)
      const result = calcCrowdGraphData({positions: nowPosition, info})
      areas = result.areaNames
      riskData = result.values
    }

    if (time && infoCmp && positionsCmp) {
      const nowPosition = getPositionMapFromAllPosition(positionsCmp, time)
      const result = calcCrowdGraphData({
        positions: nowPosition,
        info: infoCmp,
      })
      riskDataCmp = result.values
    }

    return (
      <ReactEcharts
        option={this.getOption({areas, riskData, riskDataCmp})}
        style={{height: '100%', width: '100%'}}
        className='echarts-for-echarts'
      />
    )
  }
}

export default CrowdGraph
