const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// MySQL connection configuration
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root', // Replace with your MySQL username
    password: 'muki', // Replace with your MySQL password
    database: 'ocr_live_results'
});

db.connect((err) => {       
    if (err) throw err;
    console.log('Connected to MySQL Database');
});

// GET endpoint for root URL
app.get('/', (req, res) => {
    res.send('OCR Live Feed Backend is running. Use /save-ocr for POST requests or /get-ocr to retrieve data.');
});

// GET endpoint to retrieve OCR results
app.get('/get-ocr', (req, res) => {
    db.query('SELECT * FROM detected_text', (err, results) => {
        if (err) {
            console.error(err);
            res.status(500).send('Error retrieving data');
            return;
        }
        res.json(results);
    });
});

// POST endpoint to store OCR results
app.post('/save-ocr', (req, res) => {
    const { imageName, detectedText, confidence } = req.body;
    const query = 'INSERT INTO detected_text (image_name, detected_text, confidence) VALUES (?, ?, ?)';
    db.query(query, [imageName, detectedText, confidence], (err, result) => {
        if (err) {
            console.error(err);
            res.status(500).send('Error saving to database');
            return;
        }
        res.status(200).send('Data saved successfully');
    });
});

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});