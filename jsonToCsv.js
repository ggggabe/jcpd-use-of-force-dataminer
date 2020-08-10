const json = require('./jcpd_force_2019.json')
const flattenedJson = require('./testJson.json')
const fs = require('fs')


const main = () => {
  const jsonValues = Object.values(json)

  /*
  const flattenedJson = jsonValues.map( val => {
    return flatten(val)
  })
  */

  save(convertCsv(flattenedJson))
}

const escape = val => {
  switch (typeof val) {
    case 'string':
      return `"${val}"`
    default:
      return val
  }
}

const convertCsv = (arr) => {
//  [
//    {
//      key1: value1,
//      key2: value1a,
//      key3: value1b,
//    },
//    {
//      key1: value2,
//      key2: value2a,
//      key3: value2b,
//    }
//  ]

//  [
//    '"key1", "key2", "key3"'
//    '"val1", "val1a", "val1b"
//    '"val2", "val2a", "val2b"
//  ]

  const keys = Object.keys(arr[0])
  const csvArray = [keys.map(val => escape(val)).join(',')]

  arr.map( incident => {
    const incidentCsvLine = keys.map(key => escape(incident[key])).join(',')

    csvArray.push(incidentCsvLine)
  })

  console.log(csvArray)

  return csvArray
}


const save = (csvArray) => {
  fs.writeFile(
    "./tableau-friendly.csv",
    csvArray.join('\n'),
    err => err ? console.log(err) : console.log("The file was saved!")
  )
}

main()
