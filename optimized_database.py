"""
🚀 ULTRA-OPTIMIZED DATABASE MANAGER
High-performance database operations for IMDB Clone application
"""
import sqlite3
import psycopg2
import pandas as pd
import time
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from psycopg2.extras import RealDictCursor
import concurrent.futures
from threading import Lock

class OptimizedDatabaseManager:
    """
    High-performance database manager with connection pooling,
    query optimization, and intelligent caching
    """
    
    def __init__(self, db_type="sqlite", **config):
        self.db_type = db_type
        self.config = config
        self.connection_pool = []
        self.pool_lock = Lock()
        self.query_cache = {}
        self.cache_lock = Lock()
        
        # Performance settings
        self.max_connections = 10
        self.cache_size = 1000
        self.enable_cache = True
        
        self._initialize_connection_pool()
    
    def _initialize_connection_pool(self):
        """Initialize connection pool for better performance"""
        print("🔥 Initializing optimized connection pool...")
        
        for _ in range(min(5, self.max_connections)):  # Start with 5 connections
            conn = self._create_connection()
            if conn:
                self.connection_pool.append(conn)
        
        print(f"✅ Connection pool initialized with {len(self.connection_pool)} connections")
    
    def _create_connection(self):
        """Create a new database connection with optimizations"""
        try:
            if self.db_type == "sqlite":
                conn = sqlite3.connect(
                    self.config.get('database', 'imdb.db'),
                    check_same_thread=False,
                    timeout=30.0
                )
                
                # SQLite performance optimizations
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA cache_size = 10000")
                conn.execute("PRAGMA temp_store = MEMORY")
                conn.execute("PRAGMA mmap_size = 268435456")  # 256MB
                conn.execute("PRAGMA optimize")
                
                return conn
                
            elif self.db_type == "postgresql":
                conn = psycopg2.connect(**self.config)
                conn.autocommit = True
                return conn
                
        except Exception as e:
            print(f"❌ Connection creation failed: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic return"""
        conn = None
        try:
            with self.pool_lock:
                if self.connection_pool:
                    conn = self.connection_pool.pop()
                else:
                    conn = self._create_connection()
            
            if conn:
                yield conn
            else:
                raise Exception("No database connection available")
                
        finally:
            if conn:
                with self.pool_lock:
                    if len(self.connection_pool) < self.max_connections:
                        self.connection_pool.append(conn)
                    else:
                        conn.close()
    
    def execute_query(self, query: str, params: tuple = None, use_cache: bool = True) -> List[Dict]:
        """
        Execute query with intelligent caching and optimization
        """
        # Generate cache key
        cache_key = f"{query}:{str(params)}" if params else query
        
        # Check cache first
        if use_cache and self.enable_cache:
            with self.cache_lock:
                if cache_key in self.query_cache:
                    return self.query_cache[cache_key]
        
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                if self.db_type == "sqlite":
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute(query, params or ())
                    results = [dict(row) for row in cursor.fetchall()]
                    
                else:  # PostgreSQL
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(query, params)
                        results = [dict(row) for row in cursor.fetchall()]
                
                execution_time = time.time() - start_time
                
                # Cache results if query is fast and cacheable
                if use_cache and execution_time < 2.0 and len(results) < 10000:
                    with self.cache_lock:
                        if len(self.query_cache) >= self.cache_size:
                            # Remove oldest entries
                            keys = list(self.query_cache.keys())
                            for key in keys[:len(keys)//2]:
                                del self.query_cache[key]
                        
                        self.query_cache[cache_key] = results
                
                print(f"⚡ Query executed in {execution_time:.3f}s")
                return results
                
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            return []
    
    def execute_query_pandas(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute query and return pandas DataFrame with optimizations"""
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
                
        except Exception as e:
            print(f"❌ Pandas query error: {e}")
            return pd.DataFrame()
    
    def execute_batch_insert(self, table: str, data: List[Dict], batch_size: int = 1000):
        """High-performance batch insert with chunking"""
        if not data:
            return
        
        start_time = time.time()
        total_rows = len(data)
        
        try:
            with self.get_connection() as conn:
                if self.db_type == "sqlite":
                    conn.execute("BEGIN TRANSACTION")
                
                # Get column names from first row
                columns = list(data[0].keys())
                placeholders = ', '.join(['?' if self.db_type == "sqlite" else '%s'] * len(columns))
                
                insert_query = f"""
                    INSERT INTO {table} ({', '.join(columns)}) 
                    VALUES ({placeholders})
                """
                
                cursor = conn.cursor()
                
                # Process in batches
                for i in range(0, total_rows, batch_size):
                    batch = data[i:i + batch_size]
                    batch_values = [tuple(row[col] for col in columns) for row in batch]
                    
                    if self.db_type == "sqlite":
                        cursor.executemany(insert_query, batch_values)
                    else:
                        from psycopg2.extras import execute_batch
                        execute_batch(cursor, insert_query, batch_values, page_size=batch_size)
                
                if self.db_type == "sqlite":
                    conn.execute("COMMIT")
                
                execution_time = time.time() - start_time
                print(f"🚀 Inserted {total_rows:,} rows in {execution_time:.2f}s ({total_rows/execution_time:.0f} rows/sec)")
                
        except Exception as e:
            print(f"❌ Batch insert error: {e}")
            if self.db_type == "sqlite":
                conn.execute("ROLLBACK")
    
    def clear_cache(self):
        """Clear query cache"""
        with self.cache_lock:
            self.query_cache.clear()
        print("🗑️ Query cache cleared")
    
    def get_stats(self) -> Dict:
        """Get database and performance statistics"""
        with self.cache_lock:
            cache_size = len(self.query_cache)
        
        with self.pool_lock:
            pool_size = len(self.connection_pool)
        
        return {
            'connection_pool_size': pool_size,
            'cache_entries': cache_size,
            'db_type': self.db_type
        }

# =======================
# OPTIMIZED QUERY LIBRARY
# =======================

class OptimizedQueries:
    """Pre-compiled optimized queries for maximum performance"""
    
    # Ultra-fast movie search with ranking
    MOVIE_SEARCH = """
        SELECT 
            tb.tconst,
            tb.primaryTitle,
            tb.startYear,
            tb.genres,
            tr.averageRating,
            tr.numVotes,
            -- Relevance scoring
            CASE 
                WHEN tb.primaryTitle = ? THEN 100
                WHEN tb.primaryTitle LIKE ? || '%' THEN 90
                WHEN tb.primaryTitle LIKE '%' || ? || '%' THEN 80
                ELSE 70
            END as relevance_score
        FROM title_basics tb
        LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
        WHERE tb.titleType = 'movie'
          AND (tb.primaryTitle LIKE '%' || ? || '%' OR tb.originalTitle LIKE '%' || ? || '%')
        ORDER BY relevance_score DESC, tr.numVotes DESC
        LIMIT ?
    """
    
    # Lightning-fast popular movies
    POPULAR_MOVIES = """
        SELECT 
            tb.tconst,
            tb.primaryTitle,
            tb.startYear,
            tb.genres,
            tr.averageRating,
            tr.numVotes
        FROM title_basics tb
        JOIN title_ratings tr ON tb.tconst = tr.tconst
        WHERE tb.titleType = 'movie'
          AND tr.numVotes >= 1000
          AND (? IS NULL OR tb.startYear >= ?)
          AND (? IS NULL OR tb.startYear <= ?)
          AND (? IS NULL OR tb.genres LIKE '%' || ? || '%')
        ORDER BY tr.averageRating DESC, tr.numVotes DESC
        LIMIT ? OFFSET ?
    """
    
    # Optimized movie details with cast
    MOVIE_DETAILS = """
        SELECT 
            tb.tconst,
            tb.primaryTitle,
            tb.originalTitle,
            tb.startYear,
            tb.runtimeMinutes,
            tb.genres,
            tr.averageRating,
            tr.numVotes,
            tc.directors,
            tc.writers
        FROM title_basics tb
        LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
        LEFT JOIN title_crew tc ON tb.tconst = tc.tconst
        WHERE tb.tconst = ?
    """
    
    # Fast cast lookup
    MOVIE_CAST = """
        SELECT 
            nb.nconst,
            nb.primaryName,
            tp.category,
            tp.characters,
            tp.ordering
        FROM title_principals tp
        JOIN name_basics nb ON tp.nconst = nb.nconst
        WHERE tp.tconst = ?
          AND tp.category IN ('actor', 'actress')
        ORDER BY tp.ordering
        LIMIT 20
    """
    
    # Person filmography optimized
    PERSON_FILMOGRAPHY = """
        SELECT 
            tb.tconst,
            tb.primaryTitle,
            tb.titleType,
            tb.startYear,
            tp.category,
            tp.characters,
            tr.averageRating,
            tr.numVotes
        FROM title_principals tp
        JOIN title_basics tb ON tp.tconst = tb.tconst
        LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
        WHERE tp.nconst = ?
        ORDER BY tb.startYear DESC, tr.numVotes DESC
        LIMIT 100
    """
    
    # Dashboard statistics
    DASHBOARD_STATS = """
        SELECT 
            'movies' as type,
            COUNT(*) as count
        FROM title_basics 
        WHERE titleType = 'movie'
        
        UNION ALL
        
        SELECT 
            'tv_series' as type,
            COUNT(*) as count
        FROM title_basics 
        WHERE titleType = 'tvSeries'
        
        UNION ALL
        
        SELECT 
            'people' as type,
            COUNT(*) as count
        FROM name_basics
        
        UNION ALL
        
        SELECT 
            'ratings' as type,
            COUNT(*) as count
        FROM title_ratings
    """
    
    # Genre analysis
    GENRE_ANALYSIS = """
        WITH genre_split AS (
            SELECT 
                tb.tconst,
                TRIM(genre.value) as genre,
                tr.averageRating,
                tr.numVotes
            FROM title_basics tb
            JOIN title_ratings tr ON tb.tconst = tr.tconst,
            json_each('["' || replace(tb.genres, ',', '","') || '"]') as genre
            WHERE tb.titleType = 'movie' 
              AND tb.genres IS NOT NULL
              AND tr.numVotes >= 100
        )
        SELECT 
            genre,
            COUNT(*) as movie_count,
            AVG(averageRating) as avg_rating,
            SUM(numVotes) as total_votes,
            MAX(averageRating) as max_rating
        FROM genre_split
        WHERE genre != ''
        GROUP BY genre
        HAVING COUNT(*) >= 50
        ORDER BY avg_rating DESC
    """

# Example usage
if __name__ == "__main__":
    # SQLite example
    db = OptimizedDatabaseManager(
        db_type="sqlite",
        database="imdb.db"
    )
    
    # PostgreSQL example
    # db = OptimizedDatabaseManager(
    #     db_type="postgresql",
    #     host="localhost",
    #     database="imdb",
    #     user="imdbuser",
    #     password="imdbpass",
    #     port=5432
    # )
    
    # Test queries
    queries = OptimizedQueries()
    
    # Search movies
    results = db.execute_query(
        queries.MOVIE_SEARCH,
        ("The Matrix", "The Matrix", "The Matrix", "The Matrix", "The Matrix", 10)
    )
    
    print(f"Found {len(results)} movies")
    print(db.get_stats())
