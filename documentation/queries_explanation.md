# 📚 IMDb Clone: Queries Documentation & Explanation

This document explains the purpose, logic, and performance considerations for each SQL query used in the web application and analysis.

---

## Web Application Queries

### 1. Movie Summary Page
**Purpose:** Show movie overview (title, year, length, directors, writers, main cast, rating, votes).
**How:** Uses indexed joins and GROUP_CONCAT for top 5 cast. Filters by tconst and type for performance.

### 2. Movie Details Page
**Purpose:** Show alternative titles, production details, technical details.
**How:** Joins with `title_akas` for alternative titles, groups by tconst.

### 3. Complete Cast/Crew Page
**Purpose:** List all actors/crew, sorted by category.
**How:** Joins `title_principals` and `name_basics`, sorts by category and ordering.

### 4. TV Series Summary Page
**Purpose:** Series overview, seasons, years, main cast, rating.
**How:** Joins with `title_episode` for season count, `title_ratings` for rating.

### 5. TV Series Details Page
**Purpose:** Season-by-season breakdown, cast changes, production details.
**How:** Aggregates by season, averages ratings.

### 6. Person Page
**Purpose:** Show person info and filmography by role.
**How:** Joins `name_basics`, `title_principals`, `title_basics`, orders by year.

### 7. Movie Listing Page (with filters)
**Purpose:** List/filter movies by genre, year, rating, adult content.
**How:** Uses dynamic WHERE clauses and indexes for fast filtering.

---

## Data Analysis Queries

### 1. Rating Trends by Year
**Purpose:** Show how average movie ratings change over time.
**How:** GROUP BY year, HAVING for minimum data, ORDER BY year.

### 2. Genre Popularity Over Time
**Purpose:** Track genre trends and average ratings by year.
**How:** GROUP BY genre and year, uses indexes for speed.

### 3. Director Performance Analysis
**Purpose:** Find top directors by average rating and output.
**How:** Joins principals, filters by category, aggregates and sorts.

### 4. Actor Collaboration Network
**Purpose:** Find actor pairs who frequently work together.
**How:** Self-join on principals, GROUP BY actor pairs, HAVING for minimum collaborations.

---

## Performance Notes
- All queries use indexed columns in WHERE/JOINs.
- GROUP BY, HAVING, and window functions are used for analysis.
- LIMIT/OFFSET for pagination and fast web response.
