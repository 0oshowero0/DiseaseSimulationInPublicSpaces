async function getTotalDataWithLimit({ queries, limit = 9999999999, skip = 0 }) {
  let total = 0;
  const data = [];
  for (const query of queries) {
    const count = query.count();
    total += count;
    if (total <= skip) {
      return
    }
    const overSkip = total - skip;
    const querySkip = Math.max(0, count - overSkip);
    const queryLimit = Math.min(Math.max(skip + limit - (total - count), 0), limit)
    if (count && (queryLimit)) {
      data.push(...await query.skip(querySkip).limit(queryLimit).toArray())
    }
  }
  return data;
}

exports.getTotalDataWithLimit = getTotalDataWithLimit
