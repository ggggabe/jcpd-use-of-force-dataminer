const targetFields = [
  "signatures", "officers", "subjects", "charges"
]

const isBasicVal = (val) => {
  switch (typeof val) {
    case 'string':
      return true
    case 'number':
      return true
    default:
      return false
  }
}

const addDynamicHeaders = (headers, header, c) => {
  for (let i = 0; i < c; i++) {
    headers.push(`${header}_${i + 1}`)
  }
}

const flatten = incidents => {
  let maxOfficers = 0
  let maxSubjects = 0

  const chargesSet = new Set()
  const forceSet = new Set()
  const actionsSet = new Set()

  incidents.map(({
    pages,
    officers,
    subjects
  }) => {
    oLength = Object.values(officers).length

    if (oLength > maxOfficers) maxOfficers = oLength
    if (subjects.length > maxSubjects) maxSubjects = subjects.length

    subjects.map((subject) => {
      const {
        force_received,
        charges,
        actions
      } = subject

      force_received && force_received.forEach(val => forceSet.add(val.toLowerCase()))
      charges && charges.forEach(val => chargesSet.add(val.toLowerCase()))
      actions && actions.forEach(val => actionsSet.add(val.toLowerCase()))
    })

  })

  console.log({
    maxOfficers,
    maxSubjects,
    chargesSet,
    forceSet,
    actionsSet,
  })

  const csvHeaders = [
    'id',
    'time',
    'date',
    'day',
    'location',
    'zip',

  ]

  const signatureHeaders = [
    // Signature
    'sign_date',
    'supervisor_name',
    'supervisor_signature'
  ]

  officerHeaders = []
  addDynamicHeaders(officerHeaders, 'officer', maxOfficers)

  subjectHeaders = []
  addDynamicHeaders(subjectHeaders, 'subject', maxSubjects)

  const headers = new Set()

  const flat = incidents.map(incident => {
    const flatIncident = {}

    csvHeaders.map(header => {
      flatIncident[header] = incident[header]
      headers.add(header)
    })

    const [signature] = incident.signatures

    if (signature) {
      Object.assign(flatIncident, signature)
    }

    Object.values(incident.officers).map((officer, index) => {
      Object.keys(officer).map(key => {
        const modifiedKey = `${officerHeaders[index]}_${key}`
        headers.add(modifiedKey)

        flatIncident[modifiedKey] = officer[key]
      })
    })

    incident.subjects.map((subject, index) => {
      Object.keys(subject).map(key => {
        const modifiedKey = `${subjectHeaders[index]}_${key}`
        headers.add(modifiedKey)

        flatIncident[modifiedKey] = subject[key]
      })
    })

    flatIncident.datetime = '' + flatIncident.date + ' ' + flatIncident.time

    delete flatIncident.date
    delete flatIncident.time

    return flatIncident
  })

  headers.delete('date')
  headers.delete('time')

  headers.add('datetime')

  return [flat, headers]
}

// Flatten
module.exports = flatten
