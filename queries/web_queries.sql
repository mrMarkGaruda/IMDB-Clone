-- Web API Queries for IMDB Clone Frontend
-- These are the actual queries the API will use to serve data to the frontend

-- =====================================================
-- 1. FEATURED CONTENT QUERIES
-- =====================================================

-- Get featured movies (high rated, popular movies from recent years)
-- Query ID: featured_movies
SELECT 
    tb.tconst as id,
    tb.primarytitle as title,
    tb.startyear as year,
    tb.runtimeminutes as runtime,
    tb.genres,
    COALESCE(tr.averagerating, 0) as rating,
    COALESCE(tr.numvotes, 0) as votes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titletype = 'movie'
    AND tb.isadult = false
    AND tb.startyear >= 2015
    AND tb.startyear <= EXTRACT(YEAR FROM CURRENT_DATE)
    AND tr.averagerating >= 7.0
    AND tr.numvotes >= 10000
    AND tb.runtimeminutes IS NOT NULL
ORDER BY tr.averagerating DESC, tr.numvotes DESC
LIMIT 12;

-- Get featured TV series
-- Query ID: featured_series  
SELECT 
    tb.tconst as id,
    tb.primarytitle as title,
    tb.startyear,
    tb.endyear,
    tb.genres,
    COALESCE(tr.averagerating, 0) as rating,
    COALESCE(tr.numvotes, 0) as votes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titletype = 'tvSeries'
    AND tb.startyear >= 2010
    AND tr.averagerating >= 7.5
    AND tr.numvotes >= 5000
ORDER BY tr.averagerating DESC, tr.numvotes DESC
LIMIT 12;

-- Get top rated content (mixed movies and series)
-- Query ID: top_rated
SELECT 
    tb.tconst as id,
    tb.primarytitle as title,
    tb.titletype as type,
    tb.startyear as year,
    COALESCE(tr.averagerating, 0) as rating,
    COALESCE(tr.numvotes, 0) as votes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titletype IN ('movie', 'tvSeries')
    AND tb.isadult = false
    AND tr.averagerating >= 8.5
    AND tr.numvotes >= 25000
ORDER BY tr.averagerating DESC, tr.numvotes DESC
LIMIT 20;

-- =====================================================
-- 2. BROWSE/LIST QUERIES
-- =====================================================

-- Get movies list with filters
-- Query ID: movies_list
-- Parameters: genre, year, min_rating, max_rating, limit, offset
SELECT 
    tb.tconst as id,
    tb.primarytitle as title,
    tb.startyear as year,
    tb.runtimeminutes as runtime,
    COALESCE(tr.averagerating, 0) as rating,
    COALESCE(tr.numvotes, 0) as votes,
    tb.genres,
    tb.isadult
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titletype = 'movie'
    AND ($1::text IS NULL OR tb.genres ILIKE '%' || $1 || '%')
    AND ($2::integer IS NULL OR tb.startyear = $2)
    AND ($3::decimal IS NULL OR tr.averagerating >= $3)
    AND ($4::decimal IS NULL OR tr.averagerating <= $4)
    AND ($5::boolean IS NULL OR tb.isadult = $5)
ORDER BY 
    CASE WHEN $6 = 'rating' THEN tr.averagerating END DESC,
    CASE WHEN $6 = 'year' THEN tb.startyear END DESC,
    CASE WHEN $6 = 'title' THEN tb.primarytitle END ASC,
    tr.numvotes DESC
LIMIT COALESCE($7, 50) OFFSET COALESCE($8, 0);

-- Get TV series list with filters  
-- Query ID: series_list
SELECT 
    tb.tconst as id,
    tb.primarytitle as title,
    tb.startyear,
    tb.endyear,
    COALESCE(tr.averagerating, 0) as rating,
    COALESCE(tr.numvotes, 0) as votes,
    tb.genres
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titletype = 'tvSeries'
    AND ($1::text IS NULL OR tb.genres ILIKE '%' || $1 || '%')
    AND ($2::integer IS NULL OR tb.startyear = $2)
    AND ($3::decimal IS NULL OR tr.averagerating >= $3)
ORDER BY 
    CASE WHEN $4 = 'rating' THEN tr.averagerating END DESC,
    CASE WHEN $4 = 'year' THEN tb.startyear END DESC,
    CASE WHEN $4 = 'title' THEN tb.primarytitle END ASC,
    tr.numvotes DESC
LIMIT COALESCE($5, 50) OFFSET COALESCE($6, 0);

-- Get people list
-- Query ID: people_list  
SELECT 
    nb.nconst as id,
    nb.primaryname as name,
    nb.birthyear,
    nb.deathyear,
    nb.primaryprofession as profession,
    nb.knownfortitles
FROM name_basics nb
WHERE ($1::text IS NULL OR nb.primaryprofession ILIKE '%' || $1 || '%')
    AND ($2::text IS NULL OR nb.primaryname ILIKE '%' || $2 || '%')
    AND nb.primaryprofession IS NOT NULL
ORDER BY nb.primaryname
LIMIT COALESCE($3, 50) OFFSET COALESCE($4, 0);

-- =====================================================
-- 3. SEARCH QUERIES
-- =====================================================

-- Universal search (movies, series, people)
-- Query ID: search
SELECT 
    'title' as result_type,
    tb.tconst as id,
    tb.primarytitle as title,
    tb.titletype as type,
    tb.startyear as year,
    COALESCE(tr.averagerating, 0) as rating,
    tb.genres,
    NULL as name,
    NULL as profession
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titletype IN ('movie', 'tvSeries', 'tvMovie')
    AND tb.isadult = false
    AND tb.primarytitle ILIKE '%' || $1 || '%'

UNION ALL

SELECT 
    'person' as result_type,
    nb.nconst as id,
    NULL as title,
    NULL as type,
    nb.birthyear as year,
    NULL as rating,
    NULL as genres,
    nb.primaryname as name,
    nb.primaryprofession as profession
FROM name_basics nb
WHERE nb.primaryname ILIKE '%' || $1 || '%'
    AND nb.primaryprofession IS NOT NULL

ORDER BY 
    CASE WHEN result_type = 'title' THEN rating END DESC,
    CASE WHEN result_type = 'person' THEN name END ASC,
    title ASC
LIMIT 50;

-- =====================================================
-- 4. DETAIL PAGE QUERIES
-- =====================================================

-- Get movie/series details
-- Query ID: title_details
SELECT 
    tb.tconst as id,
    tb.primarytitle as title,
    tb.originaltitle,
    tb.titletype as type,
    tb.startyear,
    tb.endyear,
    tb.runtimeminutes as runtime,
    tb.genres,
    tb.isadult,
    COALESCE(tr.averagerating, 0) as rating,
    COALESCE(tr.numvotes, 0) as votes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.tconst = $1;

-- Get cast and crew for a title
-- Query ID: title_cast_crew
SELECT 
    tp.nconst as person_id,
    nb.primaryname as name,
    tp.category as role,
    tp.job,
    tp.characters,
    tp.ordering,
    nb.birthyear,
    nb.primaryprofession
FROM title_principals tp
JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE tp.tconst = $1
ORDER BY tp.ordering, tp.category, nb.primaryname
LIMIT 50;

-- Get person details
-- Query ID: person_details
SELECT 
    nb.nconst as id,
    nb.primaryname as name,
    nb.birthyear,
    nb.deathyear,
    nb.primaryprofession as profession,
    nb.knownfortitles
FROM name_basics nb
WHERE nb.nconst = $1;

-- Get person's filmography
-- Query ID: person_filmography
SELECT 
    tb.tconst as id,
    tb.primarytitle as title,
    tb.titletype as type,
    tb.startyear as year,
    tp.category as role,
    tp.job,
    tp.characters,
    COALESCE(tr.averagerating, 0) as rating
FROM title_principals tp
JOIN title_basics tb ON tp.tconst = tb.tconst
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tp.nconst = $1
    AND tb.titletype IN ('movie', 'tvSeries', 'tvMovie')
ORDER BY tb.startyear DESC, tr.averagerating DESC
LIMIT 100;

-- =====================================================
-- 5. ANALYSIS QUERIES
-- =====================================================

-- Get genre statistics
-- Query ID: genre_stats
SELECT 
    TRIM(UNNEST(string_to_array(genres, ','))) as genre,
    COUNT(*) as title_count,
    ROUND(AVG(tr.averagerating), 2) as avg_rating,
    ROUND(AVG(tr.numvotes), 0) as avg_votes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titletype IN ('movie', 'tvSeries')
    AND tb.genres IS NOT NULL
    AND tb.isadult = false
GROUP BY genre
HAVING COUNT(*) >= 100
ORDER BY title_count DESC
LIMIT 20;

-- Get yearly statistics
-- Query ID: yearly_stats
SELECT 
    tb.startyear as year,
    COUNT(*) as title_count,
    ROUND(AVG(tr.averagerating), 2) as avg_rating,
    COUNT(CASE WHEN tb.titletype = 'movie' THEN 1 END) as movie_count,
    COUNT(CASE WHEN tb.titletype = 'tvSeries' THEN 1 END) as series_count
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.startyear BETWEEN 1980 AND EXTRACT(YEAR FROM CURRENT_DATE)
    AND tb.titletype IN ('movie', 'tvSeries')
    AND tb.isadult = false
GROUP BY tb.startyear
ORDER BY tb.startyear DESC
LIMIT 50;

-- Get top directors by average rating
-- Query ID: top_directors
SELECT 
    nb.nconst as id,
    nb.primaryname as name,
    COUNT(DISTINCT tp.tconst) as title_count,
    ROUND(AVG(tr.averagerating), 2) as avg_rating,
    ROUND(AVG(tr.numvotes), 0) as avg_votes
FROM name_basics nb
JOIN title_principals tp ON nb.nconst = tp.nconst
JOIN title_basics tb ON tp.tconst = tb.tconst
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tp.category = 'director'
    AND tb.titletype = 'movie'
    AND tb.isadult = false
    AND tr.averagerating IS NOT NULL
    AND tr.numvotes >= 1000
GROUP BY nb.nconst, nb.primaryname
HAVING COUNT(DISTINCT tp.tconst) >= 3
ORDER BY avg_rating DESC, title_count DESC
LIMIT 25;

-- =====================================================
-- 6. UTILITY QUERIES  
-- =====================================================

-- Get available genres for filters
-- Query ID: available_genres
SELECT DISTINCT TRIM(UNNEST(string_to_array(genres, ','))) as genre
FROM title_basics
WHERE genres IS NOT NULL
    AND titletype IN ('movie', 'tvSeries')
ORDER BY genre;

-- Get year range for filters
-- Query ID: year_range
SELECT 
    MIN(startyear) as min_year,
    MAX(startyear) as max_year
FROM title_basics
WHERE startyear IS NOT NULL
    AND titletype IN ('movie', 'tvSeries')
    AND startyear <= EXTRACT(YEAR FROM CURRENT_DATE);

-- =====================================================
-- 7. QUICK STATS FOR DASHBOARD
-- =====================================================

-- Get quick statistics
-- Query ID: quick_stats
SELECT 
    'movies' as category,
    COUNT(*) as count
FROM title_basics
WHERE titletype = 'movie' AND isadult = false
UNION ALL
SELECT 'series', COUNT(*)
FROM title_basics  
WHERE titletype = 'tvSeries'
UNION ALL
SELECT 'people', COUNT(*)
FROM name_basics
WHERE primaryprofession IS NOT NULL;
