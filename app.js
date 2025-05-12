const express = require('express');
const path = require('path');
const session = require('express-session');

const app = express();
const PORT = 3000;

const mainRoutes = require('./routes/main');
const authRoutes = require('./routes/auth');

// View engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.use(session({
    secret: 'harsha_secret',
    resave: false,
    saveUninitialized: true
}));

// Routes
app.use('/', mainRoutes);
app.use('/auth', authRoutes);

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
