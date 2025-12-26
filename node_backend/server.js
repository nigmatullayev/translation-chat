const express = require('express');
const path = require('path');
const { createServer } = require('http');
const { Server } = require('socket.io');
const config = require('./src/config');
const apiRoutes = require('./src/routes/api');
const { handleSocketConnection } = require('./src/controllers/socketController');

// Initialize Express app
const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer);

// Middleware
app.use(express.json());
app.use(express.static('public'));

// API Routes
app.use('/api', apiRoutes);

// Socket.IO connection handler
io.on('connection', (socket) => {
  handleSocketConnection(io, socket);
});

// Start server
httpServer.listen(config.PORT, () => {
  console.log(`Server running on http://localhost:${config.PORT}`);
  console.log(`WebSocket server ready`);
  console.log(`Environment: ${config.NODE_ENV}`);
});
