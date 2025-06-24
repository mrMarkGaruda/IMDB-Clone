# Team Members

- **Sayan DE**
- **Abramenko Mark**

# 🎬 IMDb Clone - Movie Database Project

A comprehensive movie database application built using the official IMDb dataset, featuring a complete web interface for browsing movies, TV series, and people information.

## 📋 Project Overview

This IMDb clone provides a full-featured movie database with the following capabilities:

- **Movie Browsing**: Paginated movie listings with filtering by genre, year, and rating
- **TV Series Information**: Complete TV series data with season breakdowns
- **People Profiles**: Actor, director, and crew member information with filmographies
- **Search functionality**: Search across movies, TV series, and people
- **Analytics Dashboard**: Data analysis and visualization of movie trends
- **Rating System**: Integration with IMDb ratings and vote counts

## 🏗️ Architecture

The project uses a SQLite database built from the official IMDb datasets, with a Flask web application providing the user interface.

### Core Components

- **Database**: SQLite with optimized schema and indexes
- **Backend**: Flask web application with RESTful endpoints
- **Frontend**: HTML/CSS/JavaScript with responsive design
- **Data Source**: Official IMDb TSV datasets (7 tables, 50M+ records)

## 📊 Database Schema

The database contains 7 main tables:

- `title_basics` - Core movie/TV information
- `name_basics` - People (actors, directors, etc.)
- `title_ratings` - IMDb ratings and vote counts
- `title_principals` - Cast and crew roles
- `title_crew` - Directors and writers
- `title_akas` - Alternative titles
- `title_episode` - TV episode information

See `schema/schema.sql` for complete table definitions and `schema/schema.png` for the visual diagram.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- SQLite 3
- Flask and dependencies
- ~50GB disk space for full dataset

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd imdb-clone
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download IMDb datasets**
   ```bash
   # Download from https://datasets.imdbws.com/
   mkdir dataset
   # Download all .tsv.gz files to dataset/ folder
   ```

4. **Import data**
   ```bash
   python import_data.py
   # This process takes 2-4 hours for full dataset
   ```

5. **Run the application**
   ```bash
   python simple_app.py
   ```

6. **Access the application**
   Open http://localhost:5000 in your browser

## 📁 Project Structure

```
project/
├── README.md                    # This file - project overview
├── app.py                       # Flask web application
├── requirements.txt             # Python dependencies
├── schema/
│   ├── schema.sql              # Database table definitions
│   └── schema.png              # Visual database diagram
├── import/
│   ├── import_data.py          # Data import scripts
│   └── import.sql              # SQL import statements
├── queries/
│   ├── web_queries.sql         # Production web app queries
│   └── analysis_queries.sql    # Data analysis queries
├── documentation/
│   └── queries_explanation.md  # Detailed query documentation
├── analysis/
│   ├── data_analysis.py        # Analysis scripts
│   └── visualizations.pdf      # Generated charts and graphs
├── static/                     # CSS, JavaScript, images
├── templates/                  # HTML templates
└── dataset/                    # IMDb TSV files (not in repo)
```

## 🔍 Key Features

### Web Interface Features

- **Homepage**: Database statistics and top-rated movies
- **Movie Listings**: Paginated browsing with advanced filters
- **Movie Details**: Complete information including cast, crew, ratings
- **TV Series Pages**: Season breakdowns and episode information
- **People Profiles**: Actor/director pages with complete filmographies
- **Search**: Unified search across all content types
- **Analytics**: Data visualization and trend analysis

### Technical Features

- **Performance Optimized**: Strategic indexes and query optimization
- **Scalable**: Handles 50M+ records efficiently
- **Security**: Parameterized queries prevent SQL injection
- **Responsive**: Mobile-friendly interface
- **RESTful API**: Clean endpoints for all functionality

## 📈 Performance

- **Database Size**: ~8GB (full IMDb dataset)
- **Query Performance**: <100ms for most operations
- **Concurrent Users**: 50+ simultaneous users supported
- **Memory Usage**: ~200MB typical, ~500MB peak

## 🧪 Analysis Capabilities

The project includes comprehensive data analysis features:

- **Rating Trends**: Movie quality over time
- **Genre Analysis**: Popularity and performance by genre
- **Director Statistics**: Success metrics for directors
- **Actor Networks**: Collaboration analysis
- **Temporal Trends**: Industry changes over decades

See `analysis/visualizations.pdf` for sample analyses and charts.

## 🛠️ Development

### Database Management

- **Schema Updates**: Modify `schema/schema.sql`
- **Query Development**: Test in `queries/` files first
- **Performance**: Use `EXPLAIN QUERY PLAN` for optimization
- **Backup**: Regular SQLite database backups recommended

### Web Development

- **Routes**: Add new endpoints in `app.py`
- **Templates**: HTML templates in `templates/`
- **Static Files**: CSS/JS in `static/`
- **Testing**: Include unit tests for new features

### Data Analysis

- **New Analyses**: Add scripts to `analysis/`
- **Visualization**: Update `visualizations.pdf` with new charts
- **Documentation**: Update `queries_explanation.md` for new queries

## 📝 Documentation

- **README.md** - This overview document
- **schema/schema.sql** - Complete database schema
- **queries_explanation.md** - Detailed query documentation
- **Code Comments** - Inline documentation in all files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project uses data from IMDb datasets, which are available for personal and non-commercial use. Please review IMDb's licensing terms before any commercial use.

## 🔗 Resources

- [IMDb Datasets](https://datasets.imdbws.com/) - Official data source
- [SQLite Documentation](https://sqlite.org/docs.html) - Database reference
- [Flask Documentation](https://flask.palletsprojects.com/) - Web framework guide

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review query examples in `queries/` folder

---

*Last updated: June 2025*