const { url, db, clientPromise, unwrap } = require('./mongo')
const test = require('assert')


//:::: ENV ::::
const tests = {
  env: () => {
    test.ok(typeof url === 'string')
    test.ok(url.length)

    test.ok(typeof db === 'string')
    test.ok(db.length)
  },
  async: async () => {
    const client = unwrap(await clientPromise)

    test.ok(client)
    client.close()
  }
}

tests.env()
tests.async()
