var express = require("express");
var multer = require('multer');
var router = express.Router();
const fs = require('fs');

var cp = require("child_process");

router.get("/", function(req, res, next) {
    res.send("hello");
});

const storage = multer.diskStorage({
    destination: (req, file, callBack) => {
        callBack(null, 'uploads')
    },
    filename: (req, file, callBack) => {
        callBack(null, `${file.originalname}`)
    }
})

let upload = multer({ dest: 'uploads/' })

router.post("/", upload.array('file'), function(req, res, next) {
    console.log("got file");
    const files = req.files;
    console.log(files);
    if (!files) {
        const error = new Error('No File')
        error.httpStatusCode = 400
        return next(error)
    }
    
    

    const parentDirname = __dirname.split('/').slice(0, -1).join('/');
    
    cp.exec(`python3 execute.py ${files[0].filename} ${files[1].filename} ${files[2].filename}`, {cwd: parentDirname}, function(error,stdout,stderr) {
        if (error) {
            console.log("here err");
            console.log(error);
            return;
        }

        console.log("sending........");

        fs.readFile('result.png', (err, data) => {
            if (err) throw err;
            console.log("sending...");
            res.send(new Buffer(data).toString('base64'));
        });

        console.log("success");

    });
})

module.exports = router;
