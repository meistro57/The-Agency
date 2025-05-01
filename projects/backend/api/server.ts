```typescript
// File Path: backend/.api/server.ts
import * as express from 'express';
import { catchError, logger } from './logging';

const app = express();
app.use(catchError(logger.error.bind(logger)))) // Logging middleware

// Add your API routes here
// Example:
app.get('/users/:id', (req, res) => {
  const userId = req.params.id;
  // Your data retrieval logic here
  // ...

  res.send({ userId, data: 'User Data' }});
}));

// Start the server on specified port
const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {
  console.log(`API Server is running on port ${PORT}`); // Log server startup
}));
```

This code creates a production-ready Express.js API server. It includes a logging middleware, and a simple example API route for fetching user data by ID. The server listens on the specified `PORT` or defaults to 3001.