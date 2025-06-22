-- Schema creation only - import is handled by separate import container
-- This file only creates the database schema and indexes

\echo 'Creating IMDB Database Schema...'

-- Create tables for IMDB data
CREATE TABLE IF NOT EXISTS name_basics (
    nconst VARCHAR(20) PRIMARY KEY,
    primaryName VARCHAR(500),
    birthYear INTEGER,
    deathYear INTEGER,
    primaryProfession TEXT,
    knownForTitles TEXT
);

CREATE TABLE IF NOT EXISTS title_basics (
    tconst VARCHAR(20) PRIMARY KEY,
    titleType VARCHAR(50),
    primaryTitle VARCHAR(1000),
    originalTitle VARCHAR(1000),
    isAdult BOOLEAN,
    startYear INTEGER,
    endYear INTEGER,
    runtimeMinutes INTEGER,
    genres VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS title_akas (
    titleId VARCHAR(20),
    ordering INTEGER,
    title VARCHAR(1000),
    region VARCHAR(10),
    language VARCHAR(10),
    types VARCHAR(100),
    attributes TEXT,
    isOriginalTitle BOOLEAN,
    PRIMARY KEY (titleId, ordering)
);

CREATE TABLE IF NOT EXISTS title_crew (
    tconst VARCHAR(20) PRIMARY KEY,
    directors TEXT,
    writers TEXT
);

CREATE TABLE IF NOT EXISTS title_episode (
    tconst VARCHAR(20) PRIMARY KEY,
    parentTconst VARCHAR(20),
    seasonNumber INTEGER,
    episodeNumber INTEGER
);

CREATE TABLE IF NOT EXISTS title_principals (
    tconst VARCHAR(20),
    ordering INTEGER,
    nconst VARCHAR(20),
    category VARCHAR(50),
    job VARCHAR(500),
    characters TEXT,
    PRIMARY KEY (tconst, ordering)
);

CREATE TABLE IF NOT EXISTS title_ratings (
    tconst VARCHAR(20) PRIMARY KEY,
    averageRating DECIMAL(3,1),
    numVotes INTEGER
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_title_basics_title_type ON title_basics(titleType);
CREATE INDEX IF NOT EXISTS idx_title_basics_start_year ON title_basics(startYear);
CREATE INDEX IF NOT EXISTS idx_title_basics_genres ON title_basics USING gin(string_to_array(genres, ','));
CREATE INDEX IF NOT EXISTS idx_title_ratings_rating ON title_ratings(averageRating);
CREATE INDEX IF NOT EXISTS idx_title_principals_nconst ON title_principals(nconst);
CREATE INDEX IF NOT EXISTS idx_title_principals_tconst ON title_principals(tconst);
CREATE INDEX IF NOT EXISTS idx_name_basics_name ON name_basics(primaryName);

\echo 'Schema creation completed! Ready for data import.';
\echo 'To import data, run: docker-compose run --rm importer';