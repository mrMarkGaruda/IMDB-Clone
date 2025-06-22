#!/bin/bash
# Import all .tsv.gz files in /dataset into tables with matching names with ASCII progress bar
set -e
set -o pipefail # Exit on pipe failures

# Debug environment variables
echo ">> Environment Check:"
echo "   POSTGRES_HOST: $POSTGRES_HOST"
echo "   POSTGRES_DB: $POSTGRES_DB"
echo "   POSTGRES_USER: $POSTGRES_USER"
echo "   POSTGRES_PASSWORD: [${#POSTGRES_PASSWORD} chars]"

# Wait for database to be ready
echo ">> Waiting for database connection..."
attempt=1
max_attempts=30
while [ $attempt -le $max_attempts ]; do
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; then
        echo ">> Database connection established!"
        break
    fi
    echo ">> Attempt $attempt/$max_attempts: Database not ready, waiting 5 seconds..."
    sleep 5
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo ">> ERROR: Could not connect to database after $max_attempts attempts"
    exit 1
fi

# Colors for fancy output (ASCII compatible)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display a progress bar
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    local remaining=$((width - completed))
    
    printf "\r${CYAN}Progress: ${NC}["
    printf "%*s" $completed | tr ' ' '#'
    printf "%*s" $remaining | tr ' ' '-'
    printf "] ${YELLOW}%d%%${NC} (${GREEN}%d${NC}/${BLUE}%d${NC})" $percentage $current $total
}

# Function to show real-time import progress
show_import_progress() {
    local table=$1
    local start_time=$2
    
    while true; do
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        
        # Get current row count
        row_count=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ' | tr -d '\n' || echo "0")
        
        # Show spinning indicator and stats
        spin="|/-\\"
        i=$(( elapsed % 4 ))
        spinner=${spin:$i:1}
        
        printf "\r${CYAN}>> ${spinner} Importing... ${GREEN}%s rows${NC} (${YELLOW}%ds${NC})" "$row_count" "$elapsed"
        
        sleep 1
    done
}

# Function to get file size in bytes
get_file_size() {
    if command -v stat >/dev/null 2>&1; then
        # Linux/Unix stat
        stat -c%s "$1" 2>/dev/null || stat -f%z "$1" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Function to get uncompressed size of gzip file
get_uncompressed_size() {
    if command -v gzip >/dev/null 2>&1; then
        gzip -l "$1" 2>/dev/null | awk 'NR==2 {print $2}' || echo "0"
    else
        echo "0"
    fi
}

# Function to format bytes
format_bytes() {
    local bytes=$1
    if [ $bytes -ge 1073741824 ]; then
        echo "$(( bytes / 1073741824 ))GB"
    elif [ $bytes -ge 1048576 ]; then
        echo "$(( bytes / 1048576 ))MB"
    elif [ $bytes -ge 1024 ]; then
        echo "$(( bytes / 1024 ))KB"
    else
        echo "${bytes}B"
    fi
}

# Count total files
echo -e "${PURPLE}>> IMDB Database Import Starting...${NC}"
echo -e "${CYAN}>> Scanning dataset files...${NC}"

total_files=0
total_size=0
for file in /dataset/*.tsv.gz; do
    [ -e "$file" ] || continue
    total_files=$((total_files + 1))
    file_size=$(get_file_size "$file")
    total_size=$((total_size + file_size))
done

echo -e "${GREEN}Found ${total_files} files totaling $(format_bytes $total_size)${NC}"
echo ""

# Define a function to contain the import logic for a single file
import_file() {
    local file=$1
    current_file=$((current_file + 1))
    table=$(basename "$file" .tsv.gz | tr '.' '_')
    file_size=$(get_file_size "$file")
    uncompressed_size=$(get_uncompressed_size "$file")
    filename=$(basename "$file")
    
    echo -e "\n${YELLOW}>> File ${current_file}/${total_files}: ${filename}${NC}"
    echo -e "${BLUE}>> Table: ${table} | Size: $(format_bytes $file_size) -> $(format_bytes $uncompressed_size)${NC}"
    
    # Show overall progress
    show_progress $((current_file - 1)) $total_files
    echo ""
    
    # Record start time
    start_time=$(date +%s)
      # Import with error handling and real-time progress
    echo -e "${CYAN}>> Starting import...${NC}"
    
    # Test if table exists first
    if ! PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1 FROM $table LIMIT 1;" >/dev/null 2>&1; then
        echo -e "${RED}>> ERROR: Table $table does not exist${NC}"
        # Since this is a fatal error for this file, we might want to continue to the next,
        # but the previous logic continued, so we will stick to that.
        return
    fi    # Get the header from the file to use in the COPY command
    header=$(gunzip -c "$file" | head -n 1)
    if [ -z "$header" ]; then
        echo -e "${RED}>> ERROR: Could not read header from $filename${NC}"
        return
    fi
    echo -e "${CYAN}>> Columns to import: ${header}${NC}"

    # Start background progress monitor
    show_import_progress "$table" "$start_time" &
    progress_pid=$!
      # Run the actual import with error capture
    error_file="/tmp/import_error_$table.log"
    # Use FORMAT text, specify columns, and manually skip the header with tail
    echo -e "${YELLOW}>> Debug: Running COPY command:${NC}"
    echo -e "gunzip -c '$file' | tail -n +2 | psql ... -c \"\\copy $table($header) FROM STDIN WITH (FORMAT text, NULL '\\\\N')\""
    if gunzip -c "$file" | tail -n +2 | PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c "\copy $table($header) FROM STDIN WITH (FORMAT text, NULL '\\N')" 2>"$error_file"; then
        # Kill the progress monitor
        kill $progress_pid 2>/dev/null || true
        wait $progress_pid 2>/dev/null || true
        
        # Calculate duration
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        
        # Get final row count
        row_count=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ' | tr -d '\n' || echo "Unknown")
        
        printf "\r${GREEN}>> SUCCESS! ${row_count} rows imported in ${duration}s${NC}\n"
        processed_size=$((processed_size + file_size))
        rm -f "$error_file"
    else
        # The command failed, capture the exit code for information
        exit_code=$?
        
        # Kill the progress monitor
        kill $progress_pid 2>/dev/null || true
        wait $progress_pid 2>/dev/null || true
        printf "\r${RED}>> FAILED to import $filename (exit code: $exit_code)${NC}\n"
        
        # Show the actual error from psql
        if [ -s "$error_file" ]; then
            echo -e "${RED}>> Error details from psql:${NC}"
            cat "$error_file"
        else
            echo -e "${YELLOW}>> No error details were captured in stderr. The error might be with file access or the pipeline setup.${NC}"
        fi
        
        # Add diagnostic comparison
        echo -e "\n${YELLOW}>> Running diagnostics: Comparing file header with table columns...${NC}"
        
        # Get file header (handle potential errors)
        file_header=$(gunzip -c "$file" 2>/dev/null | head -n 1 || echo "ERROR: Could not read file header")
        echo -e "${CYAN}File Header:  ${NC} ${file_header}"
        
        # Get table columns
        table_columns=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT string_agg(column_name, E'\\t') FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '$table';" 2>/dev/null | sed 's/^[ \t]*//;s/[ \t]*$//' || echo "ERROR: Could not retrieve table columns")
        echo -e "${CYAN}Table Columns:${NC} ${table_columns}"
        
        echo -e "\n${RED}>> Import aborted due to error.${NC}"
        rm -f "$error_file" 2>/dev/null
        exit 1
    fi
}

# Import each file with progress
current_file=0
processed_size=0

# Define the import order to respect foreign key constraints
import_order=(
    "name.basics.tsv.gz"
    "title.basics.tsv.gz"
    "title.akas.tsv.gz"
    "title.crew.tsv.gz"
    "title.episode.tsv.gz"
    "title.principals.tsv.gz"
    "title.ratings.tsv.gz"
)

# Create a list of files to import that actually exist
files_to_import=()
for f in "${import_order[@]}"; do
    if [ -e "/dataset/$f" ]; then
        files_to_import+=("/dataset/$f")
    fi
done

# Add any other files not in the specific order to the end
for file in /dataset/*.tsv.gz; do
    [ -e "$file" ] || continue
    is_ordered=false
    for ordered_file in "${files_to_import[@]}"; do
        if [ "$(basename "$ordered_file")" == "$(basename "$file")" ]; then
            is_ordered=true
            break
        fi
    done
    if [ "$is_ordered" = false ]; then
        files_to_import+=("$file")
    fi
done

total_files=${#files_to_import[@]}

for file in "${files_to_import[@]}"; do
    import_file "$file"
done

# Final progress
echo ""
show_progress $total_files $total_files
echo -e "\n\n${GREEN}>> Import Complete!${NC}"

# Show final statistics
echo -e "\n${PURPLE}>> Final Statistics:${NC}"
for file in /dataset/*.tsv.gz; do
    [ -e "$file" ] || continue
    table=$(basename "$file" .tsv.gz | tr '.' '_')
    count=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ' | tr -d '\n' || echo "0")
    echo -e "${CYAN}${table}:${NC} ${GREEN}${count} rows${NC}"
done

echo -e "\n${GREEN}>> IMDB Database Ready!${NC}"
