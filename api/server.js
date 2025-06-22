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
            SELECT tb.tconst as id, tb.primarytitle as title, 
                   tb.startyear as year, tb.genres,
                   tr.averagerating as rating, tr.numvotes as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titletype = 'movie' 
                AND tr.averagerating >= 8.0 
                AND tr.numvotes >= 100000
            ORDER BY tr.averagerating DESC, tr.numvotes DESC
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
            SELECT tb.tconst as id, tb.primarytitle as title, 
                   tb.startyear, tb.endyear, tb.genres,
                   tr.averagerating as rating, tr.numvotes as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titletype IN ('tvSeries', 'tvMiniSeries') 
                AND tr.averagerating >= 8.0 
                AND tr.numvotes >= 10000
            ORDER BY tr.averagerating DESC, tr.numvotes DESC
            LIMIT 12
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            ...row,
            startYear: row.startyear,
            endYear: row.endyear
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
            SELECT tb.tconst as id, tb.primarytitle as title, 
                   tb.startyear as year, tb.titletype as type,
                   tr.averagerating as rating, tr.numvotes as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titletype IN ('movie', 'tvSeries', 'tvMiniSeries') 
                AND tr.averagerating >= 8.5 
                AND tr.numvotes >= 50000
            ORDER BY tr.averagerating DESC, tr.numvotes DESC
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
            SELECT tb.tconst as id, tb.primarytitle as title, 
                   tb.startyear as year, tb.runtimeminutes as runtime,
                   tb.genres, tb.isadult,
                   tr.averagerating as rating, tr.numvotes as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titletype = 'movie' 
                AND tb.startyear IS NOT NULL
                AND tr.numvotes >= 1000
            ORDER BY tr.numvotes DESC, tr.averagerating DESC
            LIMIT 100
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            ...row,
            isAdult: row.isadult === '1'
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
            SELECT tb.tconst as id, tb.primarytitle as title, 
                   tb.startyear, tb.endyear, tb.genres,
                   tr.averagerating as rating, tr.numvotes as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.titletype IN ('tvSeries', 'tvMiniSeries') 
                AND tb.startyear IS NOT NULL
                AND tr.numvotes >= 1000
            ORDER BY tr.numvotes DESC, tr.averagerating DESC
            LIMIT 100
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            ...row,
            startYear: row.startyear,
            endYear: row.endyear
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
            SELECT nb.nconst as id, nb.primaryname as name, 
                   nb.birthyear, nb.deathyear, nb.primaryprofession as profession
            FROM name_basics nb
            WHERE nb.primaryprofession IS NOT NULL
            ORDER BY nb.primaryname
            LIMIT 100
        `;
        const result = await pool.query(query);
        res.json(result.rows.map(row => ({
            ...row,
            birthYear: row.birthyear,
            deathYear: row.deathyear
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
            SELECT tb.tconst as id, tb.primarytitle as title, 
                   tb.startyear as year, tb.titletype,
                   tr.averagerating as rating, 'title' as type
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE LOWER(tb.primarytitle) LIKE $1
                AND tb.titletype IN ('movie', 'tvSeries', 'tvMiniSeries')
            ORDER BY tr.numvotes DESC NULLS LAST
            LIMIT 20
        `;
        
        // Search people
        const peopleQuery = `
            SELECT nb.nconst as id, nb.primaryname as name, 
                   nb.birthyear, nb.deathyear, nb.primaryprofession as profession,
                   'person' as type
            FROM name_basics nb
            WHERE LOWER(nb.primaryname) LIKE $1
            ORDER BY nb.primaryname
            LIMIT 20
        `;
        
        const [titleResults, peopleResults] = await Promise.all([
            pool.query(titleQuery, [searchTerm]),
            pool.query(peopleQuery, [searchTerm])
        ]);
        
        const results = [
            ...titleResults.rows.map(row => ({
                ...row,
                titleType: row.titletype,
                birthYear: row.birthyear,
                deathYear: row.deathyear
            })),
            ...peopleResults.rows.map(row => ({
                ...row,
                birthYear: row.birthyear,
                deathYear: row.deathyear
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
            SELECT tb.tconst as id, tb.primarytitle as title, 
                   tb.startyear as year, tb.runtimeminutes as runtime,
                   tb.genres,
                   tr.averagerating as rating, tr.numvotes as votes
            FROM title_basics tb
            LEFT JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.tconst = $1
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
            SELECT nb.nconst as id, nb.primaryname as name, 
                   tp.category, tp.characters, tp.job
            FROM title_principals tp
            JOIN name_basics nb ON tp.nconst = nb.nconst
            WHERE tp.tconst = $1
            ORDER BY tp.ordering
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
            SELECT tb.startyear as year, 
                   AVG(tr.averagerating) as avgrating,
                   COUNT(*) as count
            FROM title_basics tb
            JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.startyear BETWEEN 2000 AND 2023
                AND tb.titletype IN ('movie', 'tvSeries')
                AND tr.numvotes >= 1000
            GROUP BY tb.startyear
            ORDER BY tb.startyear
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
                SELECT unnest(string_to_array(tb.genres, ',')) as genre
                FROM title_basics tb
                JOIN title_ratings tr ON tb.tconst = tr.tconst
                WHERE tb.titletype IN ('movie', 'tvSeries')
                    AND tb.genres IS NOT NULL
                    AND tr.numvotes >= 1000
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
            SELECT tb.startyear as year, COUNT(*) as count
            FROM title_basics tb
            JOIN title_ratings tr ON tb.tconst = tr.tconst
            WHERE tb.startyear BETWEEN 2010 AND 2023
                AND tb.titletype IN ('movie', 'tvSeries')
                AND tr.numvotes >= 1000
            GROUP BY tb.startyear
            ORDER BY tb.startyear DESC
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
