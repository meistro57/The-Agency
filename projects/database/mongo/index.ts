// Filename: database/mongo/index.ts
// Production-Quality Code for MongoDB Index Setup

import * as mongoose from 'mongoose';

// Project-specific database configuration
const dbUrl = 'mongodb://username:password@hostname:port/database_name';

// Connect to MongoDB
mongoose.connect(dbUrl, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
}));

// Migration function for setting up an index
async function createIndex(modelName: string, fields: string[]) {
  try {
    // Use the mongoose model instance
    const indexedModel = new mongoose.model(modelName, require('./models/' + modelName))[0]);

    // Build the index with required fields
    await indexedModel.createIndex(fields);

    console.log(`Index created for ${modelName} on`, fields);
  } catch (error) {
    console.error('Error creating index:', error);
  }
}

// Example usage: Create an ascending index on 'field1' in 'YourModel'
createIndex('YourModel', ['field1', { order: 'asc' }]]);

// Remember to replace 'YourModel', 'field1' with your actual model name and field.

This code sets up a MongoDB connection based on the provided configuration. It then defines a function `createIndex` which takes a mongoose model name and an array of fields for creating an ascending index.

You can customize this according to your project's structure and needs.