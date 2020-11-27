require('dotenv').config()
const { createClient } = require('./mongo')
const CHARGE_MAPS = require('./cleanCharges')

const url = process.env.MONGO_URL

  ; (async () => {
    const [dbname, collection, targetJson] = process.argv.slice(2)

    console.log(targetJson)
    const uploadTarget = Object.values(require(targetJson)).map(incident => ({
      ...incident,
      officers: Object.values(incident.officers),
      subjects: Object.values(incident.subjects).map(subject => {
        const { charges } = subject

        const legaleze = []
        const codes = []

        charges.forEach(charge => {
          legaleze.push(
            L2C[charge] ? charge : (C2L[charge] || `Undocumented Charge: [${charge}]`)
          )

          codes.push(
            C2L[charge] ? charge : (L2C[charge] || `Undocumented Charge: [${charge}]`)
          )
        })

        console.log({
          charges,
          code,
          legaleze
        })

        return {
          ...subject,
          charges: {
            legaleze,
            codes
          }
        }

      })
    }))

    const db = (await createClient(url).then((d) => d, data => {
      console.log(data)
      return {
        db: () => {
          console.log('could not connect')
        }
      }
    })).db(dbname)

    let page = 0

    const pageSize = 10
    const removeResult = await db.collection(collection).remove({})

    const result = await db.collection(collection).insertMany(uploadTarget)

    console.log('done')
    return

    /*
    const len = uploadTarget.length
  
  
    for (page; page < len; page += pageSize) {
      const payload = uploadTarget.slice(page, page + pageSize < len ? page + pageSize : undefined)
      const result = await db.collection(collection).insertMany(payload)
    }
  
    console.log('done')
    return
    */

  })()
