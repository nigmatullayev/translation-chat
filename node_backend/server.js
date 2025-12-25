const express = require("express");
const axios = require("axios");
const path = require("path");

const app = express();
app.use(express.json());
app.use(express.static("public"));

app.post("/api/translate", async (req, res) => {
  try {
    const { text, source_lang, target_lang } = req.body;

    const response = await axios.post("http://localhost:5000/translate", {
      text,
      source_lang,
      target_lang
    });

    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: "Translate error" });
  }
});

app.listen(3000, () => {
  console.log("Node.js server running on http://localhost:3000");
});
