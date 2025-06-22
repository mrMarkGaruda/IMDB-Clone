-- IMDB Dataset Schema
-- This creates tables matching the IMDB dataset structure

-- Name basics (people information)
CREATE TABLE IF NOT EXISTS name_basics (
    nconst VARCHAR(10) PRIMARY KEY,
    primaryName VARCHAR(255),
    birthYear INTEGER,
    deathYear INTEGER,
    primaryProfession TEXT,
    knownForTitles TEXT
);

-- Title basics (movies/shows information)
CREATE TABLE IF NOT EXISTS title_basics (
    tconst VARCHAR(10) PRIMARY KEY,
    titleType VARCHAR(50),
    primaryTitle VARCHAR(500),
    originalTitle VARCHAR(500),
    isAdult BOOLEAN,
    startYear INTEGER,
    endYear INTEGER,
    runtimeMinutes INTEGER,
    genres TEXT
);

-- Title ratings
CREATE TABLE IF NOT EXISTS title_ratings (
    tconst VARCHAR(10) PRIMARY KEY,
    averageRating DECIMAL(3,1),
    numVotes INTEGER,
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
);

-- Title principals (cast and crew)
CREATE TABLE IF NOT EXISTS title_principals (
    tconst VARCHAR(10),
    ordering INTEGER,
    nconst VARCHAR(10),
    category VARCHAR(50),
    job VARCHAR(255),
    characters TEXT,
    PRIMARY KEY (tconst, ordering),
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst),
    FOREIGN KEY (nconst) REFERENCES name_basics(nconst)
);

-- Title crew (directors and writers)
CREATE TABLE IF NOT EXISTS title_crew (
    tconst VARCHAR(10) PRIMARY KEY,
    directors TEXT,
    writers TEXT,
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst)
);

-- Title episodes (TV episode information)
CREATE TABLE IF NOT EXISTS title_episode (
    tconst VARCHAR(10) PRIMARY KEY,
    parentTconst VARCHAR(10),
    seasonNumber INTEGER,
    episodeNumber INTEGER,
    FOREIGN KEY (tconst) REFERENCES title_basics(tconst),
    FOREIGN KEY (parentTconst) REFERENCES title_basics(tconst)
);

-- Title akas (alternative titles)
CREATE TABLE IF NOT EXISTS title_akas (
    titleId VARCHAR(10),
    ordering INTEGER,
    title VARCHAR(500),
    region VARCHAR(10),
    language VARCHAR(10),
    types TEXT,
    attributes TEXT,
    isOriginalTitle BOOLEAN,
    PRIMARY KEY (titleId, ordering),
    FOREIGN KEY (titleId) REFERENCES title_basics(tconst)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_title_basics_title_type ON title_basics(titleType);
CREATE INDEX IF NOT EXISTS idx_title_basics_start_year ON title_basics(startYear);
CREATE INDEX IF NOT EXISTS idx_title_ratings_rating ON title_ratings(averageRating);
CREATE INDEX IF NOT EXISTS idx_title_principals_nconst ON title_principals(nconst);
CREATE INDEX IF NOT EXISTS idx_title_principals_category ON title_principals(category);
CREATE INDEX IF NOT EXISTS idx_name_basics_name ON name_basics(primaryName);