const DICT = {
    social_distancing: '增大社交距离',
    more_security_ck: '增加安检口',
    speed_up: '增加移动速度',
    reduce_explore: '减少探索行为',
    none: '无',
    crowd: '拥挤踩踏',
    plague: '新冠疫情',
    mask_on: '佩戴口罩',
    more_susceptible: '增加易感人口比例',
    more_disinfection: '提高消毒频率',
    social_force: 'Social Force算法'
};

const FIELDS = {
    time: '时间',
    method: '轨迹生成算法',
    trace_control: '移动管控',
    risk_choice: '风险选择',
    risk_control: '传染风险管控',
};

export function getDict(key) {
    return DICT[key] || key;
}

export function getDictMul(keys, split) {
    if (typeof keys === 'string') {
        if (keys[0] === '[') keys = JSON.parse(keys);
        else keys = keys.split(',');
    }
    if (!Array.isArray(keys)) return '';
    split = split || ',';
    return keys.map(x => getDict(x)).join(split)
}

export function getFiledName(field) {
    return FIELDS[field] || field;
}

