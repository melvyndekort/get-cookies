import { handler } from './index.js';
import fs from 'fs'

const data = fs.readFileSync('./event.json', 'utf8')
const event = JSON.parse(data);

handler(
  event,
  {},
  function(data,ss) {
    console.log(data);
    console.log(ss);
  }
);
