const fs = require('fs')

const manyToOne = list => list.reduce(
  (map, [key, value]) => {
    const k = key.trim().toLowerCase()
    const v = value.toLowerCase()

    return ({
      ...map,
      [k]: map[k] ? map[k].add(v) : new Set([v])
    })
  },
  {}
)
const parseCsv = text => text.split('\n').map(row => row.split(','))

const C2L = {}
const L2C = {}

fs.readFile(
  '../data/csv/hopefully full charges list  - Copy of Sheet2.csv',
  'utf8',
  (err, data) => {
    C2L.unwrap = manyToOne(parseCsv(data))
  }
)

fs.readFile(
  '../data/csv/hopefully full charges list  - Copy of Sheet3.csv',
  'utf8',
  (err, data) => {
    L2C.unwrap = manyToOne(parseCsv(data))
  }
)

module.exports = {
  C2L,
  L2C
}
