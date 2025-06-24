-- Data Analysis Queries for IMDb Clone
-- Each query is commented with its purpose and optimization notes

-- 1. Rating Trends by Year
SELECT tb.startYear, COUNT(*) as movie_count, AVG(tr.averageRating) as avg_rating
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie' AND tb.startYear BETWEEN 1950 AND 2023
GROUP BY tb.startYear
HAVING COUNT(*) >= 20
ORDER BY tb.startYear;

-- 2. Genre Popularity Over Time
SELECT tb.genres, tb.startYear, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie' AND tb.startYear BETWEEN 1980 AND 2023
GROUP BY tb.genres, tb.startYear
ORDER BY tb.genres, tb.startYear;

-- 3. Director Performance Analysis
SELECT nb.primaryName as director, COUNT(*) as movie_count, AVG(tr.averageRating) as avg_director_rating
FROM name_basics nb
JOIN title_principals tp ON nb.nconst = tp.nconst AND tp.category = 'director'
JOIN title_basics tb ON tp.tconst = tb.tconst AND tb.titleType = 'movie'
JOIN title_ratings tr ON tb.tconst = tr.tconst
GROUP BY nb.primaryName
HAVING COUNT(*) >= 5
ORDER BY avg_director_rating DESC, movie_count DESC
LIMIT 20;

-- 4. Actor Collaboration Network (Top Pairs)
SELECT a1.primaryName as actor1, a2.primaryName as actor2, COUNT(*) as movies_together
FROM title_principals tp1
JOIN title_principals tp2 ON tp1.tconst = tp2.tconst AND tp1.nconst < tp2.nconst
JOIN name_basics a1 ON tp1.nconst = a1.nconst AND tp1.category IN ('actor','actress')
JOIN name_basics a2 ON tp2.nconst = a2.nconst AND tp2.category IN ('actor','actress')
WHERE tp1.category IN ('actor','actress') AND tp2.category IN ('actor','actress')
GROUP BY actor1, actor2
HAVING movies_together >= 3
ORDER BY movies_together DESC, actor1, actor2
LIMIT 20;
