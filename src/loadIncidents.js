require('dotenv').config()
const { createClient } = require('./mongo')

const incidents = process.env.INCIDENTS_DB

; (async () => {
  const db = (await createClient(process.env.MONGO_URL)).db(process.env.MONGO_DB)

  await db.collection(process.env.INCIDENTS_COLLECTION).remove({})
  const jcpdDocs = await db.collection(process.env.JCPD_COLLECTION).find({}).toArray()

  const incidents = jcpdDocs.map( d => ({
    pageLength: d.pages.length,
    pageStart: d.pages[0] || null,
    incidentId: d.id,
    location: d.location || 'N/A',
    zip: d.zip,
    signature: {
      ...d.signatures[0]
    },
    officers: d.officers
  }))

  console.log(`incidents: ${incidents.length}`)
  const result = await db.collection(process.env.INCIDENTS_COLLECTION).insertMany(incidents)
  console.log('done')

})()
