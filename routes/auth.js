const express = require('express');
const router = express.Router();

const users = []; // Temporary in-memory user list

router.get('/login', (req, res) => {
  res.render('auth/login', { error: null });
});

router.post('/login', (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username && u.password === password);
  if (user) {
    req.session.user = user;
    res.redirect(user.role === 'admin' ? '/admin' : '/');
  } else {
    res.render('auth/login', { error: 'Invalid credentials' });
  }
});

router.get('/register', (req, res) => {
  res.render('auth/register', { error: null });
});

router.post('/register', (req, res) => {
  const { username, email, password } = req.body;
  if (users.some(u => u.username === username)) {
    res.render('auth/register', { error: 'Username already taken' });
  } else {
    const newUser = { username, email, password, role: username === 'harsha' ? 'admin' : 'user' };
    users.push(newUser);
    req.session.user = newUser;
    res.redirect(newUser.role === 'admin' ? '/admin' : '/');
  }
});

module.exports = router;
