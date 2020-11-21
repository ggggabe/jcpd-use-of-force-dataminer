require('dotenv').config()
const { createClient } = require('./mongo')

const subjects = process.env.SUBJECTS_COLLECTION

; (async () => {
  const db = (await createClient(process.env.MONGO_URL)).db(process.env.MONGO_DB)

  await db.collection(process.env.SUBJECTS_COLLECTION).remove({})

  const jcpdDocs = await db.collection(process.env.JCPD_COLLECTION).find({}).toArray()
  const subjects = []

  jcpdDocs.forEach( doc => {
    subjects.push(...doc.subjects.map((s, i) => ({
      ...s,
      subjectId: [doc.id, i].join('-'),
      incidentId: doc.id,
      charges: s.charges || []
    })))
  })

  const result = await db.collection(process.env.SUBJECTS_COLLECTION).insertMany(subjects)

  console.log('done')
})()
