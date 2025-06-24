-- Web Application Queries for IMDb Clone
-- Each query is commented with its purpose and optimization notes

-- 1. Movie Summary Page
-- Shows title, year, length, directors, writers, main cast (top 5), rating, votes
SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.runtimeMinutes, tb.genres,
       tr.averageRating, tr.numVotes, tc.directors, tc.writers,
       GROUP_CONCAT(nb.primaryName, ', ') as main_cast
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
LEFT JOIN title_crew tc ON tb.tconst = tc.tconst
LEFT JOIN title_principals tp ON tb.tconst = tp.tconst AND tp.ordering <= 5
LEFT JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE tb.tconst = ? AND tb.titleType = 'movie'
GROUP BY tb.tconst;

-- 2. Movie Details Page
-- Shows alternative titles, production details, full technical details
SELECT tb.tconst, tb.primaryTitle, tb.originalTitle, tb.startYear, tb.endYear, tb.runtimeMinutes, tb.genres, tb.isAdult,
       GROUP_CONCAT(DISTINCT ta.title || ' (' || ta.region || ')') as alternative_titles
FROM title_basics tb
LEFT JOIN title_akas ta ON tb.tconst = ta.titleId
WHERE tb.tconst = ?
GROUP BY tb.tconst;

-- 3. Complete Cast/Crew Page
-- All actors with roles, full crew listing, sorted by categories
SELECT tp.ordering, nb.nconst, nb.primaryName, tp.category, tp.job, tp.characters
FROM title_principals tp
JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE tp.tconst = ?
ORDER BY CASE tp.category WHEN 'director' THEN 1 WHEN 'writer' THEN 2 WHEN 'producer' THEN 3 WHEN 'actor' THEN 4 WHEN 'actress' THEN 4 ELSE 5 END, tp.ordering;

-- 4. TV Series Summary Page
-- Series overview, seasons count, years active, main cast, general rating
SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.endYear, tb.genres, tr.averageRating, tr.numVotes,
       (SELECT COUNT(DISTINCT seasonNumber) FROM title_episode te WHERE te.parentTconst = tb.tconst) as seasons_count
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'tvSeries' AND tb.tconst = ?;

-- 5. TV Series Details Page
-- Season-by-season breakdown, cast changes, production details
SELECT te.seasonNumber, COUNT(*) as episode_count, AVG(tr.averageRating) as avg_season_rating
FROM title_episode te
JOIN title_basics tb ON te.tconst = tb.tconst
LEFT JOIN title_ratings tr ON te.tconst = tr.tconst
WHERE te.parentTconst = ?
GROUP BY te.seasonNumber
ORDER BY te.seasonNumber;

-- 6. Person Page
-- Basic info, complete filmography, categorized by role type
SELECT nb.nconst, nb.primaryName, nb.birthYear, nb.deathYear, nb.primaryProfession, tp.category, tb.primaryTitle, tb.startYear, tb.titleType
FROM name_basics nb
LEFT JOIN title_principals tp ON nb.nconst = tp.nconst
LEFT JOIN title_basics tb ON tp.tconst = tb.tconst
WHERE nb.nconst = ?
ORDER BY tb.startYear DESC;

-- 7. Movie Listing Page (with filters)
-- Filterable by genre, year, rating, adult content
SELECT tb.tconst, tb.primaryTitle, tb.startYear, tb.genres, tr.averageRating, tr.numVotes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie'
  AND (? IS NULL OR tb.genres LIKE '%' || ? || '%')
  AND (? IS NULL OR tb.startYear >= ?)
  AND (? IS NULL OR tb.startYear <= ?)
  AND (? IS NULL OR tr.averageRating >= ?)
  AND (? IS NULL OR tb.isAdult = ?)
ORDER BY tr.averageRating DESC, tr.numVotes DESC
LIMIT ? OFFSET ?;
