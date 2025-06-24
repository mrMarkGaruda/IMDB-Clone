# 📚 IMDb Clone: Queries Documentation & Explanation

This document explains the purpose, logic, and performance considerations for each SQL query used in the web application and analysis.

---

## Web Application Queries

### 1. Home Page Statistics
**Purpose:** Display database statistics and top-rated movies on the home page.
**How:** Simple COUNT queries for each table, plus a top-rated movies query with JOIN and ORDER BY.

### 2. Movies Listing Page
**Purpose:** Paginated movie browsing with optional filters (genre, year, rating, adult content).
**How:** Dynamic WHERE clauses with optional parameters, uses LIMIT/OFFSET for pagination.

### 3. Movie Details Page
**Purpose:** Show complete movie information including ratings.
**How:** LEFT JOIN with title_ratings to get all movie data plus ratings if available.

### 4. Movie Cast and Crew
**Purpose:** Display cast and crew for a specific movie, ordered by importance.
**How:** JOIN between title_principals and name_basics, ordered by tp.ordering.

### 5. Alternative Titles
**Purpose:** Show alternative titles/names for movies in different regions.
**How:** Simple query on title_akas table filtered by titleId.

### 6. Person Details Page
**Purpose:** Show basic information about a person (actor, director, etc.).
**How:** Direct query on name_basics table by nconst.

### 7. Person Filmography
**Purpose:** Show complete filmography for a person, categorized by role.
**How:** JOIN title_principals with title_basics, ordered by year descending.

### 8. Search Movies and TV Series
**Purpose:** Search functionality across movie and TV titles.
**How:** LIKE pattern matching with result ordering by popularity (numVotes).

### 9. Search People
**Purpose:** Search functionality for actors, directors, and other people.
**How:** LIKE pattern matching on primaryName with alphabetical ordering.

---

## Data Analysis Queries

### 1. Rating Trends by Year
**Purpose:** Show how average movie ratings change over time for analysis dashboard.
**How:** GROUP BY year with HAVING clause for minimum data points, filtered by modern years (1980-2023).

### 2. Genre Popularity Analysis
**Purpose:** Analyze which genres are most popular and their average ratings.
**How:** CASE statement to categorize genres, GROUP BY genre with aggregation functions.

### 3. Top Directors Analysis
**Purpose:** Find directors with the best average ratings and sufficient output.
**How:** JOIN principals table filtering by director category, GROUP BY with HAVING for minimum movie count.

### 4. Actor Collaboration Analysis
**Purpose:** Find actor pairs who frequently work together.
**How:** Self-join on title_principals table, GROUP BY actor pairs with HAVING for minimum collaborations.

---

## Performance Notes
- All queries use indexed columns in WHERE/JOINs.
- GROUP BY, HAVING, and window functions are used for analysis.
- LIMIT/OFFSET for pagination and fast web response.
