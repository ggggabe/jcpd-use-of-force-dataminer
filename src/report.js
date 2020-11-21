require('dotenv').config()
const fs = require('fs')
const { createClient } = require('./mongo')

; (async () => {
  const db = (await createClient(process.env.MONGO_URL)).db(process.env.MONGO_DB)

  const subjects = await db.collection(process.env.SUBJECTS_COLLECTION)
  const incidentsCollection = await db.collection(process.env.INCIDENTS_COLLECTION)

  const noCharges = await subjects.find({ charges: { $size: 0 }}).toArray()


  const incidentsNoCharges = new Set()
  noCharges.forEach( ({ incidentId }) => {
    incidentsNoCharges.add(incidentId)
  })

  console.log(`Subjects without charges: ${noCharges.length}`)
  console.log(`Total amount of subjects: ${await subjects.countDocuments({})}`)
  console.log(`Number of Incidents where all subjects have no charges: ${incidentsNoCharges.size}`)
  console.log(`Total Number of Incidents: ${await db.collection(process.env.INCIDENTS_COLLECTION).countDocuments({})}`)
  console.log(`Incidents with redacted addresses: ${ await incidentsCollection.countDocuments({ $or: [
    { location: {$regex: /^JERSEY CITY, NJ \d{5}(?:[-\s]\d{4})?$/}},
  ]
  })}`)

  console.log(`Cops with most incidents in data/worst.csv`)

  /*
  const csvContent = [
    'name, badge, sex, race, age, rank, duty, service_years, incidents, incidentCount',
    ...(await db.collection(process.env.OFFICERS_COLLECTION).find().sort({
      incidentsCount: -1
    }).limit(10).toArray()).map( ({
      name,
      badge,
      sex,
      race,
      age,
      rank,
      duty,
      service_years,
      incidents,
      incidentsCount
    }) => [
      name,
      badge,
      sex,
      race,
      age,
      rank,
      duty,
      service_years,
      '"' + incidents.join(', ') + '"',
      incidentsCount
    ].join(', '))
  ]
  */
  const csvContent = [
    'incident, address',
    ... await Promise.all(
      [...((await db.collection(process.env.OFFICERS_COLLECTION).find().sort({
        incidentsCount: -1
      }).limit(10).toArray()).reduce( (acc, {incidents}) => {
        incidents.forEach(i => acc.add(i))
        return acc
      }, new Set()))].map(async incidentId => [
        incidentId,
        `"${(await db.collection(process.env.INCIDENTS_COLLECTION).findOne({ incidentId })).location}"`
      ].join(', '))
    ),
  ]

  /*
  await fs.writeFile(
    '../data/incidentAddresses.csv',
    csvContent.join('\n'),
    process.exit
  )
  */

  /*
  await fs.writeFile('../data/worst.csv', csvContent.join('\n'), () => {
  process.exit()
  })
  */

})()
