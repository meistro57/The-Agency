// Filename: reporter.js
// Production-Quality JavaScript Code for Generating HTML Reports
// Adheres to project's overall structure

// Global variables and functions
const utils = {
  createElement(tagName, props) {
    const element = document.createElement(tagName);
    if (props) Object.keys(props).forEach(prop => {
      element.setAttribute(prop, props[prop]);
    });
    return element;
  },
  appendContent(element, content) {
    if (Array.isArray(content)) {
      content.forEach(c => {
        if (typeof c === 'string') {
          const textElement = document.createTextNode(c);
          element.appendChild(textElement);
        } else if (c.nodeType && !c.tagName) {
          // If it's a DOM node, just append
          element.appendChild(c);
        }
      });
    } else if (content && typeof content === 'object')) {
      // Append child elements recursively
      Object.keys(content).forEach(key => {
        if (utils.createElement) {
          content[key] = utils.createElement(content[key].tagName, content[key].props));
        }
        element.appendChild(content[key]);
      });
    } else if (content && typeof content === 'string') {
      const textElement = document.createTextNode(content);
      element.appendChild(textElement);
    } else {
      console.error('Invalid content type for appending to element.');
    }
  },
};

// Report generation function
function generateReport(data) {
  // Create HTML structure
  const reportContainer = utils.createElement('div', { id: 'report'...
