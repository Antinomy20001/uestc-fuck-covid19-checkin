var express = require('express')
var request = require('request')
var app = express()
app.use('/', function (req, res) {
    console.log(req.headers.cookie)
    request.post({
        url: 'http://fuck-checkin-app:8000/origin_index_cookie/',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify({
            cookie: req.headers.cookie
        })
    }, (err, resp, body) => {
    })
    req.pipe(request(req.url)).pipe(res)
})
app.listen(3000)