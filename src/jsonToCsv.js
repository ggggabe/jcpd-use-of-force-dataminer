const json = require('./json/jcpd_force_2019.json')
const fs = require('fs')

const flatten = require('./flatten')

//const flattenedJson = require('./testJson.json')

function trim(s) {
  return (s || '').replace(/^"|"$/g, '').replace(/"/g, '\'')
}

const escape = val => {
  switch (typeof val) {
    case 'string':
      return `"${trim(val)}"`
    case 'boolean':
      return val
    case 'number':
      return val
    case 'object':
      return val && val.length
        ? `"${trim(val.join(','))}"`
        : ''
    default:
      return val || ''
  }
}

const convertCsv = ([arr, headers]) => {
  const keys = [...headers]
  const csvArray = [keys.map(val => escape(val)).join(',')]

  arr.map(incident => {
    const incidentCsvLine = keys.map(key => escape(incident[key])).join(',')

    csvArray.push(incidentCsvLine)
  })

  return csvArray
}


const save = (csvArray) => {
  fs.writeFile(
    "./tableau-friendly.csv",
    csvArray.join('\n'),
    err => err ? console.log(err) : console.log("The file was saved!"))
}

save(convertCsv(flatten(Object.values(json))))
fs.writeFile('jcpd.json', JSON.stringify(Object.values(json)), err => err ? console.log(err) : console.log("The file was saved!"))
