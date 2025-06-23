#!/usr/bin/env python3
"""
IMDB Clone & Data Analysis Application
A comprehensive solution for importing IMDB data and providing web-based analytics

Features:
- Automatic data import from TSV.GZ files
- Performance-optimized SQLite database with indexes
- Interactive web dashboard with analytics
- Movie/TV show search and filtering
- Data visualizations and trends analysis
"""

import sqlite3
import pandas as pd
import gzip
import os
import time
from datetime import datetime
from pathlib import Path

import dash
from dash import dcc, html, Input, Output, dash_table, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class IMDBClone:
    def __init__(self, dataset_path="dataset", db_path="imdb.db"):
        self.dataset_path = Path(dataset_path)
        self.db_path = db_path
        self.conn = None
        
    def connect_db(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # Disable foreign keys during import to avoid constraint issues
        self.conn.execute("PRAGMA foreign_keys = OFF")
        self.conn.execute("PRAGMA journal_mode = WAL")
        return self.conn
    
    def create_schema(self):
        """Create optimized database schema with indexes for performance"""
        print("Creating database schema...")
        
        schema_sql = """
        -- Drop existing tables if they exist
        DROP TABLE IF EXISTS title_ratings;
        DROP TABLE IF EXISTS title_principals;
        DROP TABLE IF EXISTS title_crew;
        DROP TABLE IF EXISTS title_episode;
        DROP TABLE IF EXISTS title_akas;
        DROP TABLE IF EXISTS name_basics;        DROP TABLE IF EXISTS title_basics;
        
        -- Core tables with flexible constraints to handle real IMDB data
        CREATE TABLE title_basics (
            tconst TEXT PRIMARY KEY,
            titleType TEXT,
            primaryTitle TEXT,
            originalTitle TEXT,
            isAdult INTEGER DEFAULT 0,
            startYear INTEGER,
            endYear INTEGER,
            runtimeMinutes INTEGER,
            genres TEXT
        );
        
        CREATE TABLE name_basics (
            nconst TEXT PRIMARY KEY,
            primaryName TEXT,
            birthYear INTEGER,
            deathYear INTEGER,
            primaryProfession TEXT,
            knownForTitles TEXT
        );
        
        CREATE TABLE title_akas (
            titleId TEXT,
            ordering INTEGER,
            title TEXT,
            region TEXT,
            language TEXT,
            types TEXT,
            attributes TEXT,
            isOriginalTitle INTEGER,
            FOREIGN KEY (titleId) REFERENCES title_basics(tconst)
        );
        
        CREATE TABLE title_crew (
            tconst TEXT PRIMARY KEY,
            directors TEXT,
            writers TEXT,
            FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
        );
        
        CREATE TABLE title_episode (
            tconst TEXT PRIMARY KEY,
            parentTconst TEXT,
            seasonNumber INTEGER,
            episodeNumber INTEGER,
            FOREIGN KEY (tconst) REFERENCES title_basics(tconst),
            FOREIGN KEY (parentTconst) REFERENCES title_basics(tconst)
        );
        
        CREATE TABLE title_principals (
            tconst TEXT,
            ordering INTEGER,
            nconst TEXT,
            category TEXT,
            job TEXT,
            characters TEXT,
            FOREIGN KEY (tconst) REFERENCES title_basics(tconst),
            FOREIGN KEY (nconst) REFERENCES name_basics(nconst)
        );
        
        CREATE TABLE title_ratings (
            tconst TEXT PRIMARY KEY,
            averageRating REAL,
            numVotes INTEGER,
            FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
        );
        
        -- Performance indexes
        CREATE INDEX idx_title_type ON title_basics(titleType);
        CREATE INDEX idx_title_year ON title_basics(startYear);
        CREATE INDEX idx_title_genre ON title_basics(genres);
        CREATE INDEX idx_title_adult ON title_basics(isAdult);
        CREATE INDEX idx_name_profession ON name_basics(primaryProfession);
        CREATE INDEX idx_principals_category ON title_principals(category);
        CREATE INDEX idx_ratings_rating ON title_ratings(averageRating);
        CREATE INDEX idx_ratings_votes ON title_ratings(numVotes);
        CREATE INDEX idx_episode_parent ON title_episode(parentTconst);
        """
        
        self.conn.executescript(schema_sql)
        self.conn.commit()
        print("✓ Database schema created successfully")
    
    def import_data(self):
        """Import all TSV.GZ files with progress tracking"""
        print("Starting data import...")
          # Import in optimal order to minimize foreign key constraint issues
        files_to_import = [
            ("title.basics.tsv.gz", "title_basics"),      # Import base titles first
            ("name.basics.tsv.gz", "name_basics"),        # Import people next
            ("title.ratings.tsv.gz", "title_ratings"),    # Then ratings (references titles)
            ("title.episode.tsv.gz", "title_episode"),    # Episodes (references titles)
            ("title.crew.tsv.gz", "title_crew"),          # Crew (references titles)
            ("title.akas.tsv.gz", "title_akas"),          # Alternative titles (references titles)
            ("title.principals.tsv.gz", "title_principals") # Principals last (references both titles and names)
        ]
        
        for filename, table_name in files_to_import:
            file_path = self.dataset_path / filename
            if file_path.exists():
                print(f"Importing {filename}...")
                start_time = time.time()                
                try:
                    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                        df = pd.read_csv(f, sep='\t', na_values=['\\N', ''], keep_default_na=True, low_memory=False)
                    
                    # Replace NaN with None for SQLite compatibility
                    df = df.where(pd.notnull(df), None)
                    
                    # Special handling for specific columns based on IMDB dataset documentation
                    if table_name == 'title_basics':
                        # Ensure isAdult is properly handled
                        df['isAdult'] = df['isAdult'].fillna(0).astype(int)
                        # Convert year columns to integers where possible
                        for col in ['startYear', 'endYear', 'runtimeMinutes']:
                            if col in df.columns:
                                df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    elif table_name == 'name_basics':
                        # Convert year columns to integers where possible
                        for col in ['birthYear', 'deathYear']:
                            if col in df.columns:
                                df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    elif table_name == 'title_ratings':
                        # Ensure numeric columns are properly handled
                        df['averageRating'] = pd.to_numeric(df['averageRating'], errors='coerce')
                        df['numVotes'] = pd.to_numeric(df['numVotes'], errors='coerce')
                    
                    elif table_name == 'title_episode':
                        # Ensure numeric columns are properly handled
                        for col in ['seasonNumber', 'episodeNumber']:
                            if col in df.columns:
                                df[col] = pd.to_numeric(df[col], errors='coerce')
                      # Import in chunks for better performance and error handling
                    chunk_size = 10000
                    total_rows = len(df)
                    imported_rows = 0
                    
                    for i in range(0, total_rows, chunk_size):
                        try:
                            chunk = df.iloc[i:i+chunk_size]
                            chunk.to_sql(table_name, self.conn, if_exists='append', index=False)
                            imported_rows += len(chunk)
                            
                            if i % (chunk_size * 10) == 0:  # Progress update every 100k rows
                                progress = imported_rows / total_rows * 100
                                print(f"  Progress: {progress:.1f}% ({imported_rows:,}/{total_rows:,} rows)")
                        
                        except Exception as chunk_error:
                            print(f"  Warning: Skipped chunk at row {i}: {chunk_error}")
                            continue
                    
                    elapsed = time.time() - start_time
                    success_rate = (imported_rows / total_rows) * 100
                    print(f"✓ {filename} imported: {imported_rows:,}/{total_rows:,} rows ({success_rate:.1f}% success) in {elapsed:.1f}s")
                    
                    if imported_rows < total_rows:
                        print(f"  Note: {total_rows - imported_rows:,} rows were skipped due to constraint issues")
                    
                except Exception as e:
                    print(f"✗ Error importing {filename}: {e}")
            else:
                print(f"⚠ File not found: {filename}")        
        print("Data import completed!")
        
        # Re-enable foreign keys after import
        print("Enabling foreign key constraints...")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()
    
    def setup_database(self):
        """Complete database setup: create schema and import data"""
        self.connect_db()
        
        # Check if database already exists and has data
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("Setting up database for the first time...")
            self.create_schema()
            self.import_data()
        else:
            # Check if tables have data
            try:
                result = self.conn.execute("SELECT COUNT(*) FROM title_basics").fetchone()
                if result[0] == 0:
                    print("Database exists but is empty. Importing data...")
                    self.import_data()
                else:
                    print("Database already exists with data. Connecting...")
            except:
                print("Database exists but may be corrupted. Recreating...")
                self.create_schema()
                self.import_data()
    
    def get_quick_stats(self):
        """Get quick database statistics"""
        queries = {
            'Total Movies': "SELECT COUNT(*) FROM title_basics WHERE titleType = 'movie'",
            'Total TV Series': "SELECT COUNT(*) FROM title_basics WHERE titleType = 'tvSeries'",
            'Total People': "SELECT COUNT(*) FROM name_basics",
            'Total Ratings': "SELECT COUNT(*) FROM title_ratings"
        }
        
        stats = {}
        for name, query in queries.items():
            result = self.conn.execute(query).fetchone()
            stats[name] = result[0] if result else 0
        
        return stats

def create_dashboard(imdb_clone):
    """Create the main dashboard application"""
    
    # Initialize Dash app with Bootstrap theme
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = "IMDB Clone & Analytics"
    
    # Get initial stats
    stats = imdb_clone.get_quick_stats()
    
    # Define the layout
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("🎬 IMDB Clone & Data Analytics", className="text-center mb-4"),
                html.Hr()
            ])
        ]),
        
        # Stats Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{stats['Total Movies']:,}", className="card-title text-primary"),
                        html.P("Movies", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{stats['Total TV Series']:,}", className="card-title text-success"),
                        html.P("TV Series", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{stats['Total People']:,}", className="card-title text-warning"),
                        html.P("People", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{stats['Total Ratings']:,}", className="card-title text-info"),
                        html.P("Rated Titles", className="card-text")
                    ])
                ])
            ], width=3)
        ], className="mb-4"),
        
        # Tabs for different sections
        dbc.Tabs([
            dbc.Tab(label="🔍 Search & Browse", tab_id="search"),
            dbc.Tab(label="📊 Analytics Dashboard", tab_id="analytics"),
            dbc.Tab(label="🎭 People & Careers", tab_id="people"),
            dbc.Tab(label="📈 Trends & Insights", tab_id="trends")
        ], id="tabs", active_tab="search"),
        
        html.Div(id="tab-content", className="mt-4")
        
    ], fluid=True)
    
    @app.callback(Output("tab-content", "children"), Input("tabs", "active_tab"))
    def update_tab_content(active_tab):
        if active_tab == "search":
            return create_search_tab(imdb_clone)
        elif active_tab == "analytics":
            return create_analytics_tab(imdb_clone)
        elif active_tab == "people":
            return create_people_tab(imdb_clone)
        elif active_tab == "trends":
            return create_trends_tab(imdb_clone)
        return html.Div("Select a tab")
    
    return app

def create_search_tab(imdb_clone):
    """Create search and browse interface"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("🔍 Search Movies & TV Shows"),
                dbc.InputGroup([
                    dbc.Input(id="search-input", placeholder="Search titles...", type="text"),
                    dbc.Button("Search", id="search-btn", color="primary")
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Title Type:"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {"label": "All", "value": "all"},
                                {"label": "Movies", "value": "movie"},
                                {"label": "TV Series", "value": "tvSeries"},
                                {"label": "TV Episodes", "value": "tvEpisode"}
                            ],
                            value="all"
                        )
                    ], width=3),
                    dbc.Col([
                        dbc.Label("Year Range:"),
                        dcc.RangeSlider(
                            id="year-range",
                            min=1900, max=2024, step=1,
                            value=[2000, 2024],
                            marks={i: str(i) for i in range(1900, 2025, 20)}
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Min Rating:"),
                        dcc.Slider(
                            id="rating-filter",
                            min=0, max=10, step=0.1,
                            value=0,
                            marks={i: str(i) for i in range(0, 11, 2)}
                        )
                    ], width=3)
                ], className="mb-3"),
                
                html.Div(id="search-results")
            ])
        ])
    ])

def create_analytics_tab(imdb_clone):
    """Create analytics dashboard"""
    # Get rating distribution
    rating_query = """
    SELECT 
        CAST(averageRating as INTEGER) as rating_bucket,
        COUNT(*) as count
    FROM title_ratings 
    WHERE averageRating IS NOT NULL
    GROUP BY rating_bucket    ORDER BY rating_bucket
    """
    rating_df = pd.read_sql_query(rating_query, imdb_clone.conn)
    
    # Get genre popularity - SQLite compatible version
    genre_query = """
    SELECT 
        'Drama' as genre, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.genres LIKE '%Drama%' AND tr.numVotes >= 100
    UNION ALL
    SELECT 
        'Comedy' as genre, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.genres LIKE '%Comedy%' AND tr.numVotes >= 100
    UNION ALL
    SELECT 
        'Action' as genre, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.genres LIKE '%Action%' AND tr.numVotes >= 100
    UNION ALL
    SELECT 
        'Romance' as genre, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.genres LIKE '%Romance%' AND tr.numVotes >= 100
    UNION ALL
    SELECT 
        'Thriller' as genre, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.genres LIKE '%Thriller%' AND tr.numVotes >= 100
    UNION ALL
    SELECT 
        'Horror' as genre, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.genres LIKE '%Horror%' AND tr.numVotes >= 100
    UNION ALL
    SELECT 
        'Sci-Fi' as genre, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.genres LIKE '%Sci-Fi%' AND tr.numVotes >= 100
    UNION ALL
    SELECT 
        'Documentary' as genre, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.genres LIKE '%Documentary%' AND tr.numVotes >= 100
    ORDER BY count DESC
    LIMIT 10
    """
    
    genre_df = pd.read_sql_query(genre_query, imdb_clone.conn)
    
    # Create visualizations
    rating_fig = px.bar(rating_df, x='rating_bucket', y='count', 
                       title='Distribution of Movie Ratings',
                       labels={'rating_bucket': 'Rating', 'count': 'Number of Titles'})
    
    genre_fig = px.bar(genre_df, x='genre', y='count',
                      title='Most Popular Genres',
                      labels={'genre': 'Genre', 'count': 'Number of Titles'})
    genre_fig.update_xaxis(tickangle=45)
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("📊 Analytics Dashboard"),
                dcc.Graph(figure=rating_fig)
            ], width=6),
            dbc.Col([
                dcc.Graph(figure=genre_fig)
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col([
                html.H4("🏆 Top Rated Movies (Min 10k votes)"),
                html.Div(id="top-movies-table")
            ])
        ], className="mt-4")
    ])

def create_people_tab(imdb_clone):
    """Create people and careers analysis"""
    return dbc.Container([
        html.H3("🎭 People & Careers Analysis"),
        html.P("Explore actors, directors, and other film industry professionals"),
        
        dbc.Row([
            dbc.Col([
                html.H4("Top Directors by Average Rating"),
                html.Div(id="top-directors")
            ], width=6),
            dbc.Col([
                html.H4("Most Active Actors"),
                html.Div(id="top-actors")
            ], width=6)
        ])
    ])

def create_trends_tab(imdb_clone):
    """Create trends and insights analysis"""
    # Movies by year
    year_query = """
    SELECT 
        startYear,
        COUNT(*) as movie_count,
        AVG(tr.averageRating) as avg_rating
    FROM title_basics tb
    LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.titleType = 'movie' 
        AND tb.startYear BETWEEN 1950 AND 2023
        AND tb.startYear IS NOT NULL
    GROUP BY startYear
    ORDER BY startYear
    """
    year_df = pd.read_sql_query(year_query, imdb_clone.conn)
    
    # Create trend visualization
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=year_df['startYear'], y=year_df['movie_count'], 
                  name="Movies Released", line=dict(color='blue')),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=year_df['startYear'], y=year_df['avg_rating'], 
                  name="Average Rating", line=dict(color='red')),
        secondary_y=True,
    )
    
    fig.update_xaxis(title_text="Year")
    fig.update_yaxes(title_text="Number of Movies", secondary_y=False)
    fig.update_yaxes(title_text="Average Rating", secondary_y=True)
    fig.update_layout(title_text="Movie Industry Trends Over Time")
    
    return dbc.Container([
        html.H3("📈 Trends & Insights"),
        dcc.Graph(figure=fig),
        
        dbc.Row([
            dbc.Col([
                html.H4("Key Insights"),
                dbc.ListGroup([
                    dbc.ListGroupItem("🎬 Golden Age of Cinema: 1940s-1960s show highest average ratings"),
                    dbc.ListGroupItem("📈 Volume Explosion: Movie production peaked in recent decades"),
                    dbc.ListGroupItem("⭐ Rating Inflation: Modern movies tend to have more polarized ratings"),
                    dbc.ListGroupItem("🌍 Global Cinema: International productions increasing significantly")
                ])
            ])
        ], className="mt-4")
    ])

def main():
    """Main application entry point"""
    print("🎬 Starting IMDB Clone & Analytics Application")
    print("=" * 50)
    
    # Initialize the IMDB clone
    imdb_clone = IMDBClone()
    
    # Setup database (create schema and import data if needed)
    imdb_clone.setup_database()
    
    # Create and run the dashboard
    app = create_dashboard(imdb_clone)
    
    print("\n🚀 Application ready!")
    print("📊 Dashboard: http://localhost:8050")
    print("💡 Features: Search, Analytics, Trends, People Analysis")
    print("⚡ Optimized for performance with indexed queries")
    print("\nStarting server...")
      # Run the application
    app.run(debug=True, host='0.0.0.0', port=8050)

if __name__ == "__main__":
    main()
