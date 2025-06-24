"""
🚀 ULTRA-OPTIMIZED IMDb Clone - Flask Web Application
Complete optimized application with lightning-fast database operations
"""
import os
import io
import json
import base64
import warnings
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from plotly.utils import PlotlyJSONEncoder
from datetime import datetime
from optimized_database import OptimizedDatabaseManager, OptimizedQueries
import time
warnings.filterwarnings('ignore')

# Configure matplotlib for web deployment
plt.switch_backend('Agg')
matplotlib.use('Agg')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-imdb-clone-2025')

# 🚀 OPTIMIZED DATABASE INITIALIZATION
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

# Performance monitoring decorator
def monitor_performance(route_name):
    """Decorator to monitor route performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
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

# =====================
# MAIN ROUTES
# =====================

@app.route('/')
@monitor_performance('home')
def home():
    """🏠 Ultra-fast home page with cached statistics"""
    try:
        # Get cached dashboard statistics
        stats_data = db.execute_query(queries.DASHBOARD_STATS, use_cache=True)
        
        # Convert to dictionary for easy access
        stats = {}
        for row in stats_data:
            stats[row['type']] = row['count']
        
        # Get featured movies (top rated with enough votes)
        featured_movies = db.execute_query("""
            SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.genres, tr.averageRating, tr.numVotes
            FROM title_basics tb
            JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titleType = 'movie' AND tr.numVotes >= 10000
            ORDER BY tr.averageRating DESC, tr.numVotes DESC
            LIMIT 12
        """, use_cache=True)
        
        # Get recent releases
        current_year = datetime.now().year
        recent_releases = db.execute_query("""
            SELECT tb.tconst, tb.primaryTitle, tb.startYear, tr.averageRating, tr.numVotes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titleType = 'movie' AND tb.startYear >= ? - 3
            ORDER BY tb.startYear DESC, tr.numVotes DESC
            LIMIT 8
        """, (current_year,), use_cache=True)
        
        return render_template('home.html',
                             stats=stats,
                             featured_movies=featured_movies,
                             recent_releases=recent_releases)
        
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return render_template('home.html',
                             stats={'movies': 0, 'tv_series': 0, 'people': 0, 'ratings': 0},
                             featured_movies=[],
                             recent_releases=[])

@app.route('/movies')
@monitor_performance('movies')
def movies():
    """🎬 Lightning-fast movies listing with advanced filters"""
    try:
        # Get filter parameters
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, int(request.args.get('per_page', 24)))
        offset = (page - 1) * per_page
        
        # Filters
        year_min = request.args.get('year_min', type=int)
        year_max = request.args.get('year_max', type=int)
        genre = request.args.get('genre', '')
        min_rating = request.args.get('min_rating', type=float)
        sort_by = request.args.get('sort', 'popularity')
        
        # Use optimized query
        movies_data = db.execute_query(
            queries.POPULAR_MOVIES,
            (year_min, year_min, year_max, year_max, genre, genre, per_page, offset)
        )
        
        # Get total count for pagination (cached)
        total_count = db.execute_query("""
            SELECT COUNT(*) as count
            FROM title_basics tb
            WHERE tb.titleType = 'movie'
        """, use_cache=True)[0]['count']
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return render_template('movies.html',
                             movies=movies_data,
                             page=page,
                             total_pages=total_pages,
                             total_count=total_count,
                             filters={
                                 'year_min': year_min,
                                 'year_max': year_max,
                                 'genre': genre,
                                 'min_rating': min_rating,
                                 'sort': sort_by
                             })
        
    except Exception as e:
        print(f"❌ Movies page error: {e}")
        return render_template('movies.html', movies=[], page=1, total_pages=1, 
                             total_count=0, filters={})

@app.route('/movie/<tconst>')
@monitor_performance('movie_details')
def movie_details(tconst):
    """🎭 Ultra-fast movie details with optimized queries"""
    try:
        # Get movie details (cached)
        movie_data = db.execute_query(queries.MOVIE_DETAILS, (tconst,))
        if not movie_data:
            flash('Movie not found.', 'error')
            return redirect(url_for('movies'))
        
        movie = movie_data[0]
        
        # Get cast (cached)
        cast_data = db.execute_query(queries.MOVIE_CAST, (tconst,))
        
        # Get crew
        crew_data = db.execute_query("""
            SELECT nb.nconst, nb.primaryName, tp.category, tp.job
            FROM title_principals tp
            JOIN name_basics nb ON tp.nconst = nb.nconst
            WHERE tp.tconst = ? AND tp.category IN ('director', 'writer', 'producer')
            ORDER BY 
                CASE tp.category 
                    WHEN 'director' THEN 1
                    WHEN 'writer' THEN 2
                    WHEN 'producer' THEN 3
                    ELSE 4 
                END,
                tp.ordering
            LIMIT 20
        """, (tconst,))
        
        # Get similar movies
        similar_movies = []
        if movie.get('genres'):
            main_genre = movie['genres'].split(',')[0] if ',' in movie['genres'] else movie['genres']
            similar_movies = db.execute_query("""
                SELECT tb.tconst, tb.primaryTitle, tb.startYear, tr.averageRating
                FROM title_basics tb
                JOIN title_ratings tr ON tb.tconst = tr.tconst
                WHERE tb.titleType = 'movie' 
                  AND tb.tconst != ?
                  AND tb.genres LIKE '%' || ? || '%'
                  AND tr.numVotes >= 1000
                ORDER BY tr.averageRating DESC
                LIMIT 6
            """, (tconst, main_genre), use_cache=True)
        
        return render_template('movie_details.html',
                             movie=movie,
                             cast=cast_data,
                             crew=crew_data,
                             similar_movies=similar_movies)
        
    except Exception as e:
        print(f"❌ Movie details error: {e}")
        flash('Error loading movie details.', 'error')
        return redirect(url_for('movies'))

@app.route('/series')
@monitor_performance('series')
def series():
    """📺 TV Series listing page"""
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(50, int(request.args.get('per_page', 24)))
        offset = (page - 1) * per_page
        
        series_data = db.execute_query("""
            SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.endYear, tr.averageRating, tr.numVotes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titleType = 'tvSeries'
            ORDER BY tr.numVotes DESC, tr.averageRating DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        
        return render_template('series.html', series=series_data, page=page)
        
    except Exception as e:
        print(f"❌ Series page error: {e}")
        return render_template('series.html', series=[], page=1)

@app.route('/person/<nconst>')
@monitor_performance('person_details')
def person_details(nconst):
    """👤 Person details with filmography"""
    try:
        # Get person info
        person_data = db.execute_query("""
            SELECT nconst, primaryName, birthYear, deathYear, primaryProfession
            FROM name_basics
            WHERE nconst = ?
        """, (nconst,))
        
        if not person_data:
            flash('Person not found.', 'error')
            return redirect(url_for('people'))
        
        person = person_data[0]
        
        # Get filmography
        filmography = db.execute_query(queries.PERSON_FILMOGRAPHY, (nconst,))
        
        return render_template('person_details.html', person=person, filmography=filmography)
        
    except Exception as e:
        print(f"❌ Person details error: {e}")
        return redirect(url_for('people'))

@app.route('/search')
@monitor_performance('search')
def search():
    """🔍 Universal search page"""
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')
        
        if not query:
            return render_template('search.html', results=[], query='')
        
        if len(query) < 2:
            flash('Search query must be at least 2 characters.', 'warning')
            return render_template('search.html', results=[], query=query)
        
        results = []
        
        if search_type in ['all', 'movies']:
            # Search movies
            movie_results = db.execute_query(
                queries.MOVIE_SEARCH,
                (query, query, query, query, query, 20)
            )
            for movie in movie_results:
                movie['result_type'] = 'movie'
            results.extend(movie_results)
        
        if search_type in ['all', 'people']:
            # Search people
            people_results = db.execute_query("""
                SELECT nconst, primaryName, birthYear, primaryProfession,
                       'person' as result_type
                FROM name_basics
                WHERE primaryName LIKE '%' || ? || '%'
                ORDER BY primaryName
                LIMIT 10
            """, (query,))
            results.extend(people_results)
        
        return render_template('search.html', results=results, query=query, search_type=search_type)
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return render_template('search.html', results=[], query='')

# =====================
# ANALYTICS ROUTES
# =====================

@app.route('/analysis')
@monitor_performance('analysis')
def analysis():
    """📊 Data analysis dashboard"""
    try:
        # Get basic statistics
        stats = db.execute_query(queries.DASHBOARD_STATS, use_cache=True)
        
        # Genre analysis
        genre_data = db.execute_query(queries.GENRE_ANALYSIS, use_cache=True)
        
        # Create visualizations
        plotly_charts = {}
        
        if genre_data:
            # Genre distribution chart
            fig = px.bar(
                genre_data[:15], 
                x='genre', 
                y='movie_count',
                title='Movies by Genre',
                color='avg_rating',
                color_continuous_scale='viridis'
            )
            plotly_charts['genre_chart'] = json.dumps(fig, cls=PlotlyJSONEncoder)
        
        return render_template('analysis.html', stats=stats, genre_data=genre_data, 
                             plotly_charts=plotly_charts)
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return render_template('analysis.html', stats=[], genre_data=[], plotly_charts={})

# =====================
# API ENDPOINTS
# =====================

@app.route('/api/search/autocomplete')
def search_autocomplete():
    """🔍 Lightning-fast autocomplete API"""
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify([])
        
        suggestions = db.execute_query("""
            (SELECT 'movie' as type, tconst as id, primaryTitle as title, startYear as year
             FROM title_basics 
             WHERE titleType = 'movie' AND primaryTitle LIKE ? || '%'
             ORDER BY primaryTitle LIMIT 5)
            UNION ALL
            (SELECT 'person' as type, nconst as id, primaryName as title, birthYear as year
             FROM name_basics 
             WHERE primaryName LIKE ? || '%'
             ORDER BY primaryName LIMIT 5)
        """, (query, query), use_cache=True)
        
        return jsonify(suggestions)
        
    except Exception as e:
        print(f"❌ Autocomplete error: {e}")
        return jsonify([])

@app.route('/api/stats')
def api_stats():
    """📊 API endpoint for dashboard statistics"""
    try:
        stats_data = db.execute_query(queries.DASHBOARD_STATS, use_cache=True)
        stats = {row['type']: row['count'] for row in stats_data}
        return jsonify(stats)
    except Exception as e:
        print(f"❌ API stats error: {e}")
        return jsonify({'error': 'Unable to fetch statistics'}), 500

@app.route('/api/performance')
def api_performance():
    """⚡ Database performance statistics"""
    try:
        db_stats = db.get_stats()
        return jsonify(db_stats)
    except Exception as e:
        print(f"❌ Performance API error: {e}")
        return jsonify({'error': 'Unable to fetch performance stats'}), 500

# =====================
# ERROR HANDLERS
# =====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    print(f"Server Error: {e}")
    return render_template('500.html'), 500

# =====================
# UTILITY ROUTES
# =====================

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        test_result = db.execute_query("SELECT 1 as test")
        if test_result:
            return jsonify({'status': 'healthy', 'database': 'connected'})
        else:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/cache/clear')
def clear_cache():
    """Clear query cache (for development)"""
    try:
        db.clear_cache()
        flash('Cache cleared successfully!', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error clearing cache: {e}', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    print("🚀 Starting Ultra-Optimized IMDB Clone")
    print("=" * 50)
    print(f"Database: {db_type.upper()}")
    print(f"Debug mode: {app.debug}")
    print("🌐 Open: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
