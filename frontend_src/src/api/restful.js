import axios from 'axios'
import {evalJSONObjectWithShit} from "../utils/ployfill";

export function loadPeopleData(options, onProcess) {
  return axios.get('http://127.0.0.1:2000/individual_traces', {
    params: options,
    timeout: 1000 * 60 * 10,
    onDownloadProgress: progressEvent => {
      let percentCompleted = Math.floor(progressEvent.loaded / progressEvent.total * 100)
      console.log('completed: ', percentCompleted)
      if (onProcess) {
        onProcess(percentCompleted, progressEvent.loaded, progressEvent.total)
      }
    }
  })
}

export function loadRiskData(options, onProcess) {
  return new Promise((resolve, reject) => {
    axios.get('http://127.0.0.1:2000/risk_evaluation', {
      params: options,
      timeout: 1000 * 60 * 10,
      onDownloadProgress: progressEvent => {
        let percentCompleted = Math.floor(progressEvent.loaded / progressEvent.total * 100)
        console.log('completed: ', percentCompleted)
        if (onProcess) {
          onProcess(percentCompleted, progressEvent.loaded, progressEvent.total)
        }
      }
    }).then(function (res) {
      let mapper = evalJSONObjectWithShit(res.data);
      let result = {};
      for(let k in mapper){
        if(mapper.hasOwnProperty(k)){
          let tmp;
          if(typeof mapper[k]==='string'){
            tmp = evalJSONObjectWithShit(mapper[k]);
          }else if(typeof mapper[k]==='object'){
            tmp = mapper[k];
          }else{
            continue;
          }
          result[tmp.state['passenger_ID2']] = tmp;
        }
      }
      resolve({data:result})
    });
  });
}
