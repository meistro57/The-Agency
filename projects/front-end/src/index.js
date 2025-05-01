// Filename: front-end/src/index.js

// Production-quality React entry point for the frontend.
/* eslint React/no-unmountable-domComponents: "off" */

import React from 'react';
import ReactDOM from 'react-dom';
import './styles.css'; // Assuming a CSS file exists with this name

// Import any necessary modules or components here
import App from './components/App';

// Mount the app to the DOM
ReactDOM.render(<App />, document.getElementById('root'));