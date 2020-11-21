const { MongoClient } = require('mongodb')

const unwrap = wrapper => wrapper.ok ? wrapper.value : null

const createClient = async (url, options = { useUnifiedTopology: true }) => {
  const clientPromise = new Promise((resolve, reject) => {
    MongoClient.connect(url, options, function (err, client) {
      if (err) return reject(err)
      return resolve(client)
    })
  }).then(client => ({
    ok: true,
    value: client
  }), err => ({
    ok: false,
    message: err
  }))

  return unwrap(await clientPromise)
}


module.exports = {
  ...module.exports,
  createClient,
  unwrap
}