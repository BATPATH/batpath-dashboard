// Full-stack BATPATH Dashboard (React Frontend, Node.js Backend, PostgreSQL Database)
// This will be a fully functional dashboard for coaches to enter and track player data.

// ------------------------- FRONTEND (React) -------------------------
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = () => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [team, setTeam] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    axios.get('/api/auth/user')
      .then(response => {
        setUser(response.data);
        return axios.get(`/api/team/${response.data.team_id}`);
      })
      .then(response => {
        setTeam(response.data);
        return axios.get(`/api/players?team=${response.data.id}`);
      })
      .then(response => {
        setPlayers(response.data);
        setLoading(false);
      })
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  return (
    <div className="container">
      <h1>{team ? `${team.name} Player Dashboard` : 'BATPATH Player Dashboard'}</h1>
      {loading ? <p>Loading...</p> : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Age</th>
              <th>Exit Velocity</th>
              <th>Throwing Velocity</th>
            </tr>
          </thead>
          <tbody>
            {players.map(player => (
              <tr key={player.id}>
                <td>{player.name}</td>
                <td>{player.age}</td>
                <td>{player.exit_velocity} mph</td>
                <td>{player.throwing_velocity} mph</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Dashboard;

// ------------------------- BACKEND (Node.js / Express) -------------------------
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const cookieParser = require('cookie-parser');

const app = express();
app.use(cors());
app.use(express.json());
app.use(cookieParser());

const pool = new Pool({
  user: 'your_db_user',
  host: 'your_db_host',
  database: 'batpath_db',
  password: 'your_db_password',
  port: 5432,
});

// Authentication route
app.post('/api/auth/login', async (req, res) => {
  const { email } = req.body;
  try {
    const userResult = await pool.query('SELECT * FROM coaches WHERE email = $1', [email]);
    if (userResult.rows.length === 0) {
      return res.status(401).json({ error: 'User not found' });
    }
    const user = userResult.rows[0];
    const token = jwt.sign({ id: user.id, team_id: user.team_id }, 'your_secret_key', { expiresIn: '24h' });
    res.cookie('auth_token', token, { httpOnly: true });
    res.json({ success: true, token, user });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Login failed' });
  }
});

app.get('/api/auth/user', (req, res) => {
  const token = req.cookies.auth_token;
  if (!token) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  try {
    const decoded = jwt.verify(token, 'your_secret_key');
    res.json(decoded);
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
});

// API Route to get player data by team
app.get('/api/players', async (req, res) => {
  const { team } = req.query;
  try {
    const result = await pool.query('SELECT * FROM players WHERE team_id = $1', [team]);
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database query failed' });
  }
});

// Get team info
app.get('/api/team/:id', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM teams WHERE id = $1', [req.params.id]);
    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database query failed' });
  }
});

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

// ------------------------- DATABASE (PostgreSQL) -------------------------
// Run this SQL script to create the database tables
/*
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE coaches (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    team_id INT REFERENCES teams(id)
);

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    exit_velocity INT NOT NULL,
    throwing_velocity INT NOT NULL,
    team_id INT REFERENCES teams(id)
);

INSERT INTO teams (name) VALUES ('Baseball U');
INSERT INTO coaches (email, team_id) VALUES ('deweeseperformance@gmail.com', 1);
INSERT INTO players (name, age, exit_velocity, throwing_velocity, team_id) VALUES
    ('John Doe', 14, 85, 78, 1),
    ('Mike Smith', 16, 92, 84, 1);
*/
