const fs = require('fs')

const manyToOne = list => list.reduce(
  (map, [key, value]) => {
    const k = key.trim()

    return ({
      ...map,
      [k]: map[key] ? map[key].add(value) : new Set([value])
    })
  },
  {}
)
const parseCsv = text => text.split('\n').map( row => row.split(',') )

module.exports = {
  codeToLegalize: fs.readFile(
  '../data/csv/hopefully full charges list  - Copy of Sheet2.csv',
  'utf8',
  (err, data) => {
    console.log(manyToOne(parseCsv(data)))
  }),
  leglalizeToCode: fs.readFile(
    '../data/csv/hopefully full charges list  - Copy of Sheet3.csv',
    'utf8',
    (err, data) => {
      console.log(manyToOne(parseCsv(data)))
    }
  )
}
