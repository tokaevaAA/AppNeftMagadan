const http = require('http');
const socketIO = require('socket.io');
const express = require('express');
const xlms = require('node-xlsx');
const fs = require('fs');
const cp = require("child_process");
const port = 9000;

var app = express();

app.use('/', (req, res) => {
    res.send("Hello");
})

const server = http.createServer(app);

const io = socketIO(server, {
    cors: { origin: '*' },
    maxHttpBufferSize: 1e8
});

server.listen(port, () => console.log(`server is running on port ${port}`));

var connections = [];

io.on('connection', (socket) => {
    console.log('user connected', socket.id);
    connections.push(socket);

    socket.on('sending tables', (data) => {
        console.log('got files');
        console.log(data['names']);
        for (let i = 0; i < data['names'].length; i++) {
            fs.writeFile(`./uploads/${data['names'][i]}`, data['files'][i], (err) => {
                if (err) {
                    console.log(err);
                    return;
                }
                console.log('successfully writen');
            });
        }
        socket.emit('response', 'Ok');
        var filenamesArray = [];
        for (let i = 0; i < data['names'].length; i++) {
            filenamesArray.push(`./uploads/${data['names'][i]}`);
            filenamesArray.push(data['names'][i]);
        }

        cp.exec(`python3 executeMag.py ${filenamesArray.join(' ')}`, function(error, stdout, stderr) {
            if (error) {
                console.log(error);
                return;
            }
            console.log('success');
            fs.readFile("OtchetOneNumber.xlsx",  (err, masfile1)=>{
                if (err) {
                    console.log(err);
                    return;
                }
                fs.readFile("OtchetWithProviders.xlsx", (err, masfile2)=>{
                    if (err) {
                        console.log(err);
                        return;
                    }
                    var response = [masfile1, masfile2];
                    socket.emit('Otvet', {
                        files: response
                    });
                })
            })
        });
    });

    socket.on("sending oil", async (what_accepted) => {
        var mas_of_bufers = what_accepted['names_of_files']

        fs.writeFile("./uploads_oil/Complexity.txt", mas_of_bufers[0], (err)=>{
            if (err){
                console.log("error complexity");
                return 
            }
            fs.writeFile("./uploads_oil/Scrutiny.txt", mas_of_bufers[1], (err)=>{
                if (err){
                    console.log("error scrutiny");
                    return 
                }
                fs.writeFile("./uploads_oil/MeanGrid.txt", mas_of_bufers[2], (err)=>{
                    if (err){
                        console.log("error meanGrid");
                        return 
                    }
                    cp.exec(`python3 execute.py ./uploads_oil/Complexity.txt ./uploads_oil/Scrutiny.txt ./uploads_oil/MeanGrid.txt`, (err, stdout, stderr)=>{
                        if (err) {
                            console.log(err);
                            return;
                        }
                        fs.readFile(`result.png`, (err, kartinka) => {
                            if (err) throw err;
                            console.log("sending...");
                            socket.emit('Otvet oil', new Buffer(kartinka).toString('base64'));
                        });
                    })
                })
            })
        })
    })

    socket.on('disconnect', () => {
        const index = connections.indexOf(socket);
        connections.splice(index, 1);
        console.log('user disconnected');
    })
});
