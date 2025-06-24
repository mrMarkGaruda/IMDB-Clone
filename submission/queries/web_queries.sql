-- Web Application Queries for IMDb Clone
-- Each query is commented with its purpose and optimization notes

-- 1. Home Page - Database Statistics
-- Get movie count
SELECT COUNT(*) as count FROM title_basics WHERE titleType = "movie";

-- Get TV series count  
SELECT COUNT(*) as count FROM title_basics WHERE titleType = "tvSeries";

-- Get people count
SELECT COUNT(*) as count FROM name_basics;

-- Get ratings count
SELECT COUNT(*) as count FROM title_ratings;

-- Get top rated movies for homepage
SELECT tb.tconst, tb.primaryTitle, tb.startYear, tr.averageRating, tr.numVotes
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie' AND tr.numVotes >= 1000
ORDER BY tr.averageRating DESC, tr.numVotes DESC
LIMIT 10;

-- 2. Movies Listing Page (with filters and pagination)
-- Base query with optional filters for genre, year, rating, adult content
SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.runtimeMinutes, 
       tb.genres, tr.averageRating, tr.numVotes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie'
  AND (? IS NULL OR tb.genres LIKE '%' || ? || '%')  -- genre filter
  AND (? IS NULL OR tb.startYear = ?)                -- year filter
  AND (? IS NULL OR tr.averageRating >= ?)           -- min rating filter
  AND (? IS NULL OR tb.isAdult = ?)                  -- adult content filter
ORDER BY tr.averageRating DESC, tr.numVotes DESC 
LIMIT ? OFFSET ?;

-- 3. Movie Details Page
-- Shows complete movie information including ratings
SELECT tb.*, tr.averageRating, tr.numVotes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.tconst = ?;

-- 4. Movie Cast and Crew Page
-- Shows cast and crew for a specific movie, ordered by importance
SELECT nb.nconst, nb.primaryName, tp.category, tp.characters, tp.job
FROM title_principals tp
JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE tp.tconst = ?
ORDER BY tp.ordering
LIMIT 20;

-- 5. Alternative Titles Page
-- Shows alternative titles for a movie/show
SELECT *
FROM title_akas
WHERE titleId = ?;

-- 6. Person Details Page
-- Shows person information
SELECT *
FROM name_basics
WHERE nconst = ?;

-- 7. Person Filmography
-- Shows complete filmography for a person, ordered by year
SELECT tb.primaryTitle, tb.startYear, tp.category, tp.job, tp.characters
FROM title_principals tp
JOIN title_basics tb ON tp.tconst = tb.tconst
WHERE tp.nconst = ?
ORDER BY tb.startYear DESC;

-- 8. Search Movies and TV Series
-- Search functionality across titles
SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.titleType,
       tr.averageRating, tr.numVotes, 'movie' as result_type
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.primaryTitle LIKE ? AND tb.titleType IN ('movie', 'tvSeries')
ORDER BY COALESCE(tr.numVotes, 0) DESC
LIMIT 20;

-- 9. Search People
-- Search functionality for actors, directors, etc.
SELECT nb.nconst, nb.primaryName, nb.birthYear, nb.primaryProfession,
       'person' as result_type
FROM name_basics nb
WHERE nb.primaryName LIKE ?
ORDER BY nb.primaryName
LIMIT 10;
