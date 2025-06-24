-- OPTIMIZED IMDB CLONE DATABASE SCHEMA
-- Designed for maximum performance with strategic indexing
-- Supports both SQLite and PostgreSQL

-- =======================
-- CORE TABLES
-- =======================

-- Main titles table (movies, TV series, episodes, etc.)
CREATE TABLE title_basics (
    tconst TEXT PRIMARY KEY,
    titleType TEXT NOT NULL,                    -- movie, tvSeries, tvEpisode, etc.
    primaryTitle TEXT NOT NULL,
    originalTitle TEXT,
    isAdult INTEGER DEFAULT 0,
    startYear INTEGER,
    endYear INTEGER,
    runtimeMinutes INTEGER,
    genres TEXT                                  -- Comma-separated for fast LIKE queries
);

-- People in the industry (actors, directors, writers, etc.)
CREATE TABLE name_basics (
    nconst TEXT PRIMARY KEY,
    primaryName TEXT NOT NULL,
    birthYear INTEGER,
    deathYear INTEGER,
    primaryProfession TEXT,                     -- Comma-separated professions
    knownForTitles TEXT                         -- Comma-separated tconst values
);

-- Ratings and votes for titles
CREATE TABLE title_ratings (
    tconst TEXT PRIMARY KEY,
    averageRating REAL NOT NULL,
    numVotes INTEGER NOT NULL,
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
);

-- Cast and crew assignments
CREATE TABLE title_principals (
    tconst TEXT NOT NULL,
    ordering INTEGER NOT NULL,                  -- Position in credits
    nconst TEXT NOT NULL,
    category TEXT NOT NULL,                     -- actor, director, writer, etc.
    job TEXT,                                   -- Specific job title
    characters TEXT,                            -- Character names (JSON array as text)
    PRIMARY KEY (tconst, ordering),
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst),
    FOREIGN KEY (nconst) REFERENCES name_basics(nconst)
);

-- Directors and writers (denormalized for performance)
CREATE TABLE title_crew (
    tconst TEXT PRIMARY KEY,
    directors TEXT,                             -- Comma-separated nconst values
    writers TEXT,                               -- Comma-separated nconst values
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
);

-- TV episode relationships
CREATE TABLE title_episode (
    tconst TEXT PRIMARY KEY,
    parentTconst TEXT NOT NULL,                 -- Reference to TV series
    seasonNumber INTEGER,
    episodeNumber INTEGER,
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst),
    FOREIGN KEY (parentTconst) REFERENCES title_basics(tconst)
);

-- Alternative titles and regional variations
CREATE TABLE title_akas (
    titleId TEXT NOT NULL,
    ordering INTEGER NOT NULL,
    title TEXT,
    region TEXT,
    language TEXT,
    types TEXT,
    attributes TEXT,
    isOriginalTitle INTEGER,
    PRIMARY KEY (titleId, ordering),
    FOREIGN KEY (titleId) REFERENCES title_basics(tconst)
);

-- =======================
-- PERFORMANCE INDEXES
-- =======================

-- Primary lookup indexes
CREATE INDEX idx_title_type ON title_basics(titleType);
CREATE INDEX idx_title_year ON title_basics(startYear);
CREATE INDEX idx_title_year_range ON title_basics(startYear, endYear);
CREATE INDEX idx_title_adult ON title_basics(isAdult);
CREATE INDEX idx_title_runtime ON title_basics(runtimeMinutes);

-- Genre searching (for LIKE queries)
CREATE INDEX idx_title_genre ON title_basics(genres);

-- Text search indexes
CREATE INDEX idx_title_primary ON title_basics(primaryTitle);
CREATE INDEX idx_title_original ON title_basics(originalTitle);
CREATE INDEX idx_name_primary ON name_basics(primaryName);

-- Rating and popularity indexes
CREATE INDEX idx_ratings_score ON title_ratings(averageRating DESC);
CREATE INDEX idx_ratings_votes ON title_ratings(numVotes DESC);
CREATE INDEX idx_ratings_combined ON title_ratings(averageRating DESC, numVotes DESC);

-- Cast and crew indexes
CREATE INDEX idx_principals_title ON title_principals(tconst);
CREATE INDEX idx_principals_person ON title_principals(nconst);
CREATE INDEX idx_principals_category ON title_principals(category);
CREATE INDEX idx_principals_ordering ON title_principals(tconst, ordering);

-- Episode indexes
CREATE INDEX idx_episode_parent ON title_episode(parentTconst);
CREATE INDEX idx_episode_season ON title_episode(parentTconst, seasonNumber);

-- Alternative titles
CREATE INDEX idx_akas_title ON title_akas(titleId);
CREATE INDEX idx_akas_region ON title_akas(region);

-- Crew quick lookup
CREATE INDEX idx_crew_directors ON title_crew(directors);
CREATE INDEX idx_crew_writers ON title_crew(writers);

-- =======================
-- COMPOSITE INDEXES FOR COMPLEX QUERIES
-- =======================

-- Movie listing with filters
CREATE INDEX idx_movie_filters ON title_basics(titleType, startYear, isAdult, genres);

-- Popular movies by year
CREATE INDEX idx_popular_by_year ON title_basics(titleType, startYear) 
    WHERE titleType = 'movie';

-- TV series with episodes
CREATE INDEX idx_tv_series ON title_basics(titleType, startYear) 
    WHERE titleType = 'tvSeries';

-- Person filmography
CREATE INDEX idx_filmography ON title_principals(nconst, tconst);

-- =======================
-- VIEWS FOR COMMON QUERIES
-- =======================

-- Popular movies view
CREATE VIEW popular_movies AS
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
ORDER BY tr.averageRating DESC, tr.numVotes DESC;

-- Recent releases view
CREATE VIEW recent_releases AS
SELECT 
    tb.tconst,
    tb.primaryTitle,
    tb.titleType,
    tb.startYear,
    tr.averageRating,
    tr.numVotes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.startYear >= (strftime('%Y', 'now') - 5)
ORDER BY tb.startYear DESC, tr.numVotes DESC;

-- =======================
-- OPTIMIZATION SETTINGS
-- =======================

-- SQLite specific optimizations
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456; -- 256MB memory map
