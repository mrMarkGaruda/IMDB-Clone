#!/usr/bin/env python3
"""
⚡ PERFORMANCE BENCHMARK SUITE
Test and validate the optimized IMDB Clone performance
"""
import time
import sqlite3
import statistics
from pathlib import Path
import sys

class PerformanceTester:
    """Comprehensive performance testing suite"""
    
    def __init__(self, db_path="imdb.db"):
        self.db_path = db_path
        self.results = {}
        
    def connect_db(self):
        """Get optimized database connection"""
        conn = sqlite3.connect(self.db_path)
        # Apply performance optimizations
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL") 
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = MEMORY")
        return conn
    
    def time_query(self, query, params=None, runs=5):
        """Time a query execution multiple times"""
        times = []
        
        for _ in range(runs):
            conn = self.connect_db()
            start_time = time.time()
            
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            
            execution_time = time.time() - start_time
            times.append(execution_time)
            conn.close()
        
        return {
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'result_count': len(results) if 'results' in locals() else 0
        }
    
    def test_basic_queries(self):
        """Test basic query performance"""
        print("🔍 Testing Basic Query Performance...")
        
        tests = [
            ("Movie Count", "SELECT COUNT(*) FROM title_basics WHERE titleType = 'movie'"),
            ("Person Count", "SELECT COUNT(*) FROM name_basics"),
            ("Rating Count", "SELECT COUNT(*) FROM title_ratings"),
            ("Recent Movies", """
                SELECT tb.tconst, tb.primaryTitle, tb.startYear 
                FROM title_basics tb 
                WHERE tb.titleType = 'movie' AND tb.startYear >= 2020 
                LIMIT 100
            """),
            ("Top Rated", """
                SELECT tb.tconst, tb.primaryTitle, tr.averageRating 
                FROM title_basics tb 
                JOIN title_ratings tr ON tb.tconst = tr.tconst 
                WHERE tb.titleType = 'movie' AND tr.numVotes >= 1000
                ORDER BY tr.averageRating DESC 
                LIMIT 50
            """)
        ]
        
        for test_name, query in tests:
            result = self.time_query(query)
            self.results[test_name] = result
            
            status = "⚡" if result['avg_time'] < 0.1 else "🐌" if result['avg_time'] > 1.0 else "✅"
            print(f"  {status} {test_name:15}: {result['avg_time']:.3f}s avg ({result['result_count']} rows)")
    
    def test_search_queries(self):
        """Test search performance"""
        print("\n🔍 Testing Search Performance...")
        
        search_tests = [
            ("Title Search", """
                SELECT tb.tconst, tb.primaryTitle, tb.startYear
                FROM title_basics tb
                WHERE tb.primaryTitle LIKE '%Matrix%'
                LIMIT 20
            """),
            ("Person Search", """
                SELECT nb.nconst, nb.primaryName, nb.birthYear
                FROM name_basics nb
                WHERE nb.primaryName LIKE '%Smith%'
                LIMIT 20
            """),
            ("Genre Filter", """
                SELECT tb.tconst, tb.primaryTitle, tb.genres
                FROM title_basics tb
                WHERE tb.titleType = 'movie' AND tb.genres LIKE '%Action%'
                LIMIT 50
            """)
        ]
        
        for test_name, query in search_tests:
            result = self.time_query(query)
            self.results[test_name] = result
            
            status = "⚡" if result['avg_time'] < 0.05 else "🐌" if result['avg_time'] > 0.5 else "✅"
            print(f"  {status} {test_name:15}: {result['avg_time']:.3f}s avg ({result['result_count']} rows)")
    
    def test_complex_queries(self):
        """Test complex query performance"""
        print("\n📊 Testing Complex Query Performance...")
        
        complex_tests = [
            ("Movie Details", """
                SELECT 
                    tb.tconst, tb.primaryTitle, tb.startYear, tb.genres,
                    tr.averageRating, tr.numVotes,
                    tc.directors, tc.writers
                FROM title_basics tb
                LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
                LEFT JOIN title_crew tc ON tb.tconst = tc.tconst
                WHERE tb.tconst = 'tt0111161'
            """),
            ("Cast Query", """
                SELECT 
                    nb.primaryName, tp.category, tp.characters
                FROM title_principals tp
                JOIN name_basics nb ON tp.nconst = nb.nconst
                WHERE tp.tconst = 'tt0111161'
                ORDER BY tp.ordering
                LIMIT 20
            """),
            ("Filmography", """
                SELECT 
                    tb.tconst, tb.primaryTitle, tb.titleType, tb.startYear,
                    tp.category, tr.averageRating
                FROM title_principals tp
                JOIN title_basics tb ON tp.tconst = tb.tconst
                LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
                WHERE tp.nconst = 'nm0000209'
                ORDER BY tb.startYear DESC
                LIMIT 50
            """),
            ("Genre Analysis", """
                SELECT 
                    SUBSTR(tb.genres, 1, INSTR(tb.genres || ',', ',') - 1) as primary_genre,
                    COUNT(*) as movie_count,
                    AVG(tr.averageRating) as avg_rating
                FROM title_basics tb
                JOIN title_ratings tr ON tb.tconst = tr.tconst
                WHERE tb.titleType = 'movie' AND tb.genres IS NOT NULL AND tr.numVotes >= 1000
                GROUP BY primary_genre
                HAVING movie_count >= 100
                ORDER BY avg_rating DESC
                LIMIT 20
            """)
        ]
        
        for test_name, query in complex_tests:
            result = self.time_query(query, runs=3)  # Fewer runs for complex queries
            self.results[test_name] = result
            
            status = "⚡" if result['avg_time'] < 0.2 else "🐌" if result['avg_time'] > 2.0 else "✅"
            print(f"  {status} {test_name:15}: {result['avg_time']:.3f}s avg ({result['result_count']} rows)")
    
    def test_database_size(self):
        """Test database size and statistics"""
        print("\n📊 Database Statistics...")
        
        try:
            # Database file size
            db_size = Path(self.db_path).stat().st_size / (1024**2)  # MB
            print(f"  📁 Database size: {db_size:.1f} MB")
            
            # Table counts
            conn = self.connect_db()
            
            tables = [
                'title_basics', 'name_basics', 'title_ratings',
                'title_principals', 'title_crew', 'title_episode', 'title_akas'
            ]
            
            total_rows = 0
            for table in tables:
                try:
                    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    print(f"  📊 {table:20}: {count:,} rows")
                    total_rows += count
                except:
                    print(f"  ⚠️ {table:20}: Table not found")
            
            print(f"  📈 Total rows: {total_rows:,}")
            
            # Index information
            indexes = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """).fetchall()
            
            print(f"  🗂️ Custom indexes: {len(indexes)}")
            
            conn.close()
            
        except Exception as e:
            print(f"  ❌ Error getting database stats: {e}")
    
    def generate_report(self):
        """Generate performance report"""
        print("\n📈 PERFORMANCE REPORT")
        print("=" * 50)
        
        # Categorize results
        excellent = []  # < 0.1s
        good = []       # 0.1s - 0.5s
        acceptable = [] # 0.5s - 1.0s
        slow = []       # > 1.0s
        
        for test_name, result in self.results.items():
            avg_time = result['avg_time']
            
            if avg_time < 0.1:
                excellent.append((test_name, avg_time))
            elif avg_time < 0.5:
                good.append((test_name, avg_time))
            elif avg_time < 1.0:
                acceptable.append((test_name, avg_time))
            else:
                slow.append((test_name, avg_time))
        
        if excellent:
            print("⚡ EXCELLENT (< 0.1s):")
            for name, time in excellent:
                print(f"   {name}: {time:.3f}s")
        
        if good:
            print("\n✅ GOOD (0.1s - 0.5s):")
            for name, time in good:
                print(f"   {name}: {time:.3f}s")
        
        if acceptable:
            print("\n⚠️ ACCEPTABLE (0.5s - 1.0s):")
            for name, time in acceptable:
                print(f"   {name}: {time:.3f}s")
        
        if slow:
            print("\n🐌 NEEDS OPTIMIZATION (> 1.0s):")
            for name, time in slow:
                print(f"   {name}: {time:.3f}s")
        
        # Overall assessment
        total_tests = len(self.results)
        fast_tests = len(excellent) + len(good)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total tests: {total_tests}")
        print(f"   Fast queries (< 0.5s): {fast_tests}/{total_tests} ({fast_tests/total_tests*100:.1f}%)")
        
        if fast_tests/total_tests >= 0.8:
            print("   🎉 Performance: EXCELLENT!")
        elif fast_tests/total_tests >= 0.6:
            print("   ✅ Performance: GOOD")
        elif fast_tests/total_tests >= 0.4:
            print("   ⚠️ Performance: ACCEPTABLE")
        else:
            print("   🐌 Performance: NEEDS IMPROVEMENT")
    
    def run_all_tests(self):
        """Run complete performance test suite"""
        print("🚀 IMDB Clone Performance Benchmark")
        print("=" * 50)
        
        if not Path(self.db_path).exists():
            print(f"❌ Database file '{self.db_path}' not found!")
            print("Please run the data import first.")
            return
        
        try:
            self.test_database_size()
            self.test_basic_queries() 
            self.test_search_queries()
            self.test_complex_queries()
            self.generate_report()
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")

def main():
    """Main function"""
    db_path = sys.argv[1] if len(sys.argv) > 1 else "imdb.db"
    
    tester = PerformanceTester(db_path)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
