```javascript
// File Path: src/api/pdfUpload.js
// Production-Quality File Upload Backend Script

const express = require('express');
const fs = require('fs');
require('multer')({ dest: 'uploads' });

// Initialize Express App
const app = express();

// Set middleware for handling uploaded files
app.post('/upload/pdf', multer.single('file')), (req, res) => {
    try {
        if (!fs.existsSync(req.file.path))) { // File already exists in uploads directory
            fs.rename(req.file.path, `${req.file.originalname}.backup`, err => {
                if (err) {
                    console.error(`Error renaming backup file: ${err}`)");
                    return res.status(500).json({ error: "Backup file rename failed" });
                } else {
                    res.status(201).json({ message: "File uploaded successfully. Backup saved as .backup", file: { name: req.file.originalname, path: `${req.file.originalname}.backup` } });
                }
            }) || fs.move(req.file.path, `${req.file.originalname}.backup`, (err) => {
                if (err) {
                    console.error(`Error moving backup file: ${err}`));
                    return res.status(500).json({ error: "Backup file move failed" });
                } else {
                    res.status(201).json({
                        message: "File uploaded successfully. Backup saved as .backup",
                        file: { name: req.file.originalname, path: `${req.file.originalname}.backup` }
                    });
                }
            }) }) 
        } else {
            fs.rename(req.file.path, req.file.originalname), (err) => {
                if (err) {
                    console.error(`Error renaming uploaded file back to its original name: ${err}`));
                    return res.status(500).json({ error: "Renaming uploaded file failed" });
                } else {
                    res.status(201).json({
                        message: "File uploaded successfully. Renamed back to original name.",
                        file: { name: req.file.originalname, path: req.file.originalname } 
                    });
                }
            });
        }
    } catch (error) {
        console.error(`Error handling file upload: ${error}`));
        return res.status(500).json({ error: "Failed to handle file upload" });
    }
});

// Route for serving uploaded PDFs
app.get('/upload/pdf/:id', (req, res)) => {
    try {
        // Check if PDF exists before sending response
        const filePath = `${__dirname}/uploads/${req.params.id}.pdf`;
        fs.access(filePath, fs.constants.F_OK), (err) => {
            if (!err) {
                // Serve the uploaded PDF file
                res.setHeader('Content-Type', 'application/pdf'));
                fs.createReadStream(filePath).pipe(res);
                return;
            }
        } catch (error) {
            console.error(`Error serving uploaded PDF: ${error}`));
            res.status(500).json({ error: "Failed to serve uploaded PDF" });
            return;
        }
    } catch (error) {
        console.error("Error serving uploaded PDF: ", error);
        res.status(500).json({ error: "Failed to serve uploaded PDF" });
        return;
    }
};

// Start the server
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`Server started on port ${PORT}).`);
}));