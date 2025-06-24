"""
🚀 Simple IMDb Clone Flask Application
Optimized for performance with your existing database
"""
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'imdb-clone-secret-key'

# Database connection with optimizations
def get_db_connection():
    conn = sqlite3.connect('imdb.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # SQLite performance optimizations
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA cache_size=10000')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA synchronous=NORMAL')
    return conn

def execute_query(query, params=None):
    """Execute query and return results as list of dicts"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@app.route('/', endpoint='home')
def home():
    """Home page with statistics and top movies"""
    try:
        # Get database statistics
        stats = {}
        
        # Movie count
        movie_count = execute_query('SELECT COUNT(*) as count FROM title_basics WHERE titleType = "movie"')
        stats['movies'] = movie_count[0]['count'] if movie_count else 0
        
        # TV Series count
        tv_count = execute_query('SELECT COUNT(*) as count FROM title_basics WHERE titleType = "tvSeries"')
        stats['tv_series'] = tv_count[0]['count'] if tv_count else 0
        
        # People count
        people_count = execute_query('SELECT COUNT(*) as count FROM name_basics')
        stats['people'] = people_count[0]['count'] if people_count else 0
        
        # Ratings count
        ratings_count = execute_query('SELECT COUNT(*) as count FROM title_ratings')
        stats['ratings'] = ratings_count[0]['count'] if ratings_count else 0
        
        # Get top rated movies
        top_movies = execute_query("""
            SELECT tb.tconst, tb.primaryTitle, tb.startYear, tr.averageRating, tr.numVotes
            FROM title_basics tb
            JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titleType = 'movie' AND tr.numVotes >= 1000
            ORDER BY tr.averageRating DESC, tr.numVotes DESC
            LIMIT 10
        """)
        
        return render_template('home.html', stats=stats, top_movies=top_movies)
        
    except Exception as e:
        print(f"Error in home route: {e}")
        return render_template('home.html', stats={}, top_movies=[])

@app.route('/movies', endpoint='movies')
def movies():
    """Movies listing with pagination and filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        
        # Filters
        genre = request.args.get('genre')
        year = request.args.get('year')
        min_rating = request.args.get('min_rating')
        is_adult = request.args.get('adult')
        
        # Base query
        query = """
            SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.runtimeMinutes, 
                   tb.genres, tr.averageRating, tr.numVotes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titleType = 'movie'
        """
        params = []
        
        # Apply filters
        if genre:
            query += ' AND tb.genres LIKE ?'
            params.append(f'%{genre}%')
        if year:
            query += ' AND tb.startYear = ?'
            params.append(year)
        if min_rating:
            query += ' AND tr.averageRating >= ?'
            params.append(min_rating)
        if is_adult:
            query += ' AND tb.isAdult = ?'
            params.append(is_adult)
        
        # Pagination
        query += ' ORDER BY tr.averageRating DESC, tr.numVotes DESC LIMIT ? OFFSET ?'
        params += [per_page, offset]
        
        # Execute query
        movies = execute_query(query, params)
        
        # Get total count for pagination
        total_count = execute_query('SELECT COUNT(*) as count FROM title_basics WHERE titleType = "movie"')
        total = total_count[0]['count'] if total_count else 0
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'has_prev': page > 1,
            'has_next': (page * per_page) < total,
            'prev_num': page - 1 if page > 1 else None,
            'next_num': page + 1 if (page * per_page) < total else None
        }
        
        return render_template('movies.html', movies=movies, pagination=pagination)
        
    except Exception as e:
        print(f"Error in movies route: {e}")
        return render_template('movies.html', movies=[], pagination={})

@app.route('/movie/<tconst>', endpoint='movie_details')
def movie_details(tconst):
    """Individual movie details"""
    try:
        # Get movie details
        movie = execute_query("""
            SELECT tb.*, tr.averageRating, tr.numVotes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.tconst = ?
        """, (tconst,))
        
        if not movie:
            return "Movie not found", 404
            
        movie = movie[0]
        
        # Get cast and crew
        cast_crew = execute_query("""
            SELECT nb.nconst, nb.primaryName, tp.category, tp.characters, tp.job
            FROM title_principals tp
            JOIN name_basics nb ON tp.nconst = nb.nconst
            WHERE tp.tconst = ?
            ORDER BY tp.ordering
            LIMIT 20
        """, (tconst,))
        
        # Get alternative titles
        alt_titles = execute_query("""
            SELECT *
            FROM title_akas
            WHERE titleId = ?
        """, (tconst,))
        
        return render_template('movie_details.html', movie=movie, cast_crew=cast_crew, alt_titles=alt_titles)
        
    except Exception as e:
        print(f"Error in movie details route: {e}")
        return "Error loading movie details", 500

@app.route('/person/<nconst>', endpoint='person')
def person(nconst):
    """Person (actor/director) details and filmography"""
    try:
        # Get person details
        person = execute_query("""
            SELECT *
            FROM name_basics
            WHERE nconst = ?
        """, (nconst,))
        
        if not person:
            return "Person not found", 404
            
        person = person[0]
        
        # Get filmography
        filmography = execute_query("""
            SELECT tb.primaryTitle, tb.startYear, tp.category, tp.job, tp.characters
            FROM title_principals tp
            JOIN title_basics tb ON tp.tconst = tb.tconst
            WHERE tp.nconst = ?
            ORDER BY tb.startYear DESC
        """, (nconst,))
        
        return render_template('person.html', person=person, filmography=filmography)
        
    except Exception as e:
        print(f"Error in person route: {e}")
        return "Error loading person details", 500

@app.route('/search', endpoint='search')
def search():
    """Search functionality"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return render_template('search.html', results=[], query='')
        
        search_term = f'%{query}%'
        
        # Search movies
        movies = execute_query("""
            SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.titleType,
                   tr.averageRating, tr.numVotes, 'movie' as result_type
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.primaryTitle LIKE ? AND tb.titleType IN ('movie', 'tvSeries')
            ORDER BY COALESCE(tr.numVotes, 0) DESC
            LIMIT 20
        """, (search_term,))
        
        # Search people
        people = execute_query("""
            SELECT nb.nconst, nb.primaryName, nb.birthYear, nb.primaryProfession,
                   'person' as result_type
            FROM name_basics nb
            WHERE nb.primaryName LIKE ?
            ORDER BY nb.primaryName
            LIMIT 10
        """, (search_term,))
        
        results = movies + people
        
        return render_template('search.html', results=results, query=query)
        
    except Exception as e:
        print(f"Error in search route: {e}")
        return render_template('search.html', results=[], query=request.args.get('q', ''))

@app.route('/analysis', endpoint='analysis')
def analysis():
    """Data analysis dashboard"""
    try:
        # Get rating trends by year
        trends = execute_query("""
            SELECT tb.startYear, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
            FROM title_basics tb
            JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titleType = 'movie' AND tb.startYear BETWEEN 1980 AND 2023
                AND tr.numVotes >= 100
            GROUP BY tb.startYear
            HAVING COUNT(*) >= 10
            ORDER BY tb.startYear
        """)
        
        # Get genre popularity
        genre_data = execute_query("""
            SELECT 
                CASE 
                    WHEN genres LIKE '%Action%' THEN 'Action'
                    WHEN genres LIKE '%Drama%' THEN 'Drama'
                    WHEN genres LIKE '%Comedy%' THEN 'Comedy'
                    WHEN genres LIKE '%Thriller%' THEN 'Thriller'
                    WHEN genres LIKE '%Horror%' THEN 'Horror'
                    WHEN genres LIKE '%Romance%' THEN 'Romance'
                    ELSE 'Other'
                END as genre,
                COUNT(*) as count,
                AVG(tr.averageRating) as avg_rating
            FROM title_basics tb
            JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titleType = 'movie' AND tr.numVotes >= 1000
            GROUP BY genre
            ORDER BY count DESC
            LIMIT 10
        """)
        
        # Get top directors
        top_directors = execute_query("""
            SELECT nb.primaryName, COUNT(*) as movie_count, AVG(tr.averageRating) as avg_rating
            FROM name_basics nb
            JOIN title_principals tp ON nb.nconst = tp.nconst AND tp.category = "director"
            JOIN title_basics tb ON tp.tconst = tb.tconst AND tb.titleType = "movie"
            JOIN title_ratings tr ON tb.tconst = tr.tconst
            GROUP BY nb.primaryName
            HAVING movie_count >= 3
            ORDER BY avg_rating DESC, movie_count DESC
            LIMIT 10
        """)
        
        # Get top collaborators (actors)
        top_collaborators = execute_query("""
            SELECT a1.primaryName as actor1, a2.primaryName as actor2, COUNT(*) as movies_together
            FROM title_principals tp1
            JOIN title_principals tp2 ON tp1.tconst = tp2.tconst AND tp1.nconst < tp2.nconst
            JOIN name_basics a1 ON tp1.nconst = a1.nconst AND tp1.category IN ("actor","actress")
            JOIN name_basics a2 ON tp2.nconst = a2.nconst AND tp2.category IN ("actor","actress")
            WHERE tp1.category IN ("actor","actress") AND tp2.category IN ("actor","actress")
            GROUP BY actor1, actor2
            HAVING movies_together >= 3
            ORDER BY movies_together DESC, actor1, actor2
            LIMIT 10
        """)
        
        return render_template('analysis.html', trends=trends, genres=genre_data, top_directors=top_directors, top_collaborators=top_collaborators)
        
    except Exception as e:
        print(f"Error in analysis route: {e}")
        return render_template('analysis.html', trends=[], genres=[], top_directors=[], top_collaborators=[])

# API endpoints for AJAX
@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        stats = {}
        
        # Get basic counts
        movie_count = execute_query('SELECT COUNT(*) as count FROM title_basics WHERE titleType = "movie"')
        stats['movies'] = movie_count[0]['count'] if movie_count else 0
        
        tv_count = execute_query('SELECT COUNT(*) as count FROM title_basics WHERE titleType = "tvSeries"')
        stats['tv_series'] = tv_count[0]['count'] if tv_count else 0
        
        people_count = execute_query('SELECT COUNT(*) as count FROM name_basics')
        stats['people'] = people_count[0]['count'] if people_count else 0
        
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error in API stats: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🎬 IMDb Clone Flask Application")
    print("📂 Main file: simple_app.py")
    print("🗂️ Pages: Home, Movie Listing, Movie Details, Person, Analysis/Dashboard")
    print("💡 Features: Search (title/person), adult content filtering, advanced person-to-person search, data analysis dashboard, top collaborators")
    print("🌐 Open in your browser: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server.")
    app.run(debug=True, host='0.0.0.0', port=5000)
