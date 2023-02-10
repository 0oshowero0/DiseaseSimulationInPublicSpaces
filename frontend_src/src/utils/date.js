/**
 *
 * @param date {number,Date} 毫秒数/日期
 * @param delta {number,Date} 毫秒数/日期
 * @returns {Date}
 */
export function addDate(date, delta) {
    delta = (new Date(delta)).getTime()
    date = (new Date(date)).getTime()
    return new Date(date + delta)
}
