import React from 'react';
import moment from 'moment';
import {
    Button,
    Collapse,
    DatePicker,
    Form,
    Input,
    Modal,
    notification,
    Progress,
    Radio,
    Select,
    Slider,
    Row,
    Col,
    Switch,
    Divider
} from "antd";
import { SelectOutlined } from '@ant-design/icons';

import styles from "./style.module.scss";
import {loadPeopleData, loadRiskData} from "../../../api/restful";
import {getDictMul, getFiledName} from "../../../utils/dictMap";

const { RangePicker } = DatePicker;
const { Panel } = Collapse;

const optionsToParams = (values) => {
  const parseMoment = momentTime => Math.round(momentTime.valueOf() / 1000)
  const {time, trace_control, risk_control, trace_control_cmp, risk_control_cmp, ...rest} = values
  return {
    ...rest,
    trace_control: trace_control && JSON.stringify(trace_control),
    risk_control: risk_control && JSON.stringify(risk_control),
    trace_control_cmp: trace_control_cmp && JSON.stringify(trace_control_cmp),
    risk_control_cmp: risk_control_cmp && JSON.stringify(risk_control_cmp),
    begin_time: parseMoment(time[0]),
    end_time: parseMoment(time[1]),
  }
}

const finishForm = async ({basicForm, traceForm, riskForm, onCollapseChange}) => {
  let basicValue, traceValue, riskValue
  try {
    basicValue = await basicForm.validateFields()
  } catch (e) {
    onCollapseChange('basic')
    throw e
  }
  try {
    traceValue = await traceForm.validateFields()
  } catch (e) {
    onCollapseChange('trace')
    throw e
  }
  try {
    riskValue = await riskForm.validateFields()
  } catch (e) {
    onCollapseChange('risk')
    throw e
  }
  return {...basicValue, ...traceValue, ...riskValue}
}

const DISPLAY_COLUMN = ['time','trace_control','risk_choice','risk_control'];
const COMPARE_COLUMN = ['method','trace_control','risk_control'];

const showRows = (data, isMultiple) => {
    let dom = [];
    for (let col of DISPLAY_COLUMN) {
        if (data[col]) {
            let emptyStr = '未填写' + getFiledName(col);
            let isSame = data[col][0] === data[col][1];
            dom.push(<Row>
                <Col span={4}>
                    <span className={styles.floatInfosItem}>{getFiledName(col)}</span>
                </Col>
                <Col span={(isMultiple && !isSame) ? 10 : 20}>
                    <span className={styles.floatInfosItem}>{getDictMul(data[col][0]) || emptyStr}</span>
                </Col>
                {(isMultiple && !isSame) && ( <>
                <Col span={10}>
                    <span className={styles.floatInfosItem}>{getDictMul(data[col][1]) || emptyStr}</span>
                </Col>
                </>)}
            </Row>);
        }
    }
    return dom;
};

const ScenarioSetting = ({
                           activeKey,
                           onCollapseChange,
                           basicForm,
                           traceForm,
                           riskForm,
                           isMultiple,
}) => {
  const [lastPanel, setLastPanel] = React.useState(activeKey || 'basic')
  const handleCollapseChange = (val) => {
    console.log('Collapse change: ', val)
    let form = null
    switch (lastPanel) {
      case 'basic':
        form = basicForm
        break;
      case 'trace':
        form = traceForm
        break;
      case 'risk':
        form = riskForm
        break;
      default:
        onCollapseChange(val)
        return
    }
    if (form) {
      form.validateFields().then(() => {
        setLastPanel(val)
        onCollapseChange(val)
      })
    }
  };

  return (
    <Collapse
      accordion
      activeKey={activeKey}
      onChange={handleCollapseChange}
    >
      <Panel header="数据补全" key="basic">
        <Form
          form={basicForm}
          layout="vertical"
          name="load_modal"
          initialValues={{
            scenario: 'airport',
            time: [
              moment('2016-09-12T08:00:00'),
              moment('2016-09-12T12:00:00')
            ],
            period: 1,
          }}
        >
          <Form.Item
            name="scenario"
            label="场景"
            rules={[
              {
                required: true,
                message: '必须输入加载的场景名',
              },
            ]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="time"
            label="加载区间"
            rules={[
              {
                type: 'array',
                required: true,
                message: '必须指定时间区间',
              },
            ]}
          >
            <RangePicker showTime />
          </Form.Item>
          {/*<Form.Item*/}
          {/*  name="period"*/}
          {/*  label="间隔(秒)"*/}
          {/*>*/}
          {/*  <Slider*/}
          {/*    min={1}*/}
          {/*    max={1000}*/}
          {/*  />*/}
          {/*</Form.Item>*/}
        </Form>
      </Panel>
      <Panel header="个体轨迹生成" key="trace">
        <Form
          form={traceForm}
          layout="vertical"
          name="load_modal"
          initialValues={{
            method: 'social_force',
            trace_control: [],
            method_cmp: 'social_force',
            trace_control_cmp: [],
          }}
        >
          <Row gutter={16}>
            <Col span={isMultiple ? 12 : 24}>
              <Form.Item
                  name="method"
                  label="轨迹生成算法"
                  rules={[
                    {
                      required: true,
                      message: '必须选择轨迹生成算法',
                    },
                  ]}
              >
                <Radio.Group
                    optionType="button"
                    buttonStyle="solid"
                >
                  <Radio.Button value="social_force">Social Force</Radio.Button>
                  {/*<Radio.Button value="GAN">GAN</Radio.Button>*/}
                </Radio.Group>
              </Form.Item>
              <Form.Item
                  name="trace_control"
                  label="移动管控"
              >
                <Select mode="multiple">
                  <Select.Option value="social_distancing">增大社交距离</Select.Option>
                  <Select.Option value="more_security_ck">增加安检口</Select.Option>
                  <Select.Option value="speed_up">增加移动速度（步行梯）</Select.Option>
                  <Select.Option value="reduce_explore">减少探索行为（关闭店铺、增加指示牌）</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            {isMultiple ? (<Col span={12}>
              <Form.Item
                  name="method_cmp"
                  label="轨迹生成算法"
                  rules={[
                    {
                      required: true,
                      message: '必须选择轨迹生成算法',
                    },
                  ]}
              >
                <Radio.Group
                    optionType="button"
                    buttonStyle="solid"
                >
                  <Radio.Button value="social_force">Social Force</Radio.Button>
                  {/*<Radio.Button value="GAN">GAN</Radio.Button>*/}
                </Radio.Group>
              </Form.Item>
              <Form.Item
                  name="trace_control_cmp"
                  label="移动管控"
              >
                <Select mode="multiple">
                  <Select.Option value="social_distancing">增大社交距离</Select.Option>
                  <Select.Option value="more_security_ck">增加安检口</Select.Option>
                  <Select.Option value="speed_up">增加移动速度（步行梯）</Select.Option>
                  <Select.Option value="reduce_explore">减少探索行为（关闭店铺、增加指示牌）</Select.Option>
                </Select>
              </Form.Item>
            </Col>) : ''}
          </Row>
        </Form>
      </Panel>
      <Panel header="风险评估" key="risk">
        <Form
          form={riskForm}
          layout="vertical"
          name="load_modal"
          initialValues={{
            risk_choice: 'none',
            risk_control: [],
            risk_control_cmp: [],
          }}
        >
          <Form.Item
              name="risk_choice"
              label="风险选择"
          >
            <Select>
              <Select.Option value="none">无</Select.Option>
              <Select.Option value="crowd">拥挤踩踏</Select.Option>
              <Select.Option value="plague">新冠疫情</Select.Option>
            </Select>
          </Form.Item>
          <Row gutter={16}>
            <Col span={isMultiple ? 12 : 24}>
              {
                <Form.Item
                    name="risk_control"
                    label="传染风险管控"
                >
                  <Select mode="multiple">
                    <Select.Option value="mask_on">佩戴口罩</Select.Option>
                    <Select.Option value="more_susceptible">增加易感人口比例</Select.Option>
                    <Select.Option value="more_disinfection">提高消毒频率</Select.Option>
                  </Select>
                </Form.Item>
              }
            </Col>
            {isMultiple?(<Col span={12}>
              {
                <Form.Item
                    name="risk_control_cmp"
                    label="传染风险管控"
                >
                  <Select mode="multiple">
                    <Select.Option value="mask_on">佩戴口罩</Select.Option>
                    <Select.Option value="more_susceptible">增加易感人口比例</Select.Option>
                    <Select.Option value="more_disinfection">提高消毒频率</Select.Option>
                  </Select>
                </Form.Item>
              }
            </Col>):''}
          </Row>
        </Form>
      </Panel>
    </Collapse>
  )
}

const LoadMenu = ({ visible, onLoad, onCancel, onComplete, isMultiple }) => {
  const [confirmLoading, setConfirmLoading] = React.useState(false);
  const [process, setProcess] = React.useState(-1);
  const [processText, setProcessText] = React.useState('');
  const [showPanel, setShowPanel] = React.useState('basic')
  const [basicForm] = Form.useForm()
  const [traceForm] = Form.useForm()
  const [riskForm] = Form.useForm()

  return (
    <Modal
      visible={visible}
      title="加载新数据"
      okText="加载"
      cancelText="取消"
      confirmLoading={confirmLoading}
      onCancel={onCancel}
      onOk={async () => {
        try {
          const values = await finishForm({
            basicForm, traceForm, riskForm,
            onCollapseChange: setShowPanel,
            isMultiple
          })
          const params = optionsToParams(values)
          setProcess(0)
          setProcessText('')
          console.log('loading values', values)
          console.log('loading setting', params)
          setConfirmLoading(true)
          let result;
            if (params.risk_choice === 'plague') {
                params.risk = 'epidemic';
                result = await loadRiskData(params,
                    (percent, current, total) => {
                        let per = isMultiple?(percent/2):percent;
                        setProcess(per)
                        setProcessText(`${current} / ${total}`)
                    })
            } else {
                result = await loadPeopleData(params,
                    (percent, current, total) => {
                        let per = isMultiple?(percent/2):percent;
                        setProcess(per)
                        setProcessText(`${current} / ${total}`)
                    })
            }
          console.log('load result:', result)
          if(!isMultiple)setConfirmLoading(false)
          setProcess(isMultiple?50:100)
          if (onLoad) {
            onLoad(result.data, values,false);
          }
          values.risk_choice_cmp = values.risk_choice;
          let paramInfos = {};
          for(let col of DISPLAY_COLUMN){
            paramInfos[col] = [ values[col] ];
          }
            if (values.time) {
                let timeStr = values.time[0].format('YYYY-MM-DD HH:mm:ss') + ' ~ ' + values.time[1].format('YYYY-MM-DD HH:mm:ss');
                paramInfos.time = [timeStr, timeStr];
            }
            // 这个其实有巨大问题 都什么玩意 得重构
          if(isMultiple){
              let tmpParam = {...params};
              for(let col of COMPARE_COLUMN){
                tmpParam[col] = tmpParam[col+'_cmp'];
              }
              for(let col of DISPLAY_COLUMN){
                paramInfos[col].push(values[col+'_cmp']);
              }
              let result2;
              if (params.risk_choice === 'plague') {
                  result2 = await loadRiskData(tmpParam,
                      (percent, current, total) => {
                          setProcess(percent+50)
                          setProcessText(`${current} / ${total}`)
                      })
              } else {
                  result2 = await loadPeopleData(tmpParam,
                      (percent, current, total) => {
                          setProcess(percent+50)
                          setProcessText(`${current} / ${total}`)
                      })
              }
              console.log('load result2:', result2)
              setConfirmLoading(false)
              setProcess(100)
              if (onLoad) {
                  onLoad(result2.data, values,true);
              }

          }
          if(onComplete){
            onComplete(paramInfos);
          }
        } catch (info) {
          setConfirmLoading(false)
          console.log('Validate Failed:', info);
          notification.error({
            message: '加载失败',
            description: `${info}`,
          })
        }
      }}
    >
      <ScenarioSetting
        activeKey={showPanel}
        onCollapseChange={setShowPanel}
        basicForm={basicForm}
        traceForm={traceForm}
        riskForm={riskForm}
        isMultiple={isMultiple}
      />
      { process >= 0 && <Progress percent={process} /> }
      <p>{processText}</p>
    </Modal>
  );
};

function FunctionalPanel({ className, onLoad, onSwitchView, onExport, canExport=true }) {
  const [loadMenuVisible, setLoadMenuVisible] = React.useState(false);
  const [isForCompare,setIsForCompare]=React.useState(false);
  const [compareInfo,setCompareInfo]=React.useState({});

  return (
    <div className={`${styles.functionalPanelContainer} ${className}`}>
      <Button
        className={styles.button}
        type="primary"
        onClick={() => {
          setIsForCompare(false);
          setLoadMenuVisible(true);
          if(onSwitchView){
            onSwitchView(false);
          }
        }}
      >
        加载单个
      </Button>
      <Button
        className={styles.button}
        type="primary"
        onClick={() => {
          setIsForCompare(true);
          setLoadMenuVisible(true);
          if(onSwitchView){
            onSwitchView(true);
          }
        }}
      >
        加载对比
      </Button>
      <Button
        className={styles.button}
        icon={<SelectOutlined />}
        onClick={() => {
          onExport()
        }}
        disabled={!canExport}
      >
        导出
      </Button>
      <LoadMenu
        visible={loadMenuVisible}
        isMultiple={isForCompare}
        onLoad={(data, options,isCompare) => {
          if(!isForCompare)setLoadMenuVisible(false)
          if (onLoad) {
            onLoad(data, options, isCompare)
          }
        }}
        onComplete={(compare) => {
          if(isForCompare)setLoadMenuVisible(false)
          console.log('onComplete',compare)
          setCompareInfo(compare);
        }}
        onCancel={() => setLoadMenuVisible(false)}
      />
      <div className={styles.floatInfos}>
        {showRows(compareInfo,isForCompare)}
      </div>
    </div>
  )
}

export default FunctionalPanel;
