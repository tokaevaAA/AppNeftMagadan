var express = require("express");
var multer = require('multer');
var router = express.Router();
const fs = require('fs');
var xlsx = require('node-xlsx');

var cp = require("child_process");

const storage = multer.diskStorage({
    destination: (req, file, callBack) => {
        callBack(null, 'uploads')
    },
    filename: (req, file, callBack) => {
        callBack(null, `${file.originalname}`)
    }
})

let upload = multer({ dest: 'multiple_uploads/' })

router.post("/", upload.array('file'), function(req, res, next) {
    const files = req.files;
    console.log(files);
    if (!files) {
        const error = new Error('No File')
        error.httpStatusCode = 400
        return next(error)
    }

    const filenamesArray = [];

    const parentDirname = __dirname.split('/').slice(0, -1).join('/');

    for (let i = 0; i < files.length; i++) {
        filenamesArray.push(`${parentDirname}/multiple_uploads/${files[i].filename}`);
    }

    cp.exec(`python3 executeMag.py ${filenamesArray.join(' ')}`, {cwd: parentDirname}, function(error,stdout,stderr) {
        if (error) {
            console.log(error);
            return;
        }

        const filesToRespond = [];

        fs.readFile(`${parentDirname}/OtchetOneNumber.xlsx`, (err, data) => {
            if (err) throw err;
            filesToRespond.push(xlsx.parse(data));

            fs.readFile(`${parentDirname}/OtchetWithProviders.xlsx`, (err, data) => {
                if (err) throw err;
                filesToRespond.push(xlsx.parse(data));
                res.send(filesToRespond);
            });
        });
    });
})

module.exports = router;
