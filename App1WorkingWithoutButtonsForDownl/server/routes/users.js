var express = require('express');
var router = express.Router();
const { exec } = require("child_process");
const fs = require('fs');
const path = require('path');

var cp = require("child_process");



/* GET users listing. */

router.get('/', function(req, res, next) {
  cp.exec("python3 create_file.py", {cwd: '/home/ruslan/SiriusProject/project'}, function(error,stdout,stderr) {
    if (error) {
      console.log(error.message);
      return;
    }
    if (stderr) {
        console.log(stderr);
        return;
    }
    console.log(stdout);
  
  });

  console.log(__dirname);


  fs.readFile('/home/ruslan/SiriusProject/project/train1.csv', (err, data) => {
    if (err) throw err;
    res.send(data);
  });
});

module.exports = router;
