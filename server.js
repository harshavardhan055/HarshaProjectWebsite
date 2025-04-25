
const express = require('express');
const session = require('express-session');
const path = require('path');
const app = express();
const mainRoutes = require('./routes/main');

app.use(session({ secret: 'harsha_secret', resave: false, saveUninitialized: true }));

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.static(path.join(__dirname, 'public')));

// Pass IP to views for admin check
app.use((req, res, next) => {
    const ip = req.ip.replace("::ffff:", "");
    res.locals.ip = ip;
    next();
});

app.use('/', mainRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server started on http://localhost:${PORT}`));
        