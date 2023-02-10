const { MongoClient } = require('mongodb')

const uri = process.env.NODEJS_MONGO_DB_URI ?? "mongodb://admin:qwer1234@localhost:27017";
const DB_NAME = process.env.NODEJS_MONGO_DB_NAME ?? 'fiblab'
const client = new MongoClient(uri, {useUnifiedTopology: true});

let waitingList = [];
client.connect().then(() => {
    waitingList.forEach(r => r(client.db(DB_NAME)))
    waitingList = []
});

function getDb() {
    return new Promise(resolve => {
        if(client.isConnected()) {
            resolve(client.db(DB_NAME));
        } else {
            waitingList.push(resolve);
        }
    })
}

async function getCollection(name) {
    const db = await getDb();
    return db.collection(name);
}

// exports = {
//     client,
//     getDb,
//     getCollection,
// }

exports.client = client;
exports.getDb = getDb;
exports.getCollection = getCollection;

if (require.main === module) {

}
