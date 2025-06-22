-- Database Structure Exploration Queries for IMDB Clone
-- These queries help understand the database schema and data relationships

-- =====================================================
-- 1. BASIC TABLE STRUCTURE EXPLORATION
-- =====================================================

-- Check all tables in the database
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Get column information for each table
SELECT table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- =====================================================
-- 2. DATA VOLUME AND SAMPLE EXPLORATION
-- =====================================================

-- Count records in each table
SELECT 'name_basics' as table_name, COUNT(*) as record_count FROM name_basics
UNION ALL
SELECT 'title_basics', COUNT(*) FROM title_basics
UNION ALL
SELECT 'title_ratings', COUNT(*) FROM title_ratings
UNION ALL
SELECT 'title_principals', COUNT(*) FROM title_principals
UNION ALL
SELECT 'title_crew', COUNT(*) FROM title_crew
UNION ALL
SELECT 'title_episode', COUNT(*) FROM title_episode
UNION ALL
SELECT 'title_akas', COUNT(*) FROM title_akas
ORDER BY record_count DESC;

-- =====================================================
-- 3. TITLE_BASICS TABLE EXPLORATION
-- =====================================================

-- Sample of title_basics (movies and shows)
SELECT tconst, titletype, primarytitle, originalTitle, isadult, startyear, endyear, runtimeminutes, genres
FROM title_basics 
LIMIT 10;

-- Count by title type
SELECT titletype, COUNT(*) as count
FROM title_basics
GROUP BY titletype
ORDER BY count DESC;

-- Sample movies (non-adult)
SELECT tconst, primarytitle, startyear, runtimeminutes, genres
FROM title_basics
WHERE titletype = 'movie' 
  AND isadult = false
  AND startyear IS NOT NULL
ORDER BY startyear DESC
LIMIT 20;

-- Sample TV series
SELECT tconst, primarytitle, startyear, endyear, genres
FROM title_basics
WHERE titletype = 'tvSeries'
  AND startyear IS NOT NULL
ORDER BY startyear DESC
LIMIT 20;

-- =====================================================
-- 4. TITLE_RATINGS TABLE EXPLORATION
-- =====================================================

-- Sample of highly rated content
SELECT tb.tconst, tb.primarytitle, tb.titletype, tb.startyear, tr.averagerating, tr.numvotes
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tr.averagerating >= 8.5 
  AND tr.numvotes >= 10000
  AND tb.isadult = false
ORDER BY tr.averagerating DESC, tr.numvotes DESC
LIMIT 25;

-- Rating distribution
SELECT 
  FLOOR(averagerating) as rating_floor,
  COUNT(*) as count,
  AVG(numvotes) as avg_votes
FROM title_ratings
GROUP BY FLOOR(averagerating)
ORDER BY rating_floor DESC;

-- =====================================================
-- 5. NAME_BASICS TABLE EXPLORATION (PEOPLE)
-- =====================================================

-- Sample of people data
SELECT nconst, primaryname, birthyear, deathyear, primaryprofession, knownfortitles
FROM name_basics
WHERE primaryprofession IS NOT NULL
LIMIT 20;

-- Count by primary profession
SELECT 
  TRIM(UNNEST(string_to_array(primaryprofession, ','))) as profession,
  COUNT(*) as count
FROM name_basics
WHERE primaryprofession IS NOT NULL
GROUP BY profession
ORDER BY count DESC
LIMIT 15;

-- Famous directors (sample)
SELECT nconst, primaryname, birthyear, primaryprofession, knownfortitles
FROM name_basics
WHERE primaryprofession LIKE '%director%'
  AND knownfortitles IS NOT NULL
ORDER BY primaryname
LIMIT 20;

-- =====================================================
-- 6. TITLE_PRINCIPALS TABLE EXPLORATION (CAST & CREW)
-- =====================================================

-- Sample of principal data (cast and crew)
SELECT tp.tconst, tb.primarytitle, tp.nconst, nb.primaryname, tp.category, tp.job, tp.characters
FROM title_principals tp
JOIN title_basics tb ON tp.tconst = tb.tconst
JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE tb.titletype = 'movie'
  AND tp.category IN ('actor', 'actress', 'director')
LIMIT 25;

-- Count by category (role type)
SELECT category, COUNT(*) as count
FROM title_principals
WHERE category IS NOT NULL
GROUP BY category
ORDER BY count DESC;

-- =====================================================
-- 7. COMPLEX RELATIONSHIP QUERIES
-- =====================================================

-- Top rated movies with their directors
SELECT 
  tb.primarytitle,
  tb.startyear,
  tr.averagerating,
  tr.numvotes,
  STRING_AGG(DISTINCT nb.primaryname, ', ') as directors
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
JOIN title_principals tp ON tb.tconst = tp.tconst
JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE tb.titletype = 'movie'
  AND tp.category = 'director'
  AND tr.averagerating >= 8.0
  AND tr.numvotes >= 50000
  AND tb.isadult = false
GROUP BY tb.tconst, tb.primarytitle, tb.startyear, tr.averagerating, tr.numvotes
ORDER BY tr.averagerating DESC, tr.numvotes DESC
LIMIT 20;

-- Most prolific actors (by number of titles)
SELECT 
  nb.primaryname,
  nb.birthyear,
  COUNT(DISTINCT tp.tconst) as title_count,
  STRING_AGG(DISTINCT tb.titletype, ', ') as title_types
FROM name_basics nb
JOIN title_principals tp ON nb.nconst = tp.nconst
JOIN title_basics tb ON tp.tconst = tb.tconst
WHERE tp.category IN ('actor', 'actress')
  AND tb.titletype IN ('movie', 'tvSeries')
GROUP BY nb.nconst, nb.primaryname, nb.birthyear
HAVING COUNT(DISTINCT tp.tconst) >= 20
ORDER BY title_count DESC
LIMIT 25;

-- =====================================================
-- 8. GENRE ANALYSIS
-- =====================================================

-- Most common genres
SELECT 
  TRIM(UNNEST(string_to_array(genres, ','))) as genre,
  COUNT(*) as count
FROM title_basics
WHERE genres IS NOT NULL
  AND titletype IN ('movie', 'tvSeries')
GROUP BY genre
ORDER BY count DESC
LIMIT 20;

-- Average rating by genre (for movies)
SELECT 
  TRIM(UNNEST(string_to_array(tb.genres, ','))) as genre,
  COUNT(*) as title_count,
  ROUND(AVG(tr.averagerating), 2) as avg_rating,
  ROUND(AVG(tr.numvotes), 0) as avg_votes
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.genres IS NOT NULL
  AND tb.titletype = 'movie'
  AND tb.isadult = false
GROUP BY genre
HAVING COUNT(*) >= 1000
ORDER BY avg_rating DESC
LIMIT 15;

-- =====================================================
-- 9. TITLE_AKAS TABLE EXPLORATION (ALTERNATIVE TITLES)
-- =====================================================

-- Sample alternative titles
SELECT ta.titleid, tb.primarytitle, ta.title as alternative_title, ta.region, ta.language
FROM title_akas ta
JOIN title_basics tb ON ta.titleid = tb.tconst
WHERE ta.region IS NOT NULL
  AND tb.titletype = 'movie'
LIMIT 20;

-- Count by region
SELECT region, COUNT(*) as count
FROM title_akas
WHERE region IS NOT NULL
GROUP BY region
ORDER BY count DESC
LIMIT 20;

-- =====================================================
-- 10. TEMPORAL ANALYSIS
-- =====================================================

-- Movies per decade
SELECT 
  CONCAT(FLOOR(startyear/10)*10, 's') as decade,
  COUNT(*) as movie_count,
  ROUND(AVG(tr.averagerating), 2) as avg_rating
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titletype = 'movie'
  AND tb.startyear BETWEEN 1920 AND 2024
  AND tb.isadult = false
GROUP BY FLOOR(startyear/10)
ORDER BY decade DESC;

-- =====================================================
-- 11. PERFORMANCE/OPTIMIZATION QUERIES
-- =====================================================

-- Check for indexes
SELECT 
  schemaname,
  tablename,
  indexname,
  indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- =====================================================
-- 12. DATA QUALITY CHECKS
-- =====================================================

-- Check for NULL values in key fields
SELECT 
  'title_basics' as table_name,
  'tconst' as field,
  COUNT(*) as total_records,
  COUNT(tconst) as non_null_records,
  COUNT(*) - COUNT(tconst) as null_records
FROM title_basics
UNION ALL
SELECT 'title_basics', 'primarytitle', COUNT(*), COUNT(primarytitle), COUNT(*) - COUNT(primarytitle) FROM title_basics
UNION ALL
SELECT 'title_ratings', 'averagerating', COUNT(*), COUNT(averagerating), COUNT(*) - COUNT(averagerating) FROM title_ratings
UNION ALL
SELECT 'name_basics', 'primaryname', COUNT(*), COUNT(primaryname), COUNT(*) - COUNT(primaryname) FROM name_basics;

-- Check for data consistency
SELECT 
  'Ratings outside valid range' as check_type,
  COUNT(*) as issue_count
FROM title_ratings
WHERE averagerating < 0 OR averagerating > 10
UNION ALL
SELECT 
  'Future years in title_basics',
  COUNT(*)
FROM title_basics
WHERE startyear > EXTRACT(YEAR FROM CURRENT_DATE)
UNION ALL
SELECT 
  'Invalid birth years',
  COUNT(*)
FROM name_basics
WHERE birthyear < 1800 OR birthyear > EXTRACT(YEAR FROM CURRENT_DATE);
