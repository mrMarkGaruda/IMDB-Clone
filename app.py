"""
🚀 ULTRA-OPTIMIZED IMDb Clone - Flask Web Application
High-performance IMDb clone with lightning-fast database operations and smart caching
"""
import os
import io
import json
import base64
import warnings
import time
import sqlite3
import psycopg2
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from plotly.utils import PlotlyJSONEncoder
from datetime import datetime
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Configure matplotlib for web deployment
plt.switch_backend('Agg')
matplotlib.use('Agg')

# =======================
# OPTIMIZED DATABASE MANAGER
# =======================

class OptimizedDatabaseManager:
    """High-performance database manager with connection pooling and caching"""
    
    def __init__(self, db_type='sqlite', **config):
        self.db_type = db_type
        self.config = config
        self.max_connections = 10
        self.enable_cache = True
        self._cache = {}
        
        if db_type == 'sqlite':
            self.db_path = config.get('database', 'imdb.db')
        elif db_type == 'postgresql':
            self.pg_config = config
    
    def get_connection(self):
        """Get database connection with optimizations"""
        if self.db_type == 'sqlite':
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # SQLite optimizations
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA cache_size=10000')
            conn.execute('PRAGMA temp_store=MEMORY')
            conn.execute('PRAGMA synchronous=NORMAL')
            return conn
        elif self.db_type == 'postgresql':
            return psycopg2.connect(**self.pg_config)
    
    def execute_query(self, query, params=None):
        """Execute query with caching and optimization"""
        cache_key = f"{query}:{params}"
        
        if self.enable_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for row in rows:
                if self.db_type == 'sqlite':
                    result.append(dict(row))
                else:
                    result.append(dict(zip(columns, row)))
            
            if self.enable_cache:
                self._cache[cache_key] = result
            
            return result
            
        finally:
            conn.close()
    
    def execute_query_pandas(self, query, params=None):
        """Execute query and return pandas DataFrame"""
        conn = self.get_connection()
        try:
            df = pd.read_sql_query(query, conn, params=params)
            return df
        finally:
            conn.close()

class OptimizedQueries:
    """Collection of optimized SQL queries"""
    
    def __init__(self):
        pass
    
    @staticmethod
    def get_popular_movies():
        return """
            SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.genres,
                   tr.averageRating, tr.numVotes
            FROM title_basics tb
            JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titleType = 'movie' AND tr.numVotes >= 1000
            ORDER BY tr.averageRating DESC, tr.numVotes DESC
            LIMIT 10
        """

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-imdb-clone-2025')

# 🚀 OPTIMIZED DATABASE CONFIGURATION
# Automatically detects and configures the best database type available
def detect_database_config():
    """Auto-detect optimal database configuration"""
    # Check for PostgreSQL first (better for production)
    postgres_config = {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'database': os.environ.get('POSTGRES_DB', 'imdb'),
        'user': os.environ.get('POSTGRES_USER', 'imdbuser'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'imdbpass'),
        'port': int(os.environ.get('POSTGRES_PORT', 5432))
    }
    
    # Try PostgreSQL first
    try:
        import psycopg2
        test_conn = psycopg2.connect(**postgres_config)
        test_conn.close()
        print("✅ PostgreSQL detected and configured")
        return 'postgresql', postgres_config
    except:
        pass
    
    # Fallback to SQLite (development/local)
    sqlite_config = {
        'database': os.environ.get('SQLITE_DB', 'imdb.db')
    }
    
    if os.path.exists(sqlite_config['database']):
        print("✅ SQLite database detected and configured")
        return 'sqlite', sqlite_config
    else:
        print("⚠️ No database found. Please run the import process first.")
        return 'sqlite', sqlite_config

# Initialize optimized database
db_type, db_config = detect_database_config()
db = OptimizedDatabaseManager(db_type=db_type, **db_config)
queries = OptimizedQueries()

print(f"🎬 IMDB Clone initialized with {db_type.upper()} database")
print(f"📊 Connection pool: {db.max_connections} connections")
print(f"🗄️ Query cache: {'Enabled' if db.enable_cache else 'Disabled'}")

# Performance monitoring decorator
def monitor_performance(route_name):
    """Decorator to monitor route performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log slow requests
            if execution_time > 1.0:
                print(f"⚠️ Slow request: {route_name} took {execution_time:.3f}s")
            else:
                print(f"⚡ Fast request: {route_name} took {execution_time:.3f}s")
            
            return result
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

def create_plot_url(plt_obj):
    """Convert matplotlib plot to base64 string for web display"""
    img = io.BytesIO()
    plt_obj.savefig(img, format='png', bbox_inches='tight', dpi=150)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url

@app.route('/')
def home():
    """Home page with featured content and statistics"""
    try:        # Get database statistics
        stats = {
            'movies': 0,
            'tv_series': 0,
            'people': 0,
            'ratings': 0
        }
        
        movie_count = db.execute_query('SELECT COUNT(*) as count FROM title_basics WHERE "titleType" = \'movie\'')
        if movie_count:
            stats['movies'] = movie_count[0]['count']

        tv_series_count = db.execute_query('SELECT COUNT(*) as count FROM title_basics WHERE "titleType" = \'tvSeries\'')
        if tv_series_count:
            stats['tv_series'] = tv_series_count[0]['count']

        people_count = db.execute_query("SELECT COUNT(*) as count FROM name_basics")
        if people_count:
            stats['people'] = people_count[0]['count']
            
        ratings_count = db.execute_query("SELECT COUNT(*) as count FROM title_ratings")
        if ratings_count:
            stats['ratings'] = ratings_count[0]['count']
        
        # Get top rated movies
        top_movies = db.execute_query("""
            SELECT tb."tconst", tb."primaryTitle", tb."startYear", tr."averageRating", tr."numVotes"
            FROM title_basics tb
            JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."titleType" = 'movie' AND tr."numVotes" >= 1000
            ORDER BY tr."averageRating" DESC, tr."numVotes" DESC
            LIMIT 10        """)
        
        # Get recent releases
        recent_movies = db.execute_query("""
            SELECT tb."tconst", tb."primaryTitle", tb."startYear", tr."averageRating"
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."titleType" = 'movie' AND tb."startYear" >= EXTRACT(YEAR FROM CURRENT_DATE) - 2
            ORDER BY tb."startYear" DESC, tr."averageRating" DESC NULLS LAST
            LIMIT 8
        """)
        
        return render_template('home.html', 
                             stats=stats, 
                             top_movies=top_movies,
                             recent_movies=recent_movies)
    except Exception as e:
        print(f"Home page error: {e}")
        return render_template('home.html', stats={}, top_movies=[], recent_movies=[])

@app.route('/movies')
def movies():
    """Movies listing with filters and pagination"""
    try:
        # Get filter parameters
        genre = request.args.get('genre', '')
        year_from = request.args.get('year_from', '', type=str)
        year_to = request.args.get('year_to', '', type=str)
        min_rating = request.args.get('min_rating', '', type=str)
        sort_by = request.args.get('sort_by', 'rating_desc')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        # Build query conditions
        conditions = ["tb.\"titleType\" = 'movie'"]
        params = []
        
        if genre:
            conditions.append("tb.genres LIKE %s")
            params.append(f'%{genre}%')
        
        if year_from:
            conditions.append("tb.\"startYear\" >= %s")
            params.append(year_from)
        
        if year_to:
            conditions.append("tb.\"startYear\" <= %s")
            params.append(year_to)
        
        if min_rating:
            conditions.append("tr.\"averageRating\" >= %s")
            params.append(min_rating)
        
        # Sort options
        sort_options = {
            'rating_desc': 'tr."averageRating" DESC NULLS LAST',
            'rating_asc': 'tr."averageRating" ASC NULLS LAST',
            'name_asc': 'tb."primaryTitle" ASC',
            'name_desc': 'tb."primaryTitle" DESC',
            'year_desc': 'tb."startYear" DESC NULLS LAST',
            'year_asc': 'tb."startYear" ASC NULLS LAST',
        }
        order_by = sort_options.get(sort_by, 'tr."averageRating" DESC NULLS LAST')

        where_clause = " AND ".join(conditions)

        # Count total results
        count_query = f'''
            SELECT COUNT(*) as total
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE {where_clause}
        '''
        total_count = db.execute_query(count_query, params)[0]['total']

        # Get movies with pagination
        offset = (page - 1) * per_page
        movies_query = f"""
            SELECT tb."tconst", tb."primaryTitle", tb."startYear", tb."runtimeMinutes", 
                   tb."genres", tr."averageRating", tr."numVotes"
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """
        movies_list = db.execute_query(movies_query, params + [per_page, offset])

        # Get available genres for filter
        genres_query = """            SELECT DISTINCT TRIM(unnest(string_to_array(genres, ','))) as genre
            FROM title_basics 
            WHERE genres IS NOT NULL AND "titleType" = 'movie'
            ORDER BY genre
        """
        available_genres = [row['genre'] for row in db.execute_query(genres_query) if row['genre']]

        # Pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

        return render_template('movies.html',
                             movies=movies_list,
                             available_genres=available_genres,
                             current_filters={
                                 'genre': genre,
                                 'year_from': year_from,
                                 'year_to': year_to,
                                 'min_rating': min_rating,
                                 'sort_by': sort_by
                             },
                             pagination={
                                 'page': page,
                                 'per_page': per_page,
                                 'total_count': total_count,
                                 'total_pages': total_pages,
                                 'has_prev': has_prev,
                                 'has_next': has_next
                             })
    except Exception as e:
        print(f"Movies page error: {e}")
        flash('Error loading movies page.', 'error')
        return render_template('movies.html', movies=[], available_genres=[], 
                             current_filters={}, pagination={})

@app.route('/movie/<tconst>')
def movie_details(tconst):
    """Individual movie details page"""
    try:        # Get movie details
        movie_query = """
            SELECT tb.*, tr."averageRating", tr."numVotes"
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."tconst" = %s
        """
        
        movie = db.execute_query(movie_query, (tconst,))
        if not movie:
            flash('Movie not found.', 'error')
            return redirect(url_for('movies'))
        movie = movie[0]
        
        # Get cast and crew
        cast_query = """
            SELECT nb."nconst", nb."primaryName", tp.category, tp.characters
            FROM title_principals tp
            JOIN name_basics nb ON tp.nconst = nb.nconst
            WHERE tp.tconst = %s
            ORDER BY tp.ordering
            LIMIT 20
        """
        cast_crew = db.execute_query(cast_query, (tconst,))
        cast = [person for person in cast_crew if person['category'] in ['actor', 'actress']]
        crew = [person for person in cast_crew if person['category'] not in ['actor', 'actress']]
          # Get similar movies (same genre, similar rating)
        similar_movies = []
        if movie.get('genres'):
            genres = movie['genres'].split(',')
            if genres:
                genre_condition = " OR ".join([f"tb.genres LIKE %s" for g in genres])
                similar_query = f'''
                    SELECT tb."tconst", tb."primaryTitle", tb."startYear", tr."averageRating"
                    FROM title_basics tb
                    JOIN title_ratings tr ON tb."tconst" = tr."tconst"
                    WHERE tb."titleType" = \'movie\'
                      AND tb."tconst" != %s
                      AND ({genre_condition})
                    ORDER BY tr."averageRating" DESC, tr."numVotes" DESC
                    LIMIT 10
                '''
                params = [f'%{g}%' for g in genres]
                similar_movies = db.execute_query(similar_query, [tconst] + params)
        
        return render_template('movie_details.html',
                             movie=movie,
                             cast=cast,
                             crew=crew,
                             similar_movies=similar_movies)
                             
    except Exception as e:
        print(f"Movie details error: {e}")
        flash('Error loading movie details', 'error')
        return redirect(url_for('movies'))

@app.route('/series')
def series():
    """TV Series listing page"""
    try:
        # Get filter parameters
        genre = request.args.get('genre', '')
        year_from = request.args.get('year_from', '', type=str)
        year_to = request.args.get('year_to', '', type=str)
        min_rating = request.args.get('min_rating', '', type=str)
        sort_by = request.args.get('sort_by', 'rating_desc')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        # Build query conditions
        conditions = ['tb."titleType" = \'tvSeries\'']
        params = []
        
        if genre:
            conditions.append("tb.genres LIKE %s")
            params.append(f'%{genre}%')
        
        if year_from:
            conditions.append("tb.\"startYear\" >= %s")
            params.append(year_from)
        
        if year_to:
            conditions.append("tb.\"startYear\" <= %s")
            params.append(year_to)
        
        if min_rating:
            conditions.append("tr.\"averageRating\" >= %s")
            params.append(min_rating)
        # Sort options
        sort_options = {
            'rating_desc': 'tr."averageRating" DESC NULLS LAST',
            'rating_asc': 'tr."averageRating" ASC NULLS LAST',
            'name_asc': 'tb."primaryTitle" ASC',
            'name_desc': 'tb."primaryTitle" DESC',
            'year_desc': 'tb."startYear" DESC NULLS LAST',
            'year_asc': 'tb."startYear" ASC NULLS LAST',
        }
        order_by = sort_options.get(sort_by, 'tr."averageRating" DESC NULLS LAST')

        where_clause = " AND ".join(conditions)

        # Count total results
        count_query = f'''
            SELECT COUNT(*) as total
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE {where_clause}
        '''
        total_count = db.execute_query(count_query, params)[0]['total']

        # Get series with pagination
        offset = (page - 1) * per_page
        series_query = f"""
            SELECT tb."tconst", tb."primaryTitle", tb."startYear", tb."endYear",
                   tb."genres", tr."averageRating", tr."numVotes"
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """
        series_list = db.execute_query(series_query, params + [per_page, offset])
        
        # Get available genres for filter
        genres_query = """            SELECT DISTINCT TRIM(unnest(string_to_array(genres, ','))) as genre
            FROM title_basics 
            WHERE genres IS NOT NULL AND "titleType" = 'tvSeries'
            ORDER BY genre
        """
        available_genres = [row['genre'] for row in db.execute_query(genres_query) if row['genre']]

        # Pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

        return render_template('series.html',
                             series=series_list,
                             available_genres=available_genres,
                             current_filters={
                                 'genre': genre,
                                 'year_from': year_from,
                                 'year_to': year_to,
                                 'min_rating': min_rating,
                                 'sort_by': sort_by
                             },
                             pagination={
                                 'page': page,
                                 'per_page': per_page,
                                 'total_count': total_count,
                                 'total_pages': total_pages,
                                 'has_prev': has_prev,
                                 'has_next': has_next
                             })
    except Exception as e:
        print(f"Series page error: {e}")
        flash('Error loading TV series page.', 'error')
        return render_template('series.html', series=[], available_genres=[], 
                             current_filters={}, pagination={})

@app.route('/series/<tconst>')
def series_details(tconst):
    """Individual TV series details page"""
    try:        
        # Get series details
        series_query = '''
            SELECT tb.*, tr."averageRating", tr."numVotes"
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."tconst" = %s AND tb."titleType" = \'tvSeries\'
        '''
        series = db.execute_query(series_query, (tconst,))
        if not series:
            flash('TV Series not found.', 'error')
            return redirect(url_for('series'))
        series = series[0]

        # Get episodes
        episodes_query = '''
            SELECT te.*, tb."primaryTitle" as "episodeTitle", tb."startYear" as "episodeYear", tr."averageRating"
            FROM title_episode te
            JOIN title_basics tb ON te."tconst" = tb."tconst"
            LEFT JOIN title_ratings tr ON te."tconst" = tr."tconst"
            WHERE te."parentTConst" = %s
            ORDER BY te."seasonNumber", te."episodeNumber"
        '''
        episodes = db.execute_query(episodes_query, (tconst,))

        # Get cast and crew
        cast_query = '''
            SELECT nb."nconst", nb."primaryName", tp."category", tp."characters"
            FROM title_principals tp
            JOIN name_basics nb ON tp."nconst" = nb."nconst"
            WHERE tp."tconst" = %s
            ORDER BY tp."ordering"
            LIMIT 20
        '''
        cast_crew = db.execute_query(cast_query, (tconst,))
        cast = [p for p in cast_crew if p['category'] in ['actor', 'actress']]
        crew = [p for p in cast_crew if p['category'] not in ['actor', 'actress']]

        # Get similar series
        similar_series = []
        if series.get('genres'):
            genres = series['genres'].split(',')
            if genres:
                genre_condition = " OR ".join([f"tb.genres LIKE %s" for _ in genres])
                similar_query = f'''
                    SELECT tb."tconst", tb."primaryTitle", tb."startYear", tr."averageRating"
                    FROM title_basics tb
                    JOIN title_ratings tr ON tb."tconst" = tr."tconst"
                    WHERE tb."titleType" = \'tvSeries\'
                      AND tb."tconst" != %s
                      AND ({genre_condition})
                    ORDER BY tr."averageRating" DESC, tr."numVotes" DESC
                    LIMIT 10
                '''
                params = [f'%{g}%' for g in genres]
                similar_series = db.execute_query(similar_query, [tconst] + params)

        return render_template('series_details.html',
                             series=series,
                             episodes=episodes,
                             cast=cast,
                             crew=crew,
                             similar_series=similar_series)
    except Exception as e:
        print(f"Series details error: {e}")
        flash('Error loading series details.', 'error')
        return redirect(url_for('series'))

@app.route('/people')
def people():
    """People listing page"""
    try:
        # Get filter parameters
        profession = request.args.get('profession', '')
        birth_year_from = request.args.get('birth_year_from', '', type=str)
        birth_year_to = request.args.get('birth_year_to', '', type=str)
        sort_by = request.args.get('sort_by', 'name_asc')
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # Build query conditions
        conditions = []
        params = []

        if profession:
            conditions.append("nb.\"primaryProfession\" ILIKE %s")
            params.append(f'%{profession}%')

        if birth_year_from:
            conditions.append("nb.\"birthYear\" >= %s")
            params.append(birth_year_from)

        if birth_year_to:
            conditions.append("nb.\"birthYear\" <= %s")
            params.append(birth_year_to)

        # Sort options
        sort_options = {
            'name_asc': 'nb."primaryName" ASC',
            'name_desc': 'nb."primaryName" DESC',
            'birth_year_desc': 'nb."birthYear" DESC NULLS LAST',
            'birth_year_asc': 'nb."birthYear" ASC NULLS LAST',
        }
        order_by = sort_options.get(sort_by, 'nb."primaryName" ASC')

        # Build WHERE clause
        where_clause = ' AND '.join(conditions) if conditions else '1=1'

        # Count total results
        count_query = f'''
            SELECT COUNT(*) as total
            FROM name_basics nb
            WHERE {where_clause}
        '''
        total_count = db.execute_query(count_query, params)[0]['total']

        # Get people with pagination
        offset = (page - 1) * per_page
        people_query = f'''
            SELECT nb."nconst", nb."primaryName", nb."birthYear", nb."deathYear",
                   nb."primaryProfession", nb."knownForTitles"
            FROM name_basics nb
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        '''
        people_list = db.execute_query(people_query, params + [per_page, offset])
          # Get available professions for filter
        professions_query = '''
            SELECT DISTINCT TRIM(unnest(string_to_array("primaryProfession", ','))) as profession
            FROM name_basics 
            WHERE "primaryProfession" IS NOT NULL
            ORDER BY profession
        '''
        available_professions = [row['profession'] for row in db.execute_query(professions_query) if row['profession']]
        
        # Pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('people.html',
                             people=people_list,
                             available_professions=available_professions,
                             current_filters={
                                 'profession': profession,
                                 'birth_year_from': birth_year_from,
                                 'birth_year_to': birth_year_to,
                                 'sort_by': sort_by
                             },
                             pagination={
                                 'page': page,
                                 'per_page': per_page,
                                 'total_count': total_count,
                                 'total_pages': total_pages,
                                 'has_prev': has_prev,
                                 'has_next': has_next
                             })
    except Exception as e:
        print(f"People page error: {e}")
        return render_template('people.html', people=[], available_professions=[], 
                             current_filters={}, pagination={})

@app.route('/person/<nconst>')
def person_details(nconst):
    """Individual person details page"""
    try:
        # Get person details
        person_query = '''
            SELECT * FROM name_basics WHERE "nconst" = %s
        '''
        person = db.execute_query(person_query, (nconst,))
        if not person:
            flash('Person not found.', 'error')
            return redirect(url_for('people'))
        person = person[0]

        # Get filmography
        filmography_query = '''
            SELECT tb."tconst", tb."primaryTitle", tb."titleType", tb."startYear",
                   tp."category", tp."characters", tr."averageRating"
            FROM title_principals tp
            JOIN title_basics tb ON tp."tconst" = tb."tconst"
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tp."nconst" = %s
            ORDER BY tb."startYear" DESC NULLS LAST, tr."averageRating" DESC NULLS LAST
        '''
        filmography = db.execute_query(filmography_query, (nconst,))

        # Group by role
        roles = {}
        for work in filmography:
            category = work['category'].replace('_', ' ').title()
            if category not in roles:
                roles[category] = []
            roles[category].append(work)

        # Get statistics
        stats = {}
        if filmography:
            total_works = len(filmography)
            movies = len([w for w in filmography if w['titleType'] == 'movie'])
            tv_series = len([w for w in filmography if w['titleType'] == 'tvSeries'])
            
            ratings = [w['averageRating'] for w in filmography if w['averageRating']]
            avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
            
            years = [w['startYear'] for w in filmography if w['startYear']]
            career_span = f"{min(years)}–{max(years)}" if len(years) > 1 else str(years[0]) if years else "N/A"
            
            stats = {
                'total_works': total_works,
                'movies': movies,
                'tv_series': tv_series,
                'avg_rating': avg_rating,
                'career_span': career_span
            }

        return render_template('person_details.html',
                             person=person,
                             roles=roles,
                             stats=stats)
                             
    except Exception as e:
        print(f"Person details error: {e}")
        flash('Error loading person details', 'error')
        return redirect(url_for('people'))

@app.route('/search')
def search():
    """Universal search page"""
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')  # all, movies, series, people
        page = request.args.get('page', 1, type=int)
        per_page = 20

        results = {
            'movies': [],
            'series': [],
            'people': [],
            'query': query,
            'search_type': search_type,
            'total_count': 0
        }
        
        if not query:
            return render_template('search.html', results=results)

        offset = (page - 1) * per_page
        search_term = f'%{query}%'

        # Build queries based on search type
        queries = {}
        if search_type in ['all', 'movies']:
            queries['movies'] = {
                'count': '''
                    SELECT COUNT(*) as count FROM title_basics tb
                    WHERE tb."titleType" = \'movie\' AND (tb."primaryTitle" ILIKE %s OR tb."originalTitle" ILIKE %s)
                ''',
                'search': '''
                    SELECT tb."tconst", tb."primaryTitle", tb."startYear", tb."genres", tr."averageRating", tr."numVotes"
                    FROM title_basics tb
                    LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
                    WHERE tb."titleType" = \'movie\' AND (tb."primaryTitle" ILIKE %s OR tb."originalTitle" ILIKE %s)
                    ORDER BY tr."numVotes" DESC NULLS LAST, tr."averageRating" DESC NULLS LAST
                    LIMIT %s OFFSET %s
                '''
            }
        if search_type in ['all', 'series']:
            queries['series'] = {
                'count': '''
                    SELECT COUNT(*) as count FROM title_basics tb
                    WHERE tb."titleType" = \'tvSeries\' AND (tb."primaryTitle" ILIKE %s OR tb."originalTitle" ILIKE %s)
                ''',
                'search': '''
                    SELECT tb."tconst", tb."primaryTitle", tb."startYear", tb."endYear", tb."genres", tr."averageRating", tr."numVotes"
                    FROM title_basics tb
                    LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
                    WHERE tb."titleType" = \'tvSeries\' AND (tb."primaryTitle" ILIKE %s OR tb."originalTitle" ILIKE %s)
                    ORDER BY tr."numVotes" DESC NULLS LAST, tr."averageRating" DESC NULLS LAST
                    LIMIT %s OFFSET %s
                '''
            }
        if search_type in ['all', 'people']:
            queries['people'] = {
                'count': '''
                    SELECT COUNT(*) as count FROM name_basics nb WHERE nb."primaryName" ILIKE %s
                ''',
                'search': '''
                    SELECT nb."nconst", nb."primaryName", nb."birthYear", nb."primaryProfession"
                    FROM name_basics nb
                    WHERE nb."primaryName" ILIKE %s
                    ORDER BY nb."primaryName"
                    LIMIT %s OFFSET %s
                '''
            }

        # Execute queries
        total_count = 0
        for key, q in queries.items():
            if key == 'people':
                count_res = db.execute_query(q['count'], (search_term,))
                res = db.execute_query(q['search'], (search_term, per_page, offset))
            else:
                count_res = db.execute_query(q['count'], (search_term, search_term))
                res = db.execute_query(q['search'], (search_term, search_term, per_page, offset))
            
            if count_res:
                total_count += count_res[0]['count']
            results[key] = res
        
        results['total_count'] = total_count
        total_pages = (total_count + per_page - 1) // per_page
        
        return render_template('search.html', 
                             results=results,
                             pagination={
                                 'page': page,
                                 'per_page': per_page,
                                 'total_count': total_count,
                                 'total_pages': total_pages,
                                 'has_prev': page > 1,
                                 'has_next': page < total_pages
                             })

    except Exception as e:
        print(f"Search error: {e}")
        flash('An error occurred during the search.', 'error')
        return render_template('search.html', results={
            'movies': [], 'series': [], 'people': [],
            'query': request.args.get('q', ''), 'search_type': request.args.get('type', 'all')
        })

@app.route('/analysis')
def analysis():
    """Data analysis dashboard"""
    try:
        return render_template('analysis.html')
    except Exception as e:
        print(f"Analysis page error: {e}")
        flash('Could not load analysis page.', 'error')
        return render_template('analysis.html')

@app.route('/analysis/genre')
def genre_analysis():
    """Genre-based analysis page"""
    try:
        # Get genre popularity data
        genre_query = '''
            SELECT 
                TRIM(unnest(string_to_array(tb."genres", ','))) as genre,
                COUNT(*) as count,
                AVG(tr."averageRating") as avg_rating,
                SUM(tr."numVotes") as total_votes
            FROM title_basics tb
            JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."titleType" = \'movie\' AND tb."genres" IS NOT NULL AND tr."numVotes" > 1000
            GROUP BY genre
            HAVING COUNT(*) >= 100
            ORDER BY count DESC
            LIMIT 20
        '''
        genre_data = db.execute_query_pandas(genre_query)
        
        # Create Plotly visualizations
        plotly_charts = {}
        if not genre_data.empty:
            # Genre popularity chart
            fig1 = px.bar(genre_data, x='genre', y='count', 
                         title='Movie Count by Genre (Top 20)',
                         labels={'count': 'Number of Movies', 'genre': 'Genre'})
            fig1.update_layout(xaxis_tickangle=-45)
            plotly_charts['popularity'] = json.dumps(fig1, cls=PlotlyJSONEncoder)
            
            # Genre ratings chart
            fig2 = px.scatter(genre_data, x='count', y='avg_rating', 
                            size='total_votes', color='genre', hover_name='genre',
                            title='Genre Analysis: Ratings vs. Popularity',
                            labels={'count': 'Number of Movies', 'avg_rating': 'Average Rating'})
            plotly_charts['ratings'] = json.dumps(fig2, cls=PlotlyJSONEncoder)
        
        return render_template('genre_analysis.html', 
                             genre_data=genre_data.to_dict('records'),
                             plotly_charts=plotly_charts)
        
    except Exception as e:
        print(f"Genre analysis error: {e}")
        flash('Error generating genre analysis.', 'error')
        return render_template('genre_analysis.html', 
                             genre_data=[], plotly_charts={})

@app.route('/analysis/rating-trends')
def rating_trends():
    """Rating trends over time analysis"""
    try:        
        # Get yearly rating trends
        trends_query = '''
            SELECT 
                tb."startYear",
                COUNT(*) as movie_count,
                AVG(tr."averageRating") as avg_rating,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tr."averageRating") as median_rating,
                SUM(tr."numVotes") as total_votes
            FROM title_basics tb
            JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."titleType" = \'movie\' 
              AND tb."startYear" BETWEEN 1960 AND EXTRACT(YEAR FROM CURRENT_DATE) - 1
              AND tr."numVotes" >= 500
            GROUP BY tb."startYear"
            HAVING COUNT(*) >= 20
            ORDER BY tb."startYear"
        '''
        trends_data = db.execute_query_pandas(trends_query)
        
        plotly_chart = None
        if not trends_data.empty:
            # Create interactive time series plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trends_data['startYear'], y=trends_data['avg_rating'],
                mode='lines+markers', name='Average Rating',
                line=dict(color='royalblue', width=2),
                hovertemplate='Year: %{x}<br>Avg Rating: %{y:.2f}<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=trends_data['startYear'], y=trends_data['median_rating'],
                mode='lines+markers', name='Median Rating',
                line=dict(color='firebrick', width=2, dash='dash'),
                hovertemplate='Year: %{x}<br>Median Rating: %{y:.2f}<extra></extra>'
            ))
            fig.update_layout(
                title='Movie Rating Trends Over Time (1960-Present)',
                xaxis_title='Year', yaxis_title='Rating',
                hovermode='x unified', legend=dict(x=0.01, y=0.98),
                height=500
            )
            plotly_chart = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return render_template('rating_trends.html',
                             data=trends_data.to_dict('records'),
                             plotly_chart=plotly_chart)
        
    except Exception as e:
        print(f"Rating trends analysis error: {e}")
        flash('Error generating rating trends analysis.', 'error')
        return render_template('rating_trends.html', data=[], plotly_chart=None)

# API endpoints for AJAX requests
@app.route('/api/search/autocomplete')
def search_autocomplete():
    """Autocomplete API for search"""
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify([])
        
        search_term = f'%{query}%'
        autocomplete_query = '''
            (SELECT 'movie' as type, "tconst" as id, "primaryTitle" as title, "startYear" as year
             FROM title_basics 
             WHERE "titleType" = \'movie\' AND "primaryTitle" ILIKE %s
             ORDER BY "primaryTitle" LIMIT 5)
            UNION ALL
            (SELECT 'series' as type, "tconst" as id, "primaryTitle" as title, "startYear" as year
             FROM title_basics 
             WHERE "titleType" = \'tvSeries\' AND "primaryTitle" ILIKE %s
             ORDER BY "primaryTitle" LIMIT 5)
            UNION ALL
            (SELECT 'person' as type, "nconst" as id, "primaryName" as title, "birthYear" as year
             FROM name_basics 
             WHERE "primaryName" ILIKE %s
             ORDER BY "primaryName" LIMIT 5)
        '''
        
        suggestions = db.execute_query(autocomplete_query, (search_term, search_term, search_term))
        return jsonify(suggestions)
        
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return jsonify([])

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    try:        
        stats = {
            'movies': db.execute_query('SELECT COUNT(*) as count FROM title_basics WHERE "titleType" = \'movie\'')[0]['count'],
            'tv_series': db.execute_query('SELECT COUNT(*) as count FROM title_basics WHERE "titleType" = \'tvSeries\'')[0]['count'],
            'people': db.execute_query("SELECT COUNT(*) as count FROM name_basics")[0]['count'],
            'ratings': db.execute_query("SELECT COUNT(*) as count FROM title_ratings")[0]['count']
        }
        return jsonify(stats)
    except Exception as e:
        print(f"API stats error: {e}")
        return jsonify({'error': 'Unable to fetch statistics'}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    print(f"Server Error: {e}") # Log the error for debugging
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)
