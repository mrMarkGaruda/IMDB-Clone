-- Import IMDB dataset files
-- This script imports all .tsv.gz files from the dataset directory

-- Import name.basics (people information)
\COPY name_basics FROM PROGRAM 'gunzip -c /dataset/name.basics.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');

-- Import title.basics (movie/TV show information)
\COPY title_basics FROM PROGRAM 'gunzip -c /dataset/title.basics.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');

-- Import title.akas (alternative titles)
\COPY title_akas FROM PROGRAM 'gunzip -c /dataset/title.akas.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');

-- Import title.crew (directors and writers)
\COPY title_crew FROM PROGRAM 'gunzip -c /dataset/title.crew.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');

-- Import title.episode (TV episode information)
\COPY title_episode FROM PROGRAM 'gunzip -c /dataset/title.episode.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');

-- Import title.principals (cast and crew)
\COPY title_principals FROM PROGRAM 'gunzip -c /dataset/title.principals.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');

-- Import title.ratings (ratings information)
\COPY title_ratings FROM PROGRAM 'gunzip -c /dataset/title.ratings.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', NULL '\N', HEADER, QUOTE E'\b');