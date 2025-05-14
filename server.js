const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Store automation data
let automationData = {
  connections: [],
  posts: [],
  messages: []
};

// API Endpoints
app.post('/api/automation/start', (req, res) => {
  const { type, settings } = req.body;
  console.log(`Starting ${type} automation with settings:`, settings);
  res.json({ status: 'success', message: `${type} automation started` });
});

app.post('/api/automation/stop', (req, res) => {
  const { type } = req.body;
  console.log(`Stopping ${type} automation`);
  res.json({ status: 'success', message: `${type} automation stopped` });
});

app.post('/api/connections', (req, res) => {
  const { profile } = req.body;
  automationData.connections.push(profile);
  res.json({ status: 'success', message: 'Connection request logged' });
});

app.post('/api/posts', (req, res) => {
  const { content } = req.body;
  automationData.posts.push(content);
  res.json({ status: 'success', message: 'Post created' });
});

app.post('/api/messages', (req, res) => {
  const { message } = req.body;
  automationData.messages.push(message);
  res.json({ status: 'success', message: 'Message sent' });
});

app.get('/api/stats', (req, res) => {
  res.json({
    connections: automationData.connections.length,
    posts: automationData.posts.length,
    messages: automationData.messages.length
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ status: 'error', message: 'Something went wrong!' });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
}); 