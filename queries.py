"""
High-performance SQL queries for the IMDB Clone application
Optimized for sub-second execution times with proper indexing
"""

# Part 2: Web Application Queries (< 1 second execution time)

MOVIE_SUMMARY_QUERY = """
-- Movie Summary Page Query
-- Purpose: Get basic movie information with cast and crew
-- Performance: Uses primary key and indexed lookups
SELECT 
    tb.tconst,
    tb.primaryTitle,
    tb.startYear,
    tb.runtimeMinutes,
    tb.genres,
    tr.averageRating,
    tr.numVotes,
    tc.directors,
    tc.writers,
    GROUP_CONCAT(nb.primaryName, ', ') as main_cast
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
LEFT JOIN title_crew tc ON tb.tconst = tc.tconst
LEFT JOIN title_principals tp ON tb.tconst = tp.tconst AND tp.ordering <= 5
LEFT JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE tb.tconst = ? AND tb.titleType = 'movie'
GROUP BY tb.tconst
"""

MOVIE_DETAILS_QUERY = """
-- Movie Details Page Query
-- Purpose: Get detailed movie information including alternative titles
-- Performance: Uses foreign key relationships with indexes
SELECT 
    tb.tconst,
    tb.primaryTitle,
    tb.originalTitle,
    tb.startYear,
    tb.endYear,
    tb.runtimeMinutes,
    tb.genres,
    tb.isAdult,
    GROUP_CONCAT(DISTINCT ta.title || ' (' || ta.region || ')') as alternative_titles
FROM title_basics tb
LEFT JOIN title_akas ta ON tb.tconst = ta.titleId
WHERE tb.tconst = ?
GROUP BY tb.tconst
"""

CAST_CREW_QUERY = """
-- Complete Cast/Crew Page Query
-- Purpose: Get full cast and crew listing for a title
-- Performance: Uses indexed joins, sorted by category
SELECT 
    tp.ordering,
    nb.nconst,
    nb.primaryName,
    tp.category,
    tp.job,
    tp.characters
FROM title_principals tp
JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE tp.tconst = ?
ORDER BY 
    CASE tp.category 
        WHEN 'director' THEN 1
        WHEN 'writer' THEN 2
        WHEN 'producer' THEN 3
        WHEN 'actor' THEN 4
        WHEN 'actress' THEN 4
        ELSE 5 
    END,
    tp.ordering
"""

TV_SERIES_SUMMARY_QUERY = """
-- TV Series Summary Page Query
-- Purpose: Get series overview with season count and main cast
-- Performance: Uses aggregation with proper indexes
SELECT 
    tb.tconst,
    tb.primaryTitle,
    tb.startYear,
    tb.endYear,
    tb.genres,
    tr.averageRating,
    tr.numVotes,
    COUNT(DISTINCT te.seasonNumber) as season_count,
    COUNT(DISTINCT te.tconst) as episode_count,
    GROUP_CONCAT(DISTINCT nb.primaryName, ', ') as main_cast
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
LEFT JOIN title_episode te ON tb.tconst = te.parentTconst
LEFT JOIN title_principals tp ON tb.tconst = tp.tconst AND tp.ordering <= 10
LEFT JOIN name_basics nb ON tp.nconst = nb.nconst
WHERE tb.tconst = ? AND tb.titleType = 'tvSeries'
GROUP BY tb.tconst
"""

EPISODE_DETAILS_QUERY = """
-- Episode Page Query
-- Purpose: Get episode-specific details with guest stars
-- Performance: Uses episode-specific indexes
SELECT 
    tb.tconst,
    tb.primaryTitle,
    te.seasonNumber,
    te.episodeNumber,
    te.parentTconst,
    parent.primaryTitle as series_title,
    tb.startYear,
    tr.averageRating,
    tr.numVotes
FROM title_basics tb
JOIN title_episode te ON tb.tconst = te.tconst
JOIN title_basics parent ON te.parentTconst = parent.tconst
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.tconst = ?
"""

PERSON_FILMOGRAPHY_QUERY = """
-- Person Page Query
-- Purpose: Get complete filmography categorized by role
-- Performance: Uses person-centric indexes
SELECT 
    tb.tconst,
    tb.primaryTitle,
    tb.titleType,
    tb.startYear,
    tp.category,
    tp.characters,
    tr.averageRating
FROM title_principals tp
JOIN title_basics tb ON tp.tconst = tb.tconst
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tp.nconst = ?
ORDER BY tb.startYear DESC, tr.averageRating DESC
"""

MOVIE_LISTING_QUERY = """
-- Movie Listing Page Query with Filters
-- Purpose: Filterable movie listing with pagination
-- Performance: Uses multiple indexes for fast filtering
SELECT 
    tb.tconst,
    tb.primaryTitle,
    tb.startYear,
    tb.runtimeMinutes,
    tb.genres,
    tr.averageRating,
    tr.numVotes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie'
    AND (? IS NULL OR tb.startYear >= ?)
    AND (? IS NULL OR tb.startYear <= ?)
    AND (? IS NULL OR tb.genres LIKE '%' || ? || '%')
    AND (? IS NULL OR tr.averageRating >= ?)
    AND (? IS NULL OR tb.isAdult = ?)
ORDER BY tr.numVotes DESC, tr.averageRating DESC
LIMIT ? OFFSET ?
"""

SEARCH_TITLES_QUERY = """
-- Search Engine Query
-- Purpose: Full-text search across titles
-- Performance: Uses LIKE with leading wildcards minimized
SELECT 
    tb.tconst,
    tb.primaryTitle,
    tb.titleType,
    tb.startYear,
    tr.averageRating,
    tr.numVotes
FROM title_basics tb
LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.primaryTitle LIKE ? OR tb.originalTitle LIKE ?
ORDER BY 
    CASE 
        WHEN tb.primaryTitle LIKE ? THEN 1
        WHEN tb.primaryTitle LIKE ? THEN 2
        ELSE 3
    END,
    tr.numVotes DESC
LIMIT 50
"""

# Part 3: Data Analysis Queries (Advanced SQL with Window Functions)

RATING_TRENDS_BY_YEAR = """
-- Rating Trends Analysis by Year
-- Purpose: Show how movie ratings evolved over decades
-- Uses: Window functions for rolling averages
SELECT 
    startYear,
    COUNT(*) as movie_count,
    AVG(tr.averageRating) as avg_rating,
    AVG(AVG(tr.averageRating)) OVER (
        ORDER BY startYear 
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) as rolling_5yr_avg
FROM title_basics tb
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie' 
    AND tb.startYear BETWEEN 1950 AND 2023
    AND tr.numVotes >= 100
GROUP BY startYear
ORDER BY startYear
"""

GENRE_PERFORMANCE_ANALYSIS = """
-- Genre Performance Analysis
-- Purpose: Compare genre popularity and success over time
-- Uses: Advanced aggregation and window functions
WITH genre_stats AS (
    SELECT 
        TRIM(genre_split.value) as genre,
        COUNT(*) as total_movies,
        AVG(tr.averageRating) as avg_rating,
        SUM(tr.numVotes) as total_votes,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tr.averageRating) as median_rating
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst,
    json_each('["' || replace(tb.genres, ',', '","') || '"]') as genre_split
    WHERE tb.titleType = 'movie' 
        AND tb.genres IS NOT NULL
        AND tr.numVotes >= 50
    GROUP BY genre
    HAVING total_movies >= 100
)
SELECT 
    genre,
    total_movies,
    avg_rating,
    median_rating,
    total_votes,
    RANK() OVER (ORDER BY avg_rating DESC) as rating_rank,
    RANK() OVER (ORDER BY total_movies DESC) as popularity_rank
FROM genre_stats
ORDER BY avg_rating DESC
"""

DIRECTOR_SUCCESS_ANALYSIS = """
-- Directors' Performance Analysis
-- Purpose: Analyze directors' career success patterns
-- Uses: Window functions, HAVING clause, and complex joins
SELECT 
    nb.nconst,
    nb.primaryName,
    COUNT(DISTINCT tb.tconst) as movies_directed,
    AVG(tr.averageRating) as avg_rating,
    SUM(tr.numVotes) as total_votes,
    MIN(tb.startYear) as career_start,
    MAX(tb.startYear) as career_end,
    MAX(tb.startYear) - MIN(tb.startYear) as career_span,
    RANK() OVER (ORDER BY AVG(tr.averageRating) DESC) as rating_rank
FROM name_basics nb
JOIN title_crew tc ON nb.nconst IN (
    SELECT TRIM(value) 
    FROM json_each('["' || replace(tc.directors, ',', '","') || '"]')
)
JOIN title_basics tb ON tc.tconst = tb.tconst
JOIN title_ratings tr ON tb.tconst = tr.tconst
WHERE tb.titleType = 'movie'
    AND tr.numVotes >= 1000
GROUP BY nb.nconst, nb.primaryName
HAVING movies_directed >= 5
ORDER BY avg_rating DESC
LIMIT 50
"""

COLLABORATION_NETWORK_ANALYSIS = """
-- Collaboration Network Analysis
-- Purpose: Find frequent collaborations between actors and directors
-- Uses: Self-joins and advanced grouping
WITH actor_director_pairs AS (
    SELECT 
        tp_actor.nconst as actor_id,
        nb_actor.primaryName as actor_name,
        director_ids.director_id,
        nb_director.primaryName as director_name,
        COUNT(*) as collaborations
    FROM title_principals tp_actor
    JOIN name_basics nb_actor ON tp_actor.nconst = nb_actor.nconst
    JOIN (
        SELECT tc.tconst, TRIM(value) as director_id
        FROM title_crew tc,
        json_each('["' || replace(tc.directors, ',', '","') || '"]')
    ) director_ids ON tp_actor.tconst = director_ids.tconst
    JOIN name_basics nb_director ON director_ids.director_id = nb_director.nconst
    JOIN title_basics tb ON tp_actor.tconst = tb.tconst
    WHERE tp_actor.category IN ('actor', 'actress')
        AND tb.titleType = 'movie'
    GROUP BY tp_actor.nconst, director_ids.director_id
    HAVING collaborations >= 3
)
SELECT 
    actor_name,
    director_name,
    collaborations,
    RANK() OVER (ORDER BY collaborations DESC) as collaboration_rank
FROM actor_director_pairs
ORDER BY collaborations DESC
LIMIT 100
"""

GENRE_EVOLUTION_ANALYSIS = """
-- Genre Evolution Over Decades
-- Purpose: Show how genre preferences changed over time
-- Uses: Window functions and temporal analysis
SELECT 
    decade,
    genre,
    movie_count,
    pct_of_decade,
    RANK() OVER (PARTITION BY decade ORDER BY movie_count DESC) as genre_rank_in_decade
FROM (
    SELECT 
        (startYear / 10) * 10 as decade,
        TRIM(genre_split.value) as genre,
        COUNT(*) as movie_count,
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY (startYear / 10) * 10) as pct_of_decade
    FROM title_basics tb
    JOIN title_ratings tr ON tb.tconst = tr.tconst,
    json_each('["' || replace(tb.genres, ',', '","') || '"]') as genre_split
    WHERE tb.titleType = 'movie' 
        AND tb.startYear BETWEEN 1950 AND 2020
        AND tr.numVotes >= 100
    GROUP BY decade, genre
    HAVING movie_count >= 10
) genre_decade_stats
WHERE decade >= 1950
ORDER BY decade, genre_rank_in_decade
"""

# Performance Optimization Queries

CREATE_PERFORMANCE_INDEXES = """
-- Additional performance indexes for complex queries
CREATE INDEX IF NOT EXISTS idx_title_basics_composite ON title_basics(titleType, startYear, isAdult);
CREATE INDEX IF NOT EXISTS idx_title_ratings_composite ON title_ratings(averageRating, numVotes);
CREATE INDEX IF NOT EXISTS idx_principals_composite ON title_principals(tconst, category, ordering);
CREATE INDEX IF NOT EXISTS idx_episode_season ON title_episode(parentTconst, seasonNumber);
CREATE INDEX IF NOT EXISTS idx_name_basics_name ON name_basics(primaryName);
CREATE INDEX IF NOT EXISTS idx_title_basics_title ON title_basics(primaryTitle);
"""

# Query execution helper functions would go here in a full implementation
