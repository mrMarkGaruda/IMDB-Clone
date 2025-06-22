-- IMDB Dataset Schema
-- This creates tables matching the IMDB dataset structure exactly as per official documentation
-- Column names match the actual TSV file headers exactly (quoted to preserve case)

-- Name basics (people information)
-- Matches: name.basics.tsv.gz
CREATE TABLE IF NOT EXISTS name_basics (
    "nconst" VARCHAR(15) PRIMARY KEY,
    "primaryName" TEXT,
    "birthYear" INTEGER,
    "deathYear" INTEGER,
    "primaryProfession" TEXT,
    "knownForTitles" TEXT
);

-- Title basics (movies/shows information)  
-- Matches: title.basics.tsv.gz
CREATE TABLE IF NOT EXISTS title_basics (
    "tconst" VARCHAR(15) PRIMARY KEY,
    "titleType" VARCHAR(50),
    "primaryTitle" TEXT,
    "originalTitle" TEXT,
    "isAdult" BOOLEAN,
    "startYear" INTEGER,
    "endYear" INTEGER,
    "runtimeMinutes" INTEGER,
    "genres" TEXT
);

-- Title ratings
-- Matches: title.ratings.tsv.gz
CREATE TABLE IF NOT EXISTS title_ratings (
    "tconst" VARCHAR(15) PRIMARY KEY,
    "averageRating" DECIMAL(3,1),
    "numVotes" INTEGER,
    FOREIGN KEY ("tconst") REFERENCES title_basics("tconst")
);

-- Title principals (cast and crew)
-- Matches: title.principals.tsv.gz
CREATE TABLE IF NOT EXISTS title_principals (
    "tconst" VARCHAR(15),
    "ordering" INTEGER,
    "nconst" VARCHAR(15),
    "category" VARCHAR(100),
    "job" TEXT,
    "characters" TEXT,
    PRIMARY KEY ("tconst", "ordering"),
    FOREIGN KEY ("tconst") REFERENCES title_basics("tconst"),
    FOREIGN KEY ("nconst") REFERENCES name_basics("nconst")
);

-- Title crew (directors and writers)
-- Matches: title.crew.tsv.gz
CREATE TABLE IF NOT EXISTS title_crew (
    "tconst" VARCHAR(15) PRIMARY KEY,
    "directors" TEXT,
    "writers" TEXT,
    FOREIGN KEY ("tconst") REFERENCES title_basics("tconst")
);

-- Title episodes (TV episode information)
-- Matches: title.episode.tsv.gz
CREATE TABLE IF NOT EXISTS title_episode (
    "tconst" VARCHAR(15) PRIMARY KEY,
    "parentTconst" VARCHAR(15),
    "seasonNumber" INTEGER,
    "episodeNumber" INTEGER,
    FOREIGN KEY ("tconst") REFERENCES title_basics("tconst"),
    FOREIGN KEY ("parentTconst") REFERENCES title_basics("tconst")
);

-- Title akas (alternative titles)
-- Matches: title.akas.tsv.gz
CREATE TABLE IF NOT EXISTS title_akas (
    "titleId" VARCHAR(15),
    "ordering" INTEGER,
    "title" TEXT,
    "region" VARCHAR(10),
    "language" VARCHAR(10),
    "types" TEXT,
    "attributes" TEXT,
    "isOriginalTitle" BOOLEAN,
    PRIMARY KEY ("titleId", "ordering"),
    FOREIGN KEY ("titleId") REFERENCES title_basics("tconst")
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_title_basics_title_type ON title_basics("titleType");
CREATE INDEX IF NOT EXISTS idx_title_basics_start_year ON title_basics("startYear");
CREATE INDEX IF NOT EXISTS idx_title_ratings_rating ON title_ratings("averageRating");
CREATE INDEX IF NOT EXISTS idx_title_principals_nconst ON title_principals("nconst");
CREATE INDEX IF NOT EXISTS idx_title_principals_category ON title_principals("category");
CREATE INDEX IF NOT EXISTS idx_name_basics_name ON name_basics("primaryName");