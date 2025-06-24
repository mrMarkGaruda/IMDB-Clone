"""
🚀 ULTRA-FAST DATA IMPORTER
Parallel processing with optimized memory usage for IMDB data import
"""
import gzip
import pandas as pd
import sqlite3
import time
import multiprocessing as mp
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import psutil
import numpy as np
from typing import Dict, List, Tuple

class TurboDataImporter:
    """
    Lightning-fast data importer with parallel processing,
    memory optimization, and progress tracking
    """
    
    def __init__(self, dataset_path="dataset", db_path="imdb.db"):
        self.dataset_path = Path(dataset_path)
        self.db_path = db_path
        
        # Performance settings
        self.cpu_count = mp.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.optimal_chunk_size = self._calculate_optimal_chunk_size()
        self.max_workers = min(self.cpu_count, 8)  # Don't overwhelm the system
        
        print(f"🔥 TurboDataImporter initialized:")
        print(f"   📊 CPUs: {self.cpu_count}")
        print(f"   💾 RAM: {self.memory_gb:.1f} GB")
        print(f"   📦 Chunk size: {self.optimal_chunk_size:,} rows")
        print(f"   🧵 Max workers: {self.max_workers}")
    
    def _calculate_optimal_chunk_size(self) -> int:
        """Calculate optimal chunk size based on available memory"""
        if self.memory_gb >= 16:
            return 50000  # High memory system
        elif self.memory_gb >= 8:
            return 25000  # Medium memory system
        else:
            return 10000  # Low memory system
    
    def create_optimized_schema(self):
        """Create schema with maximum performance optimizations"""
        print("🏗️ Creating ultra-optimized database schema...")
        
        conn = sqlite3.connect(self.db_path)
        
        # Performance PRAGMA settings
        performance_settings = """
            PRAGMA journal_mode = OFF;          -- Fastest for bulk import
            PRAGMA synchronous = OFF;           -- Skip disk sync during import
            PRAGMA cache_size = 100000;         -- Large cache
            PRAGMA temp_store = MEMORY;         -- Use RAM for temp tables
            PRAGMA mmap_size = 1073741824;      -- 1GB memory map
            PRAGMA locking_mode = EXCLUSIVE;    -- Exclusive access
            PRAGMA foreign_keys = OFF;          -- Disable during import
        """
        
        conn.executescript(performance_settings)
        
        # Drop and recreate all tables
        schema_sql = """
        -- Drop existing tables
        DROP TABLE IF EXISTS title_ratings;
        DROP TABLE IF EXISTS title_principals;
        DROP TABLE IF EXISTS title_crew;
        DROP TABLE IF EXISTS title_episode;
        DROP TABLE IF EXISTS title_akas;
        DROP TABLE IF EXISTS name_basics;
        DROP TABLE IF EXISTS title_basics;
        
        -- Core tables (no foreign keys during import for speed)
        CREATE TABLE title_basics (
            tconst TEXT PRIMARY KEY,
            titleType TEXT NOT NULL,
            primaryTitle TEXT NOT NULL,
            originalTitle TEXT,
            isAdult INTEGER DEFAULT 0,
            startYear INTEGER,
            endYear INTEGER,
            runtimeMinutes INTEGER,
            genres TEXT
        );
        
        CREATE TABLE name_basics (
            nconst TEXT PRIMARY KEY,
            primaryName TEXT NOT NULL,
            birthYear INTEGER,
            deathYear INTEGER,
            primaryProfession TEXT,
            knownForTitles TEXT
        );
        
        CREATE TABLE title_ratings (
            tconst TEXT PRIMARY KEY,
            averageRating REAL NOT NULL,
            numVotes INTEGER NOT NULL
        );
        
        CREATE TABLE title_principals (
            tconst TEXT NOT NULL,
            ordering INTEGER NOT NULL,
            nconst TEXT NOT NULL,
            category TEXT NOT NULL,
            job TEXT,
            characters TEXT
        );
        
        CREATE TABLE title_crew (
            tconst TEXT PRIMARY KEY,
            directors TEXT,
            writers TEXT
        );
        
        CREATE TABLE title_episode (
            tconst TEXT PRIMARY KEY,
            parentTconst TEXT NOT NULL,
            seasonNumber INTEGER,
            episodeNumber INTEGER
        );
        
        CREATE TABLE title_akas (
            titleId TEXT NOT NULL,
            ordering INTEGER NOT NULL,
            title TEXT,
            region TEXT,
            language TEXT,
            types TEXT,
            attributes TEXT,
            isOriginalTitle INTEGER
        );
        """
        
        conn.executescript(schema_sql)
        conn.close()
        print("✅ Schema created successfully")
    
    def preprocess_file(self, file_path: Path, table_name: str) -> pd.DataFrame:
        """Optimized file preprocessing with memory efficiency"""
        print(f"📂 Preprocessing {file_path.name}...")
        start_time = time.time()
        
        # Read with optimized settings
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                # Read in chunks to avoid memory issues
                chunks = []
                chunk_iter = pd.read_csv(
                    f,
                    sep='\t',
                    na_values=['\\N', ''],
                    keep_default_na=True,
                    low_memory=False,
                    chunksize=self.optimal_chunk_size,
                    dtype=str  # Read everything as string initially
                )
                
                for chunk in chunk_iter:
                    chunks.append(chunk)
                
                df = pd.concat(chunks, ignore_index=True)
                
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return pd.DataFrame()
        
        # Table-specific optimizations
        df = self._optimize_dataframe(df, table_name)
        
        load_time = time.time() - start_time
        print(f"✅ Loaded {len(df):,} rows in {load_time:.2f}s from {file_path.name}")
        
        return df
    
    def _optimize_dataframe(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Optimize DataFrame for specific table"""
        # Replace NaN with None for SQLite compatibility
        df = df.where(pd.notnull(df), None)
        
        if table_name == 'title_basics':
            # Optimize data types
            df['isAdult'] = pd.to_numeric(df['isAdult'], errors='coerce').fillna(0).astype(int)
            df['startYear'] = pd.to_numeric(df['startYear'], errors='coerce')
            df['endYear'] = pd.to_numeric(df['endYear'], errors='coerce')
            df['runtimeMinutes'] = pd.to_numeric(df['runtimeMinutes'], errors='coerce')
            
        elif table_name == 'name_basics':
            df['birthYear'] = pd.to_numeric(df['birthYear'], errors='coerce')
            df['deathYear'] = pd.to_numeric(df['deathYear'], errors='coerce')
            
        elif table_name == 'title_ratings':
            df['averageRating'] = pd.to_numeric(df['averageRating'], errors='coerce')
            df['numVotes'] = pd.to_numeric(df['numVotes'], errors='coerce')
            # Remove rows with invalid ratings
            df = df.dropna(subset=['averageRating', 'numVotes'])
            
        elif table_name == 'title_episode':
            df['seasonNumber'] = pd.to_numeric(df['seasonNumber'], errors='coerce')
            df['episodeNumber'] = pd.to_numeric(df['episodeNumber'], errors='coerce')
            
        elif table_name == 'title_principals':
            df['ordering'] = pd.to_numeric(df['ordering'], errors='coerce').fillna(0).astype(int)
            
        return df
    
    def parallel_insert(self, df: pd.DataFrame, table_name: str):
        """Ultra-fast parallel insert with chunking"""
        if df.empty:
            return
        
        print(f"🚀 Starting parallel insert for {table_name} ({len(df):,} rows)...")
        start_time = time.time()
        
        # Split DataFrame into chunks for parallel processing
        chunk_size = min(self.optimal_chunk_size, len(df) // self.max_workers + 1)
        chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
        
        # Use ThreadPoolExecutor for I/O bound database operations
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for i, chunk in enumerate(chunks):
                future = executor.submit(self._insert_chunk, chunk, table_name, i)
                futures.append(future)
            
            # Wait for all chunks to complete
            completed = 0
            for future in futures:
                future.result()
                completed += 1
                progress = (completed / len(futures)) * 100
                print(f"   📊 Progress: {progress:.1f}% ({completed}/{len(futures)} chunks)")
        
        total_time = time.time() - start_time
        rows_per_second = len(df) / total_time
        
        print(f"✅ Inserted {len(df):,} rows in {total_time:.2f}s ({rows_per_second:,.0f} rows/sec)")
    
    def _insert_chunk(self, chunk: pd.DataFrame, table_name: str, chunk_id: int):
        """Insert a single chunk of data"""
        conn = sqlite3.connect(self.db_path, timeout=60.0)
        
        try:
            # Use pandas to_sql with optimized settings
            chunk.to_sql(
                table_name,
                conn,
                if_exists='append',
                index=False,
                method='multi'  # Use executemany for better performance
            )
            
        except Exception as e:
            print(f"❌ Error inserting chunk {chunk_id} for {table_name}: {e}")
        finally:
            conn.close()
    
    def create_indexes_parallel(self):
        """Create indexes in parallel for maximum speed"""
        print("🏗️ Creating performance indexes...")
        start_time = time.time()
        
        # Index creation queries
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_title_type ON title_basics(titleType)",
            "CREATE INDEX IF NOT EXISTS idx_title_year ON title_basics(startYear)",
            "CREATE INDEX IF NOT EXISTS idx_title_genre ON title_basics(genres)",
            "CREATE INDEX IF NOT EXISTS idx_title_primary ON title_basics(primaryTitle)",
            "CREATE INDEX IF NOT EXISTS idx_name_primary ON name_basics(primaryName)",
            "CREATE INDEX IF NOT EXISTS idx_ratings_score ON title_ratings(averageRating DESC)",
            "CREATE INDEX IF NOT EXISTS idx_ratings_votes ON title_ratings(numVotes DESC)",
            "CREATE INDEX IF NOT EXISTS idx_principals_title ON title_principals(tconst)",
            "CREATE INDEX IF NOT EXISTS idx_principals_person ON title_principals(nconst)",
            "CREATE INDEX IF NOT EXISTS idx_principals_category ON title_principals(category)",
            "CREATE INDEX IF NOT EXISTS idx_episode_parent ON title_episode(parentTconst)",
            "CREATE INDEX IF NOT EXISTS idx_akas_title ON title_akas(titleId)"
        ]
        
        # Create indexes in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._create_index, query) for query in index_queries]
            
            for i, future in enumerate(futures):
                future.result()
                progress = ((i + 1) / len(futures)) * 100
                print(f"   📊 Index progress: {progress:.1f}%")
        
        index_time = time.time() - start_time
        print(f"✅ Created {len(index_queries)} indexes in {index_time:.2f}s")
    
    def _create_index(self, query: str):
        """Create a single index"""
        conn = sqlite3.connect(self.db_path, timeout=60.0)
        try:
            conn.execute(query)
            conn.commit()
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
        finally:
            conn.close()
    
    def finalize_database(self):
        """Apply final optimizations and enable constraints"""
        print("🏁 Finalizing database...")
        
        conn = sqlite3.connect(self.db_path)
        
        # Re-enable normal operation modes
        finalization_sql = """
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;
            PRAGMA foreign_keys = ON;
            PRAGMA optimize;
            ANALYZE;
        """
        
        conn.executescript(finalization_sql)
        conn.close()
        
        print("✅ Database finalized and optimized")
    
    def turbo_import(self):
        """Main import method with full optimization"""
        total_start_time = time.time()
        
        print("🚀 STARTING TURBO IMPORT PROCESS")
        print("=" * 50)
        
        # File import order (optimized for foreign key dependencies)
        import_sequence = [
            ("title.basics.tsv.gz", "title_basics"),
            ("name.basics.tsv.gz", "name_basics"),
            ("title.ratings.tsv.gz", "title_ratings"),
            ("title.crew.tsv.gz", "title_crew"),
            ("title.episode.tsv.gz", "title_episode"),
            ("title.akas.tsv.gz", "title_akas"),
            ("title.principals.tsv.gz", "title_principals")  # Largest file last
        ]
        
        # Step 1: Create schema
        self.create_optimized_schema()
        
        # Step 2: Import data files
        for filename, table_name in import_sequence:
            file_path = self.dataset_path / filename
            
            if not file_path.exists():
                print(f"⚠️ File not found: {filename}")
                continue
            
            # Preprocess and import
            df = self.preprocess_file(file_path, table_name)
            if not df.empty:
                self.parallel_insert(df, table_name)
            
            # Clean up memory
            del df
        
        # Step 3: Create indexes
        self.create_indexes_parallel()
        
        # Step 4: Finalize
        self.finalize_database()
        
        total_time = time.time() - total_start_time
        print("=" * 50)
        print(f"🎉 TURBO IMPORT COMPLETED IN {total_time:.2f}s ({total_time/60:.1f} minutes)")
        
        # Show final statistics
        self.show_import_stats()
    
    def show_import_stats(self):
        """Display import statistics"""
        print("\n📊 IMPORT STATISTICS")
        print("-" * 30)
        
        conn = sqlite3.connect(self.db_path)
        
        tables = [
            'title_basics', 'name_basics', 'title_ratings',
            'title_crew', 'title_episode', 'title_akas', 'title_principals'
        ]
        
        total_rows = 0
        for table in tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"   {table:20}: {count:,} rows")
                total_rows += count
            except Exception as e:
                print(f"   {table:20}: Error - {e}")
        
        print(f"   {'TOTAL':20}: {total_rows:,} rows")
        
        # Database size
        db_size = Path(self.db_path).stat().st_size / (1024**2)  # MB
        print(f"   Database size: {db_size:.1f} MB")
        
        conn.close()

# Usage example
if __name__ == "__main__":
    importer = TurboDataImporter(dataset_path="dataset", db_path="imdb.db")
    importer.turbo_import()
