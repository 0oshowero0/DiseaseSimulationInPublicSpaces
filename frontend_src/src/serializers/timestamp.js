// import proto from 'google-protobuf'

export const tsObj2date = obj => new Date(obj.seconds * 1000 + obj.nanos / 1000000);
/**
 *
 * @param date {Date}
 * @returns {Timestamp | proto.google.protobuf.Timestamp}
 */
export const date2ts = date => {
    const ts = new window.proto.google.protobuf.Timestamp()
    ts.fromDate(date)
    return ts
}
