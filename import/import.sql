-- Import IMDB dataset files
-- This script imports all .tsv.gz files from the dataset directory

-- Import name.basics (people information)
\COPY name_basics FROM PROGRAM 'gunzip -c /dataset/name.basics.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', HEADER true, NULL '\N');

-- Import title.basics (movie/TV show information)
\COPY title_basics FROM PROGRAM 'gunzip -c /dataset/title.basics.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', HEADER true, NULL '\N');

-- Import title.akas (alternative titles)
\COPY title_akas FROM PROGRAM 'gunzip -c /dataset/title.akas.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', HEADER true, NULL '\N');

-- Import title.crew (directors and writers)
\COPY title_crew FROM PROGRAM 'gunzip -c /dataset/title.crew.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', HEADER true, NULL '\N');

-- Import title.episode (TV episode information)
\COPY title_episode FROM PROGRAM 'gunzip -c /dataset/title.episode.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', HEADER true, NULL '\N');

-- Import title.principals (cast and crew)
\COPY title_principals FROM PROGRAM 'gunzip -c /dataset/title.principals.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', HEADER true, NULL '\N');

-- Import title.ratings (ratings information)
\COPY title_ratings FROM PROGRAM 'gunzip -c /dataset/title.ratings.tsv.gz' WITH (FORMAT csv, DELIMITER E'\t', HEADER true, NULL '\N');