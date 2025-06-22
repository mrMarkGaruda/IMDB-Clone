#!/bin/bash
# Import all .tsv.gz files in /dataset into tables with matching names with ASCII progress bar
set -e

# Wait for database to be ready
echo ">> Waiting for database connection..."
until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
    echo ">> Database not ready, waiting 5 seconds..."
    sleep 5
done
echo ">> Database connection established!"

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

# Import each file with progress
current_file=0
processed_size=0

for file in /dataset/*.tsv.gz; do
    [ -e "$file" ] || continue
    
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
    
    # Start background progress monitor
    show_import_progress "$table" "$start_time" &
    progress_pid=$!
    
    # Run the actual import
    if gunzip -c "$file" | PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\\copy $table FROM STDIN WITH (FORMAT csv, DELIMITER E'\t', HEADER true, NULL '\\N')" >/dev/null 2>&1; then
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
    else
        # Kill the progress monitor
        kill $progress_pid 2>/dev/null || true
        wait $progress_pid 2>/dev/null || true
        printf "\r${RED}>> FAILED to import $filename${NC}\n"
    fi
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
