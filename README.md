# 🎬 IMDb Clone & Data Analysis - Final Project

A high-performance IMDb clone and data analysis platform using SQLite, Flask, and advanced SQL. This project is designed to meet all requirements for database structure, web application, and data analysis.

## 📁 Project Structure

```
project/
├── README.md (project overview)
├── schema/
│   └── schema.sql (database schema)
├── queries/
│   ├── web_queries.sql (web app queries)
│   └── analysis_queries.sql (analysis queries)
├── documentation/
│   └── queries_explanation.md (query explanations)
├── static/ (CSS)
├── templates/ (HTML)
├── simple_app.py (main Flask app)
├── imdb.db (SQLite database)
├── requirements.txt
└── dataset/ (IMDB TSV.GZ files)
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Create the database:**
   - Use the schema in `schema/schema.sql`.
   - Import data from the `dataset/` folder using your import script or tool.
3. **Run the web app:**
   ```bash
   python simple_app.py
   ```
4. **Open in browser:**
   - Go to [http://localhost:5000](http://localhost:5000)

## 🏗️ Features
- Movie, series, episode, and person pages
- Filterable listings
- Search engine
- Adult/genre filtering
- Data analysis dashboards

## 📊 Data Analysis
- Rating trends
- Genre popularity
- Director/actor performance
- Collaboration networks

## 📚 Documentation
- See `documentation/queries_explanation.md` for query explanations
- See `queries/` for all SQL used in the project
- See `schema/schema.sql` for the full database schema

---

**This project is fully SQLite-based, optimized, and ready for submission!**
