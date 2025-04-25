const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
    res.render('home');
});

router.get('/admin', (req, res) => {
    if (req.session.user && req.session.user.role === 'admin') {
        res.send('<h1>Welcome Admin Harsha</h1>');
    } else {
        res.status(403).send('Forbidden');
    }
});

module.exports = router;
