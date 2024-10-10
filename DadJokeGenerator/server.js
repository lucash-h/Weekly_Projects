const express = require('express');
const path = require('path');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.yourAPI_KEY;

app.use(express.static(path.join(__dirname, 'app')));

app.get('/api-key', (req, res) => {
    res.json({ apiKey: API_KEY });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});