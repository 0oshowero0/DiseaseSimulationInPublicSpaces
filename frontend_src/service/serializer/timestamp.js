exports.tsObj2date = obj => new Date(obj.seconds * 1000 + obj.nanos / 1000000);
exports.date2tsObj = date => ({
    seconds: Math.floor(date.getTime() / 1000),
    nanos: date.getTime() % 1000 * 1000000,
});
