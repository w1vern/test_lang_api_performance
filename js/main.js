const express = require("express")
const { Pool } = require("pg")
require("dotenv").config()

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_IP,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

const app = express()

app.get("/api/test1", async (req, res) => {
  try {
    const result = await pool.query('SELECT field1, field2 FROM data WHERE field2 > 995');
    res.status(200).json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
})

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});