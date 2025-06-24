-- ================================
-- IMDb Dataset Import SQL Statements
-- ================================
-- SQL commands for importing IMDb TSV datasets into SQLite
-- These statements are used by the Python import scripts
-- Optimized for performance during bulk data import

-- ================================
-- IMPORT PREPARATION
-- ================================

-- Disable safety features for faster import
PRAGMA journal_mode=OFF;
PRAGMA synchronous=OFF;
PRAGMA cache_size=1000000;
PRAGMA temp_store=MEMORY;
PRAGMA foreign_keys=OFF;

-- Drop indexes during import (rebuild later)
DROP INDEX IF EXISTS idx_title_type;
DROP INDEX IF EXISTS idx_title_year;
DROP INDEX IF EXISTS idx_title_genres;
DROP INDEX IF EXISTS idx_title_adult;
DROP INDEX IF EXISTS idx_title_runtime;
DROP INDEX IF EXISTS idx_rating_avg;
DROP INDEX IF EXISTS idx_rating_votes;
DROP INDEX IF EXISTS idx_rating_combined;
DROP INDEX IF EXISTS idx_name_primary;
DROP INDEX IF EXISTS idx_name_birth;
DROP INDEX IF EXISTS idx_name_profession;
DROP INDEX IF EXISTS idx_principals_person;
DROP INDEX IF EXISTS idx_principals_title;
DROP INDEX IF EXISTS idx_principals_category;
DROP INDEX IF EXISTS idx_principals_ordering;
DROP INDEX IF EXISTS idx_crew_directors;
DROP INDEX IF EXISTS idx_crew_writers;
DROP INDEX IF EXISTS idx_akas_title;
DROP INDEX IF EXISTS idx_akas_region;
DROP INDEX IF EXISTS idx_akas_language;
DROP INDEX IF EXISTS idx_episode_parent;
DROP INDEX IF EXISTS idx_episode_season;
DROP INDEX IF EXISTS idx_episode_number;

-- ================================
-- DATA IMPORT STATEMENTS
-- ================================

-- Import title_basics from title.basics.tsv
-- Used by Python script: import_title_basics()
INSERT OR REPLACE INTO title_basics 
(tconst, titleType, primaryTitle, originalTitle, isAdult, startYear, endYear, runtimeMinutes, genres)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);

-- Import name_basics from name.basics.tsv
-- Used by Python script: import_name_basics()
INSERT OR REPLACE INTO name_basics 
(nconst, primaryName, birthYear, deathYear, primaryProfession, knownForTitles)
VALUES (?, ?, ?, ?, ?, ?);

-- Import title_ratings from title.ratings.tsv
-- Used by Python script: import_title_ratings()
INSERT OR REPLACE INTO title_ratings 
(tconst, averageRating, numVotes)
VALUES (?, ?, ?);

-- Import title_principals from title.principals.tsv
-- Used by Python script: import_title_principals()
INSERT OR REPLACE INTO title_principals 
(tconst, ordering, nconst, category, job, characters)
VALUES (?, ?, ?, ?, ?, ?);

-- Import title_crew from title.crew.tsv
-- Used by Python script: import_title_crew()
INSERT OR REPLACE INTO title_crew 
(tconst, directors, writers)
VALUES (?, ?, ?);

-- Import title_akas from title.akas.tsv
-- Used by Python script: import_title_akas()
INSERT OR REPLACE INTO title_akas 
(titleId, ordering, title, region, language, types, attributes, isOriginalTitle)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);

-- Import title_episode from title.episode.tsv
-- Used by Python script: import_title_episode()
INSERT OR REPLACE INTO title_episode 
(tconst, parentTconst, seasonNumber, episodeNumber)
VALUES (?, ?, ?, ?);

-- ================================
-- DATA VALIDATION QUERIES
-- ================================

-- Validate import counts (run after each table import)
SELECT 'title_basics' as table_name, COUNT(*) as record_count FROM title_basics
UNION ALL
SELECT 'name_basics', COUNT(*) FROM name_basics
UNION ALL
SELECT 'title_ratings', COUNT(*) FROM title_ratings
UNION ALL
SELECT 'title_principals', COUNT(*) FROM title_principals
UNION ALL
SELECT 'title_crew', COUNT(*) FROM title_crew
UNION ALL
SELECT 'title_akas', COUNT(*) FROM title_akas
UNION ALL
SELECT 'title_episode', COUNT(*) FROM title_episode;

-- Check for orphaned records (foreign key violations)
-- Movies without ratings (expected - not all movies have ratings)
SELECT COUNT(*) as movies_without_ratings
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie' AND tr.tconst IS NULL;

-- Principals with invalid person references (should be 0)
SELECT COUNT(*) as invalid_person_refs
FROM title_principals tp
LEFT JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE nb.nconst IS NULL;

-- Principals with invalid title references (should be 0)
SELECT COUNT(*) as invalid_title_refs
FROM title_principals tp
LEFT JOIN title_basics tb ON tp.tconst = tb.tconst
WHERE tb.tconst IS NULL;

-- Episodes with invalid parent series (should be 0)
SELECT COUNT(*) as invalid_episode_parents
FROM title_episode te
LEFT JOIN title_basics tb ON te.parentTconst = tb.tconst
WHERE tb.tconst IS NULL OR tb.titleType != 'tvSeries';

-- ================================
-- POST-IMPORT CLEANUP
-- ================================

-- Clean up data inconsistencies
-- Remove adult content if desired (optional)
-- DELETE FROM title_basics WHERE isAdult = 1;

-- Remove very short movies (likely errors)
-- DELETE FROM title_basics WHERE titleType = 'movie' AND runtimeMinutes < 10;

-- Remove very old entries with missing data (optional)
-- DELETE FROM title_basics WHERE startYear < 1900 AND primaryTitle IS NULL;

-- Update null values to proper format
UPDATE title_basics SET genres = NULL WHERE genres = '\N' OR genres = '';
UPDATE title_basics SET originalTitle = NULL WHERE originalTitle = '\N' OR originalTitle = '';
UPDATE name_basics SET primaryProfession = NULL WHERE primaryProfession = '\N' OR primaryProfession = '';
UPDATE name_basics SET knownForTitles = NULL WHERE knownForTitles = '\N' OR knownForTitles = '';
UPDATE title_principals SET job = NULL WHERE job = '\N' OR job = '';
UPDATE title_principals SET characters = NULL WHERE characters = '\N' OR characters = '';
UPDATE title_crew SET directors = NULL WHERE directors = '\N' OR directors = '';
UPDATE title_crew SET writers = NULL WHERE writers = '\N' OR writers = '';

-- ================================
-- REBUILD INDEXES AND OPTIMIZE
-- ================================

-- Recreate all indexes for optimal performance
CREATE INDEX idx_title_type ON title_basics(titleType);
CREATE INDEX idx_title_year ON title_basics(startYear);
CREATE INDEX idx_title_genres ON title_basics(genres);
CREATE INDEX idx_title_adult ON title_basics(isAdult);
CREATE INDEX idx_title_runtime ON title_basics(runtimeMinutes);

CREATE INDEX idx_rating_avg ON title_ratings(averageRating);
CREATE INDEX idx_rating_votes ON title_ratings(numVotes);
CREATE INDEX idx_rating_combined ON title_ratings(averageRating, numVotes);

CREATE INDEX idx_name_primary ON name_basics(primaryName);
CREATE INDEX idx_name_birth ON name_basics(birthYear);
CREATE INDEX idx_name_profession ON name_basics(primaryProfession);

CREATE INDEX idx_principals_person ON title_principals(nconst);
CREATE INDEX idx_principals_title ON title_principals(tconst);
CREATE INDEX idx_principals_category ON title_principals(category);
CREATE INDEX idx_principals_ordering ON title_principals(tconst, ordering);

CREATE INDEX idx_crew_directors ON title_crew(directors);
CREATE INDEX idx_crew_writers ON title_crew(writers);

CREATE INDEX idx_akas_title ON title_akas(titleId);
CREATE INDEX idx_akas_region ON title_akas(region);
CREATE INDEX idx_akas_language ON title_akas(language);

CREATE INDEX idx_episode_parent ON title_episode(parentTconst);
CREATE INDEX idx_episode_season ON title_episode(parentTconst, seasonNumber);
CREATE INDEX idx_episode_number ON title_episode(seasonNumber, episodeNumber);

-- ================================
-- PRODUCTION SETTINGS
-- ================================

-- Restore production database settings
PRAGMA foreign_keys=ON;
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA temp_store=MEMORY;

-- Update SQLite statistics for optimal query planning
ANALYZE;

-- ================================
-- FINAL VALIDATION REPORT
-- ================================

-- Generate comprehensive import report
SELECT 
    'Database Import Complete' as status,
    datetime('now') as completion_time;

-- Table sizes summary
SELECT 
    'title_basics' as table_name, 
    COUNT(*) as records,
    ROUND(SUM(LENGTH(tconst) + LENGTH(titleType) + LENGTH(primaryTitle)) / 1024.0 / 1024.0, 2) as size_mb
FROM title_basics
UNION ALL
SELECT 
    'name_basics', 
    COUNT(*),
    ROUND(SUM(LENGTH(nconst) + LENGTH(primaryName)) / 1024.0 / 1024.0, 2)
FROM name_basics
UNION ALL
SELECT 
    'title_ratings', 
    COUNT(*),
    ROUND(SUM(LENGTH(tconst)) / 1024.0 / 1024.0, 2)
FROM title_ratings
UNION ALL
SELECT 
    'title_principals', 
    COUNT(*),
    ROUND(SUM(LENGTH(tconst) + LENGTH(nconst) + LENGTH(category)) / 1024.0 / 1024.0, 2)
FROM title_principals
UNION ALL
SELECT 
    'title_crew', 
    COUNT(*),
    ROUND(SUM(LENGTH(tconst)) / 1024.0 / 1024.0, 2)
FROM title_crew
UNION ALL
SELECT 
    'title_akas', 
    COUNT(*),
    ROUND(SUM(LENGTH(titleId) + LENGTH(title)) / 1024.0 / 1024.0, 2)
FROM title_akas
UNION ALL
SELECT 
    'title_episode', 
    COUNT(*),
    ROUND(SUM(LENGTH(tconst) + LENGTH(parentTconst)) / 1024.0 / 1024.0, 2)
FROM title_episode;

-- Content distribution
SELECT 
    titleType,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM title_basics), 2) as percentage
FROM title_basics
GROUP BY titleType
ORDER BY count DESC;

-- Top genres
SELECT 
    genres,
    COUNT(*) as count
FROM title_basics
WHERE genres IS NOT NULL AND titleType = 'movie'
GROUP BY genres
ORDER BY count DESC
LIMIT 10;

-- Rating distribution
SELECT 
    ROUND(averageRating) as rating_rounded,
    COUNT(*) as count
FROM title_ratings
GROUP BY ROUND(averageRating)
ORDER BY rating_rounded;

-- ================================
-- BACKUP COMMANDS
-- ================================

-- Create backup after successful import
-- .backup imdb_backup.db

-- Vacuum to reclaim space and optimize
VACUUM;