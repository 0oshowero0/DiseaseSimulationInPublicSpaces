export function evalJSONObjectWithShit(txt) {
  try {
    if(typeof txt==='object') return txt;
    // eslint-disable-next-line no-new-func
    return (new Function('return '+txt))();
  }catch (e) {
    console.warn('eval parse wrong with:', txt, ' err:', e)
    return {};
  }
}

export function dealDictWithShit(txt) {
  let mapper = evalJSONObjectWithShit(txt);
  let result = {};
  for(let k in mapper){
    if(mapper.hasOwnProperty(k)){
      let tmp = evalJSONObjectWithShit(mapper[k]);
      result[tmp.state['passenger_ID2']] = tmp;
    }
  }
  return result
}
