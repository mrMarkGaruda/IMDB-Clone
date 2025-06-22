const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3001;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

// PostgreSQL connection
const pool = new Pool({
    user: process.env.POSTGRES_USER || 'imdbuser',
    host: process.env.POSTGRES_HOST || 'localhost',
    database: process.env.POSTGRES_DB || 'imdb',
    password: process.env.POSTGRES_PASSWORD || 'imdbpass',
    port: process.env.POSTGRES_PORT || 5432,
});

// Test database connection
pool.connect((err, client, release) => {
    if (err) {
        console.error('Error connecting to database:', err);
    } else {
        console.log('Successfully connected to PostgreSQL database');
        release();
    }
});

// API Routes

// Featured Movies
app.get('/api/featured_movies', async (req, res) => {
    try {
        const query = `
            SELECT tb."tconst" as id, tb."primaryTitle" as title, 
                   tb."startYear" as year, tb."genres",
                   tr."averageRating" as rating, tr."numVotes" as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."titleType" = 'movie' 
                AND tr."averageRating" >= 8.0 
                AND tr."numVotes" >= 100000
            ORDER BY tr."averageRating" DESC, tr."numVotes" DESC
            LIMIT 12
        `;
        const result = await pool.query(query);
        res.json(result.rows);
    } catch (err) {
        console.error('Error fetching featured movies:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Featured Series
app.get('/api/featured_series', async (req, res) => {
    try {
        const query = `
            SELECT tb."tconst" as id, tb."primaryTitle" as title, 
                   tb."startYear", tb."endYear", tb."genres",
                   tr."averageRating" as rating, tr."numVotes" as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."titleType" IN ('tvSeries', 'tvMiniSeries') 
                AND tr."averageRating" >= 8.0 
                AND tr."numVotes" >= 10000
            ORDER BY tr."averageRating" DESC, tr."numVotes" DESC
            LIMIT 12
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            ...row,
            startYear: row.startYear,
            endYear: row.endYear
        })));
    } catch (err) {
        console.error('Error fetching featured series:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Top Rated Content
app.get('/api/top_rated', async (req, res) => {
    try {
        const query = `
            SELECT tb."tconst" as id, tb."primaryTitle" as title, 
                   tb."startYear" as year, tb."titleType" as type,
                   tr."averageRating" as rating, tr."numVotes" as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."titleType" IN ('movie', 'tvSeries', 'tvMiniSeries') 
                AND tr."averageRating" >= 8.5 
                AND tr."numVotes" >= 50000
            ORDER BY tr."averageRating" DESC, tr."numVotes" DESC
            LIMIT 20
        `;
        const result = await pool.query(query);
        res.json(result.rows);
    } catch (err) {
        console.error('Error fetching top rated content:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Movies List
app.get('/api/movies_list', async (req, res) => {
    try {
        const query = `
            SELECT tb."tconst" as id, tb."primaryTitle" as title, 
                   tb."startYear" as year, tb."runtimeMinutes" as runtime,
                   tb."genres", tb."isAdult",
                   tr."averageRating" as rating, tr."numVotes" as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."titleType" = 'movie' 
                AND tb."startYear" IS NOT NULL
                AND tr."numVotes" >= 1000
            ORDER BY tr."numVotes" DESC, tr."averageRating" DESC
            LIMIT 100
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            ...row,
            isAdult: row.isAdult === true
        })));
    } catch (err) {
        console.error('Error fetching movies list:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Series List
app.get('/api/series_list', async (req, res) => {
    try {
        const query = `
            SELECT tb."tconst" as id, tb."primaryTitle" as title, 
                   tb."startYear", tb."endYear", tb."genres",
                   tr."averageRating" as rating, tr."numVotes" as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."titleType" IN ('tvSeries', 'tvMiniSeries') 
                AND tb."startYear" IS NOT NULL
                AND tr."numVotes" >= 1000
            ORDER BY tr."numVotes" DESC, tr."averageRating" DESC
            LIMIT 100
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            ...row,
            startYear: row.startYear,
            endYear: row.endYear
        })));
    } catch (err) {
        console.error('Error fetching series list:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// People List
app.get('/api/people_list', async (req, res) => {
    try {
        const query = `
            SELECT nb."nconst" as id, nb."primaryName" as name, 
                   nb."birthYear", nb."deathYear", nb."primaryProfession" as profession
            FROM name_basics nb
            WHERE nb."primaryProfession" IS NOT NULL
            ORDER BY nb."primaryName"
            LIMIT 100
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            ...row,
            birthYear: row.birthYear,
            deathYear: row.deathYear
        })));
    } catch (err) {
        console.error('Error fetching people list:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Search
app.get('/api/search', async (req, res) => {
    try {
        const { q } = req.query;
        if (!q) {
            return res.json([]);
        }

        const searchTerm = `%${q.toLowerCase()}%`;
          // Search titles
        const titleQuery = `
            SELECT tb."tconst" as id, tb."primaryTitle" as title, 
                   tb."startYear" as year, tb."titleType",
                   tr."averageRating" as rating, 'title' as type
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE LOWER(tb."primaryTitle") LIKE $1
                AND tb."titleType" IN ('movie', 'tvSeries', 'tvMiniSeries')
            ORDER BY tr."numVotes" DESC NULLS LAST
            LIMIT 20
        `;
        
        // Search people
        const peopleQuery = `
            SELECT nb."nconst" as id, nb."primaryName" as name, 
                   nb."birthYear", nb."deathYear", nb."primaryProfession" as profession,
                   'person' as type
            FROM name_basics nb
            WHERE LOWER(nb."primaryName") LIKE $1
            ORDER BY nb."primaryName"
            LIMIT 20
        `;
        
        const [titleResults, peopleResults] = await Promise.all([
            pool.query(titleQuery, [searchTerm]),
            pool.query(peopleQuery, [searchTerm])
        ]);
        
        const results = [
            ...titleResults.rows.map(row => ({
                ...row,
                titleType: row.titleType,
                birthYear: row.birthYear,
                deathYear: row.deathYear
            })),
            ...peopleResults.rows.map(row => ({
                ...row,
                birthYear: row.birthYear,
                deathYear: row.deathYear
            }))
        ];
        
        res.json(results);
    } catch (err) {
        console.error('Error searching:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Movie Details
app.get('/api/movie_details/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const query = `
            SELECT tb."tconst" as id, tb."primaryTitle" as title, 
                   tb."startYear" as year, tb."runtimeMinutes" as runtime,
                   tb."genres",
                   tr."averageRating" as rating, tr."numVotes" as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."tconst" = $1
        `;
        const result = await pool.query(query, [id]);
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Movie not found' });
        }
        
        res.json(result.rows[0]);
    } catch (err) {
        console.error('Error fetching movie details:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Movie Cast & Crew
app.get('/api/movie_cast_crew/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const query = `
            SELECT nb."nconst" as id, nb."primaryName" as name, 
                   tp."category", tp."characters", tp."job"
            FROM title_principals tp
            JOIN name_basics nb ON tp."nconst" = nb."nconst"
            WHERE tp."tconst" = $1
            ORDER BY tp."ordering"
            LIMIT 20
        `;
        const result = await pool.query(query, [id]);
        res.json(result.rows);
    } catch (err) {
        console.error('Error fetching cast and crew:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Analysis endpoints
app.get('/api/rating_trends', async (req, res) => {
    try {
        const query = `
            SELECT tb."startYear" as year, 
                   AVG(tr."averageRating") as avgrating,
                   COUNT(*) as count
            FROM title_basics tb
            JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."startYear" BETWEEN 2000 AND 2023
                AND tb."titleType" IN ('movie', 'tvSeries')
                AND tr."numVotes" >= 1000
            GROUP BY tb."startYear"
            ORDER BY tb."startYear"
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            year: row.year,
            avgRating: parseFloat(row.avgrating).toFixed(2)
        })));
    } catch (err) {
        console.error('Error fetching rating trends:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/api/genre_analysis', async (req, res) => {
    try {
        const query = `
            SELECT genre, COUNT(*) as count
            FROM (
                SELECT unnest(string_to_array(tb."genres", ',')) as genre
                FROM title_basics tb
                JOIN title_ratings tr ON tb."tconst" = tr."tconst"
                WHERE tb."titleType" IN ('movie', 'tvSeries')
                    AND tb."genres" IS NOT NULL
                    AND tr."numVotes" >= 1000
            ) genre_list
            WHERE genre != ''
            GROUP BY genre
            ORDER BY count DESC
            LIMIT 15
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            name: row.genre,
            count: parseInt(row.count)
        })));
    } catch (err) {
        console.error('Error fetching genre analysis:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/api/year_analysis', async (req, res) => {
    try {
        const query = `
            SELECT tb."startYear" as year, COUNT(*) as count
            FROM title_basics tb
            JOIN title_ratings tr ON tb."tconst" = tr."tconst"
            WHERE tb."startYear" BETWEEN 2010 AND 2023
                AND tb."titleType" IN ('movie', 'tvSeries')
                AND tr."numVotes" >= 1000
            GROUP BY tb."startYear"
            ORDER BY tb."startYear" DESC
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            year: row.year,
            count: parseInt(row.count)
        })));
    } catch (err) {
        console.error('Error fetching year analysis:', err);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.listen(port, () => {
    console.log(`API server running on port ${port}`);
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('Shutting down gracefully...');
    await pool.end();
    process.exit(0);
});
