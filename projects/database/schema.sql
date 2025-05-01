```
-- File Path: database/schema.sql
-- Description: Database schema definition file executed during setup.

-- Project Structure Match:
/*
  Table Definitions
*/
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    passwordHash VARCHAR(255)
);

/*
  Schema Metadata
*/
CREATE TABLE meta (
    key VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL,
    PRIMARY KEY (key)
);
```
This is a simple production-quality database schema definition file. It includes table definitions for users and an extra table `meta` to store metadata. Please adjust the table structure, column types, and constraints according to your project's requirements.