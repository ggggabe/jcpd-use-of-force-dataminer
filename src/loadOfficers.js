require('dotenv').config()
const { createClient } = require('./mongo')

const officers = process.env.OFFICERS_DB

; (async () => {
  const db = (await createClient(process.env.MONGO_URL)).db(process.env.MONGO_DB)

  const incidents = await db.collection(process.env.INCIDENTS_COLLECTION).find({}).toArray()

  await db.collection(process.env.OFFICERS_COLLECTION).remove({})

  const officers = incidents.reduce( (acc, {officers, incidentId}) => {
    const officersCopy = {...acc}

    officers.forEach( o => {
      const { badge } = o
      if (officersCopy[badge]) return officersCopy[badge].incidents.push(incidentId)

      officersCopy[badge] = {
        ...o,
        incidents: [incidentId],
      }
    })

    return officersCopy
  }, {})

  const officersArray = Object.values(officers).map( o => ({
    ...o,
    incidentsCount: o.incidents.length
  }))
  console.log(`officers: ${officersArray.length}`)
  const result = await db.collection(process.env.OFFICERS_COLLECTION).insertMany(officersArray)
  console.log('done')

})()
