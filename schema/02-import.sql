-- Import IMDB dataset files with progress indicators
-- This script imports all .tsv.gz files with enhanced logging

\echo '🚀 Starting IMDB Data Import...'
\echo '================================================'

\echo '📂 Importing name.basics (people information)...'
\timing on
\COPY name_basics FROM PROGRAM 'gunzip -c /dataset/name.basics.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');
\echo '✅ name_basics import completed!'

\echo '📂 Importing title.basics (movie/TV show information)...'
\COPY title_basics FROM PROGRAM 'gunzip -c /dataset/title.basics.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');
\echo '✅ title_basics import completed!'

\echo '📂 Importing title.akas (alternative titles)...'
\COPY title_akas FROM PROGRAM 'gunzip -c /dataset/title.akas.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');
\echo '✅ title_akas import completed!'

\echo '📂 Importing title.crew (directors and writers)...'
\COPY title_crew FROM PROGRAM 'gunzip -c /dataset/title.crew.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');
\echo '✅ title_crew import completed!'

\echo '📂 Importing title.episode (TV episode information)...'
\COPY title_episode FROM PROGRAM 'gunzip -c /dataset/title.episode.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');
\echo '✅ title_episode import completed!'

\echo '📂 Importing title.principals (cast and crew)...'
\COPY title_principals FROM PROGRAM 'gunzip -c /dataset/title.principals.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');
\echo '✅ title_principals import completed!'

\echo '📂 Importing title.ratings (ratings information)...'
\COPY title_ratings FROM PROGRAM 'gunzip -c /dataset/title.ratings.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');
\echo '✅ title_ratings import completed!'

\timing off

\echo '================================================'
\echo '🎉 IMDB Database Import Complete!'
\echo '📊 Generating Statistics...'

\echo 'Table Statistics:'
SELECT 'name_basics' as table_name, COUNT(*) as records FROM name_basics
UNION ALL
SELECT 'title_basics', COUNT(*) FROM title_basics
UNION ALL
SELECT 'title_akas', COUNT(*) FROM title_akas
UNION ALL
SELECT 'title_crew', COUNT(*) FROM title_crew
UNION ALL
SELECT 'title_episode', COUNT(*) FROM title_episode
UNION ALL
SELECT 'title_principals', COUNT(*) FROM title_principals
UNION ALL
SELECT 'title_ratings', COUNT(*) FROM title_ratings
ORDER BY records DESC;

\echo '🔥 IMDB Database Ready for Use!'