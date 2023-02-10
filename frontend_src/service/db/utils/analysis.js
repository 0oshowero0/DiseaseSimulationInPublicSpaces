exports.getStartEndRange = (data) => {
  const start = data.length ? (
    data
      .map(obj => obj.start)
      .reduce((acc, val) => acc > val ? acc : val)
  ) : 0;
  const end = data.length ? (
    data
      .map(obj => obj.end)
      .reduce((acc, val) => acc < val ? acc : val)
  ) : 0;
  return [start, end];
}
