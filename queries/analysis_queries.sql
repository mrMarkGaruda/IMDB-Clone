-- Data Analysis Queries for IMDb Clone
-- Each query is commented with its purpose and optimization notes

-- 1. Rating Trends by Year (Used in analysis dashboard)
SELECT tb.startYear, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie' AND tb.startYear BETWEEN 1980 AND 2023
    AND tr.numVotes >= 100
GROUP BY tb.startYear
HAVING COUNT(*) >= 10
ORDER BY tb.startYear;

-- 2. Genre Popularity Analysis (Used in analysis dashboard)
SELECT 
    CASE 
        WHEN genres LIKE '%Action%' THEN 'Action'
        WHEN genres LIKE '%Drama%' THEN 'Drama'
        WHEN genres LIKE '%Comedy%' THEN 'Comedy'
        WHEN genres LIKE '%Thriller%' THEN 'Thriller'
        WHEN genres LIKE '%Horror%' THEN 'Horror'
        WHEN genres LIKE '%Romance%' THEN 'Romance'
        ELSE 'Other'
    END as genre,
    COUNT(*) as count,
    AVG(tr.averageRating) as avg_rating
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie' AND tr.numVotes >= 1000
GROUP BY genre
ORDER BY count DESC
LIMIT 10;

-- 3. Top Directors Analysis (Used in analysis dashboard)
SELECT nb.primaryName, COUNT(*) as movie_count, AVG(tr.averageRating) as avg_rating
FROM name_basics nb
JOIN title_principals tp ON nb.nconst = tp.nconst AND tp.category = "director"
JOIN title_basics tb ON tp.tconst = tb.tconst AND tb.titleType = "movie"
JOIN title_ratings tr ON tb.tconst = tr.tconst
GROUP BY nb.primaryName
HAVING movie_count >= 3
ORDER BY avg_rating DESC, movie_count DESC
LIMIT 10;

-- 4. Actor Collaboration Analysis (Used in analysis dashboard)
SELECT a1.primaryName as actor1, a2.primaryName as actor2, COUNT(*) as movies_together
FROM title_principals tp1
JOIN title_principals tp2 ON tp1.tconst = tp2.tconst AND tp1.nconst < tp2.nconst
JOIN name_basics a1 ON tp1.nconst = a1.nconst AND tp1.category IN ("actor","actress")
JOIN name_basics a2 ON tp2.nconst = a2.nconst AND tp2.category IN ("actor","actress")
WHERE tp1.category IN ("actor","actress") AND tp2.category IN ("actor","actress")
GROUP BY actor1, actor2
HAVING movies_together >= 3
ORDER BY movies_together DESC, actor1, actor2
LIMIT 10;
