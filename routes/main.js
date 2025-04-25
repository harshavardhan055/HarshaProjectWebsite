
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
    res.render('home');
});

router.get('/projects', (req, res) => {
    res.render('projects');
});

router.get('/testings', (req, res) => {
    res.render('testings');
});

router.get('/contact', (req, res) => {
    res.render('contact');
});

router.get('/admin', (req, res) => {
    const ip = req.ip.replace("::ffff:", "");
    if (ip !== "192.168.0.101") return res.status(403).send("Access Denied");
    res.render('admin');
});

module.exports = router;
        