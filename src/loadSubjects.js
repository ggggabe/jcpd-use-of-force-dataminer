require('dotenv').config()
const { createClient } = require('./mongo')
const { C2L: C2LWrapper, L2C: L2CWrapper } = require('./cleanCharges')

  ; (async () => {
    console.info('creating db client')
    const db = (await createClient(process.env.MONGO_URL)).db(process.env.MONGO_DB)
    console.info('connecting to db...')

    await db.collection(process.env.SUBJECTS_COLLECTION).remove({})

    console.info('getting JCPD Collection')
    const jcpdDocs = await db.collection(process.env.JCPD_COLLECTION).find({}).toArray()
    const subjects = []

    const C2L = C2LWrapper.unwrap
    const L2C = L2CWrapper.unwrap
    console.info('formatting subjects')
    jcpdDocs.forEach(doc => {
      subjects.push(...doc.subjects.map((s, i) => ({
        ...s,
        subjectId: [doc.id, i].join('-'),
        incidentId: doc.id,
        charges: (s.charges || []).reduce(
          ({ legaleze, codes, undocumented }, uncleanCharge) => {
            const charge = uncleanCharge.toLowerCase()
            const legalVal = L2C[charge] ? charge : ([...(C2L[charge] || [])][0] || false)
            const codeVal = C2L[charge] ? charge : ([...(L2C[charge] || [])][0] || false)
            const undocumentedVal = !C2L[charge] && !L2C[charge]

            return {
              legaleze: legalVal ? [...legaleze, legalVal] : legaleze,
              codes: codeVal ? [...codes, codeVal] : codes,
              undocumented: undocumentedVal ? [...undocumented, charge] : undocumented,
            }
          },
          { legaleze: [], codes: [], undocumented: [] }
        ) || []
      })))
    })

    const result = await db.collection(process.env.SUBJECTS_COLLECTION).insertMany(subjects)

    console.log('done')
    return
  })()
