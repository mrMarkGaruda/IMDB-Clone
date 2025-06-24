-- ================================
-- IMDb Clone Database Schema
-- ================================
-- Complete SQLite schema for IMDb dataset
-- Based on official IMDb dataset structure
-- Optimized for performance with strategic indexes

-- ================================
-- CORE TABLES
-- ================================

-- Primary table for all titles (movies, TV series, episodes)
CREATE TABLE title_basics (
    tconst TEXT PRIMARY KEY,        -- Unique identifier (e.g., 'tt0000001')
    titleType TEXT NOT NULL,        -- Type: 'movie', 'tvSeries', 'tvEpisode', etc.
    primaryTitle TEXT NOT NULL,     -- Main title
    originalTitle TEXT,             -- Original title in original language
    isAdult INTEGER DEFAULT 0,      -- 0 = non-adult, 1 = adult content
    startYear INTEGER,              -- Release/start year
    endYear INTEGER,                -- End year (for series, NULL for movies)
    runtimeMinutes INTEGER,         -- Duration in minutes
    genres TEXT                     -- Comma-separated genres
);

-- Information about people (actors, directors, writers, etc.)
CREATE TABLE name_basics (
    nconst TEXT PRIMARY KEY,        -- Unique identifier (e.g., 'nm0000001')
    primaryName TEXT NOT NULL,      -- Person's name
    birthYear INTEGER,              -- Birth year
    deathYear INTEGER,              -- Death year (NULL if alive)
    primaryProfession TEXT,         -- Main professions (comma-separated)
    knownForTitles TEXT            -- Known for these titles (comma-separated tconsts)
);

-- Ratings and vote counts for titles
CREATE TABLE title_ratings (
    tconst TEXT PRIMARY KEY,        -- Links to title_basics.tconst
    averageRating REAL NOT NULL,    -- IMDb rating (1.0-10.0)
    numVotes INTEGER NOT NULL,      -- Number of votes
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
);

-- Cast and crew information with roles
CREATE TABLE title_principals (
    tconst TEXT NOT NULL,           -- Links to title_basics.tconst
    ordering INTEGER NOT NULL,      -- Order of importance (1, 2, 3...)
    nconst TEXT NOT NULL,           -- Links to name_basics.nconst
    category TEXT NOT NULL,         -- Role: 'actor', 'director', 'writer', etc.
    job TEXT,                       -- Specific job title
    characters TEXT,                -- Character names (JSON array as string)
    PRIMARY KEY (tconst, ordering),
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst),
    FOREIGN KEY (nconst) REFERENCES name_basics(nconst)
);

-- Director and writer information
CREATE TABLE title_crew (
    tconst TEXT PRIMARY KEY,        -- Links to title_basics.tconst
    directors TEXT,                 -- Comma-separated director nconsts
    writers TEXT,                   -- Comma-separated writer nconsts
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
);

-- Alternative titles and localizations
CREATE TABLE title_akas (
    titleId TEXT NOT NULL,          -- Links to title_basics.tconst
    ordering INTEGER NOT NULL,      -- Order of this alternative title
    title TEXT,                     -- Alternative title
    region TEXT,                    -- Country/region code
    language TEXT,                  -- Language code
    types TEXT,                     -- Type of alternative title
    attributes TEXT,                -- Additional attributes
    isOriginalTitle INTEGER DEFAULT 0, -- 1 if this is the original title
    PRIMARY KEY (titleId, ordering),
    FOREIGN KEY (titleId) REFERENCES title_basics(tconst)
);

-- TV episode information
CREATE TABLE title_episode (
    tconst TEXT PRIMARY KEY,        -- Episode's tconst
    parentTconst TEXT NOT NULL,     -- Series' tconst
    seasonNumber INTEGER,           -- Season number
    episodeNumber INTEGER,          -- Episode number within season
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst),
    FOREIGN KEY (parentTconst) REFERENCES title_basics(tconst)
);

-- ================================
-- PERFORMANCE INDEXES
-- ================================

-- Essential indexes for fast queries
-- Title-based searches and filtering
CREATE INDEX idx_title_type ON title_basics(titleType);
CREATE INDEX idx_title_year ON title_basics(startYear);
CREATE INDEX idx_title_genres ON title_basics(genres);
CREATE INDEX idx_title_adult ON title_basics(isAdult);
CREATE INDEX idx_title_runtime ON title_basics(runtimeMinutes);

-- Rating-based sorting and filtering
CREATE INDEX idx_rating_avg ON title_ratings(averageRating);
CREATE INDEX idx_rating_votes ON title_ratings(numVotes);
CREATE INDEX idx_rating_combined ON title_ratings(averageRating, numVotes);

-- People-based lookups
CREATE INDEX idx_name_primary ON name_basics(primaryName);
CREATE INDEX idx_name_birth ON name_basics(birthYear);
CREATE INDEX idx_name_profession ON name_basics(primaryProfession);

-- Cast and crew lookups
CREATE INDEX idx_principals_person ON title_principals(nconst);
CREATE INDEX idx_principals_title ON title_principals(tconst);
CREATE INDEX idx_principals_category ON title_principals(category);
CREATE INDEX idx_principals_ordering ON title_principals(tconst, ordering);

-- Director and writer lookups
CREATE INDEX idx_crew_directors ON title_crew(directors);
CREATE INDEX idx_crew_writers ON title_crew(writers);

-- Alternative title searches
CREATE INDEX idx_akas_title ON title_akas(titleId);
CREATE INDEX idx_akas_region ON title_akas(region);
CREATE INDEX idx_akas_language ON title_akas(language);

-- TV episode navigation
CREATE INDEX idx_episode_parent ON title_episode(parentTconst);
CREATE INDEX idx_episode_season ON title_episode(parentTconst, seasonNumber);
CREATE INDEX idx_episode_number ON title_episode(seasonNumber, episodeNumber);

-- ================================
-- FULL-TEXT SEARCH INDEXES
-- ================================

-- Full-text search for titles (SQLite FTS5)
CREATE VIRTUAL TABLE title_search USING fts5(
    tconst UNINDEXED,
    primaryTitle,
    originalTitle,
    genres,
    content=title_basics,
    content_rowid=rowid
);

-- Full-text search for people
CREATE VIRTUAL TABLE name_search USING fts5(
    nconst UNINDEXED,
    primaryName,
    primaryProfession,
    content=name_basics,
    content_rowid=rowid
);

-- ================================
-- DATABASE CONFIGURATION
-- ================================

-- Performance optimizations for production
PRAGMA journal_mode=WAL;          -- Better concurrency
PRAGMA synchronous=NORMAL;        -- Balance speed/safety
PRAGMA cache_size=10000;          -- More memory for caching
PRAGMA temp_store=MEMORY;         -- Temp tables in RAM
PRAGMA mmap_size=268435456;       -- 256MB memory mapping

-- Foreign key enforcement
PRAGMA foreign_keys=ON;

-- Analysis optimization
ANALYZE;

-- ================================
-- VIEWS FOR COMMON QUERIES
-- ================================

-- Popular movies with ratings
CREATE VIEW popular_movies AS
SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.genres,
       tr.averageRating, tr.numVotes
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie' AND tr.numVotes >= 1000
ORDER BY tr.averageRating DESC, tr.numVotes DESC;

-- TV series with episode counts
CREATE VIEW tv_series_summary AS
SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.endYear, tb.genres,
       tr.averageRating, tr.numVotes,
       COUNT(DISTINCT te.seasonNumber) as season_count,
       COUNT(te.tconst) as episode_count
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
LEFT JOIN title_episode te ON tb.tconst = te.parentTconst
WHERE tb.titleType = 'tvSeries'
GROUP BY tb.tconst, tb.primaryTitle, tb.startYear, tb.endYear, tb.genres,
         tr.averageRating, tr.numVotes;

-- Person filmography summary
CREATE VIEW person_filmography AS
SELECT nb.nconst, nb.primaryName, nb.birthYear, nb.deathYear,
       tp.category, tb.primaryTitle, tb.startYear, tb.titleType,
       tr.averageRating, tr.numVotes
FROM name_basics nb
JOIN title_principals tp ON nb.nconst = tp.nconst
JOIN title_basics tb ON tp.tconst = tb.tconst
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
ORDER BY nb.primaryName, tb.startYear DESC;

-- ================================
-- TRIGGERS FOR DATA INTEGRITY
-- ================================

-- Update FTS index when title_basics changes
CREATE TRIGGER title_search_insert AFTER INSERT ON title_basics
BEGIN
    INSERT INTO title_search(tconst, primaryTitle, originalTitle, genres)
    VALUES (NEW.tconst, NEW.primaryTitle, NEW.originalTitle, NEW.genres);
END;

CREATE TRIGGER title_search_update AFTER UPDATE ON title_basics
BEGIN
    UPDATE title_search 
    SET primaryTitle = NEW.primaryTitle,
        originalTitle = NEW.originalTitle,
        genres = NEW.genres
    WHERE tconst = NEW.tconst;
END;

CREATE TRIGGER title_search_delete AFTER DELETE ON title_basics
BEGIN
    DELETE FROM title_search WHERE tconst = OLD.tconst;
END;

-- Update FTS index when name_basics changes
CREATE TRIGGER name_search_insert AFTER INSERT ON name_basics
BEGIN
    INSERT INTO name_search(nconst, primaryName, primaryProfession)
    VALUES (NEW.nconst, NEW.primaryName, NEW.primaryProfession);
END;

CREATE TRIGGER name_search_update AFTER UPDATE ON name_basics
BEGIN
    UPDATE name_search 
    SET primaryName = NEW.primaryName,
        primaryProfession = NEW.primaryProfession
    WHERE nconst = NEW.nconst;
END;

CREATE TRIGGER name_search_delete AFTER DELETE ON name_basics
BEGIN
    DELETE FROM name_search WHERE nconst = OLD.nconst;
END;

-- ================================
-- COMMENTS AND DOCUMENTATION
-- ================================

-- This schema is optimized for:
-- 1. Fast movie/TV series browsing with filters
-- 2. Efficient person lookups and filmographies
-- 3. Quick search across titles and people
-- 4. Analytics queries for trends and statistics
-- 5. Scalability to handle 50M+ records

-- Index strategy:
-- - Single column indexes for common WHERE clauses
-- - Composite indexes for complex queries
-- - Full-text search for advanced search features
-- - Strategic use of covering indexes

-- Performance notes:
-- - WAL mode enables better concurrency
-- - Memory mapping improves large dataset performance
-- - Regular ANALYZE updates help query optimizer
-- - Views simplify common query patterns