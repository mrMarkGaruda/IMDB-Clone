# IMDB Clone - Data Import Instructions

## How to Import the IMDB Dataset

The import process is now handled by a separate container that can be run manually. This gives you full control over when to import the data and allows you to monitor the progress.

### Step 1: Start the Main Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (with schema)
- API server
- Frontend
- pgAdmin

The database will be initialized with the schema but no data.

### Step 2: Run the Import

```bash
docker-compose run --rm importer
```

This will:
- Start the import container
- Connect to the database
- Show a fancy ASCII progress bar
- Import all TSV files with real-time progress
- Display final statistics
- Remove the container when done

### Features of the Import Process

- **Real-time Progress**: Shows current file being processed and overall progress
- **ASCII Compatible**: Works in all terminals without Unicode issues
- **File Statistics**: Shows compressed and uncompressed file sizes
- **Row Counting**: Displays rows imported per table during and after import
- **Error Handling**: Gracefully handles import failures
- **Timing**: Shows how long each file takes to import

### Expected Output

```
>> IMDB Database Import Starting...
>> Scanning dataset files...
Found 7 files totaling 1.2GB

>> File 1/7: name.basics.tsv.gz
>> Table: name_basics | Size: 273MB -> 849MB
Progress: [##########----------] 50% (3/7)
>> | Importing... 12345678 rows (120s)
>> SUCCESS! 12345678 rows imported in 120s
```

### Monitoring Progress

You can also monitor the database in real-time from another terminal:

```bash
# Connect to database
docker exec -it imdb_postgres psql -U imdbuser -d imdb

# Check table sizes
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size 
FROM pg_tables WHERE schemaname = 'public';
```

### Troubleshooting

If the import fails:
1. Check if all TSV files are present in the `dataset/` directory
2. Ensure the database container is running: `docker ps`
3. Check the import logs: `docker-compose logs importer`
4. Restart the database if needed: `docker-compose restart db`

The import can be run multiple times safely - it will append data or fail gracefully if data already exists.
