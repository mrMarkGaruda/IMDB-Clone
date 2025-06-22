# IMDb Clone & Data Analysis Project Checklist

This checklist breaks down the project tasks, assigns responsibilities to S and M, and provides suggested Git commit messages for each step.

---

## Part 1: Database Structure & Data Import

**Objective:** Design and implement the database schema and import the IMDb non-commercial dataset.

### Task 1.1: Database Schema Design (S Primary, M Review)

- [ ] **1.1.1 Identify Entities:** List all core entities (Movies, TV Series, Episodes, People, Genres, Ratings, Votes, etc.).
    - Assigned to: S
    - Git Commit: `feat: Identify core entities for IMDb schema`
- [ ] **1.1.2 Define Tables & Columns:** For each entity, create a table and define relevant columns.
    - Assigned to: S
    - Git Commit: `feat: Draft initial table and column definitions`
- [ ] **1.1.3 Establish Relationships:** Determine how tables relate to each other (e.g., many-to-many, foreign keys).
    - Assigned to: S
    - Git Commit: `feat: Define table relationships and foreign keys`
- [ ] **1.1.4 Specify Data Types:** Choose appropriate SQL data types for each column.
    - Assigned to: S
    - Git Commit: `refactor: Optimize data types for schema columns`
- [ ] **1.1.5 Set Constraints:** Apply `NOT NULL` constraints where data is mandatory.
    - Assigned to: S
    - Git Commit: `feat: Add NULL constraints to schema tables`
- [ ] **1.1.6 Design Primary & Foreign Keys:** Define primary keys for uniqueness and foreign keys for referential integrity.
    - Assigned to: S
    - Git Commit: `feat: Implement primary and foreign key constraints`
- [ ] **1.1.7 Plan Indexes:** Identify columns for indexing to optimize performance.
    - Assigned to: S
    - Git Commit: `perf: Plan initial indexes for schema tables`
- [ ] **Completion:** Finalize `schema.sql` and `schema.png`.
    - Assigned to: S
    - Git Commit: `feat: Complete initial database schema design (schema.sql & schema.png)`

### Task 1.2: Data Import Script Creation (M Primary, S Review/Testing)

- [ ] **1.2.1 Data Source Analysis:** Understand the format and structure of the IMDb dataset files.
    - Assigned to: M
    - Git Commit: `docs: Analyze IMDb dataset file formats`
- [ ] **1.2.2 Scripting Import:** Write `INSERT` statements or use bulk import commands.
    - Assigned to: M
    - Git Commit: `feat: Develop core data import scripts`
- [ ] **1.2.3 Handle Duplicates:** Implement logic to prevent or manage duplicate entries.
    - Assigned to: M
    - Git Commit: `fix: Add duplicate handling to import scripts`
- [ ] **1.2.4 Validate Data Integrity:** Run checks for data consistency and accuracy after import.
    - Assigned to: M & S (Collaborative testing)
    - Git Commit: `test: Implement and run data integrity validation checks`
- [ ] **1.2.5 Create Test Data (if needed):** Generate small datasets for testing.
    - Assigned to: M
    - Git Commit: `feat: Generate small test dataset for import`
- [ ] **Completion:** Finalize `import.sql` (or equivalent import scripts).
    - Assigned to: M
    - Git Commit: `feat: Finalize data import scripts for IMDb dataset`

---

## Part 2: Web Application Queries & Features

**Objective:** Develop SQL queries to support a web application with specified pages and features.

### Task 2.1: Core Page Queries (S Primary, M Review/Testing)

- [ ] **2.1.1 Movie Summary Page:** Query for title, year, length, directors, writers, top 5 cast, rating, votes.
    - Assigned to: S
    - Git Commit: `feat(web): Add query for Movie Summary Page`
- [ ] **2.1.2 Movie Details Page:** Query for alternative titles, production details, full technical details.
    - Assigned to: S
    - Git Commit: `feat(web): Add query for Movie Details Page`
- [ ] **2.1.3 Complete Cast/Crew Page:** Query for all actors with roles, full crew listing, sorted by categories.
    - Assigned to: S
    - Git Commit: `feat(web): Add query for Complete Cast/Crew Page`
- [ ] **2.1.4 TV Series Summary Page:** Query for series overview, seasons count, years active, main cast, general rating.
    - Assigned to: S
    - Git Commit: `feat(web): Add query for TV Series Summary Page`
- [ ] **2.1.5 TV Series Details Page:** Query for season-by-season breakdown, cast changes, production details.
    - Assigned to: S
    - Git Commit: `feat(web): Add query for TV Series Details Page`
- [ ] **2.1.6 Episode Page:** Query for episode-specific details, guest stars, individual rating.
    - Assigned to: S
    - Git Commit: `feat(web): Add query for Episode Page`
- [ ] **2.1.7 Person Page:** Query for basic information, complete filmography (categorized by role type).
    - Assigned to: S
    - Git Commit: `feat(web): Add query for Person Page`
- [ ] **2.1.8 Movie Listing Page:** Query for filterable movies by genre, year, rating, and other criteria.
    - Assigned to: S
    - Git Commit: `feat(web): Add query for Movie Listing Page with filters`
- [ ] **2.1.9 Series Listing Page:** Query for filterable series similar to movies, plus TV-specific filters.
    - Assigned to: S
    - Git Commit: `feat(web): Add query for Series Listing Page with filters`
- [ ] **2.1.10 Home Page:** Query for featured content and navigation links.
    - Assigned to: S
    - Git Commit: `feat(web): Add query for Home Page featured content`
- [ ] **Completion:** Finalize all queries in `web_queries.sql` with detailed comments.
    - Assigned to: S
    - Git Commit: `feat(web): Complete all core web application page queries`

### Task 2.2: General Application Features Queries (M Primary, S Review/Integration)

- [ ] **2.2.1 Adult Content Filtering:** Query to filter content based on an "adult" flag.
    - Assigned to: M
    - Git Commit: `feat(web): Implement adult content filtering query`
- [ ] **2.2.2 Search Engine:** Queries to support searching by title, person name, genre, etc.
    - Assigned to: M
    - Git Commit: `feat(web): Develop search engine queries`
- [ ] **2.2.3 Advanced Person-to-Person Search:** Queries to find collaboration networks or relationships.
    - Assigned to: M
    - Git Commit: `feat(web): Add advanced person-to-person search queries`
- [ ] **2.2.4 Custom Creative Feature (if chosen):** Propose and implement a unique new feature.
    - Assigned to: M & S (Collaborative proposal & M primary implementation)
    - Git Commit: `feat(web): Implement custom creative feature: [Feature Name]`
- [ ] **Completion:** Finalize general feature queries in `web_queries.sql` with comments.
    - Assigned to: M
    - Git Commit: `feat(web): Finalize general web application feature queries`

---

## Part 3: Data Analysis & Visualization

**Objective:** Create SQL queries for data analysis reports and visualize the findings.

### Task 3.1: Data Analysis Queries (M Primary, S Review/Understanding insights)

- [ ] **3.1.1 Rating Trends - By year/decade:** SQL to aggregate average ratings over time.
    - Assigned to: M
    - Git Commit: `feat(analysis): Query for rating trends by year/decade`
- [ ] **3.1.2 Rating Trends - By genre:** SQL to calculate average ratings per genre.
    - Assigned to: M
    - Git Commit: `feat(analysis): Query for rating trends by genre`
- [ ] **3.1.3 Rating Trends - By country:** SQL to determine average ratings by country of origin.
    - Assigned to: M
    - Git Commit: `feat(analysis): Query for rating trends by country`
- [ ] **3.1.4 Performance Analysis - Directors' average ratings:** SQL to compute average film ratings for directors.
    - Assigned to: M
    - Git Commit: `feat(analysis): Query for directors' average ratings`
- [ ] **3.1.5 Performance Analysis - Actors' film success:** SQL to analyze actor performance based on film ratings.
    - Assigned to: M
    - Git Commit: `feat(analysis): Query for actors' film success analysis`
- [ ] **3.1.6 Performance Analysis - Genre popularity over time:** SQL to track genre trends.
    - Assigned to: M
    - Git Commit: `feat(analysis): Query for genre popularity over time`
- [ ] **3.1.7 Relationship Analysis - Collaboration networks:** SQL to identify frequent collaborations.
    - Assigned to: M
    - Git Commit: `feat(analysis): Query for collaboration networks`
- [ ] **3.1.8 Relationship Analysis - Genre combinations:** SQL to find common genre pairings.
    - Assigned to: M
    - Git Commit: `feat(analysis): Query for common genre combinations`
- [ ] **3.1.9 Relationship Analysis - Success patterns:** SQL to identify common elements in highly-rated content.
    - Assigned to: M
    - Git Commit: `feat(analysis): Query for success patterns in content`
- [ ] **3.1.10 Custom Analysis (if chosen):** Propose and implement a unique analysis.
    - Assigned to: M & S (Collaborative proposal & M primary implementation)
    - Git Commit: `feat(analysis): Implement custom analysis: [Analysis Name]`
- [ ] **Completion:** Finalize all queries in `analysis_queries.sql` with extensive comments.
    - Assigned to: M
    - Git Commit: `feat(analysis): Complete all required data analysis queries`

### Task 3.2: Visualization and Report Generation (S Primary, M Data preparation/Support)

- [ ] **3.2.1 Select Tools:** Choose a tool for visualization (e.g., spreadsheet software, Python libraries, etc.).
    - Assigned to: S
    - Git Commit: `docs: Select data visualization tools for analysis`
- [ ] **3.2.2 Generate Visualizations:** Create clear and informative graphs for each analysis.
    - Assigned to: S
    - Git Commit: `feat(analysis): Generate visualizations for data reports`
- [ ] **3.2.3 Document Methodology:** Explain how the analysis was performed.
    - Assigned to: S
    - Git Commit: `docs(analysis): Document analysis methodologies`
- [ ] **3.2.4 Explain Insights:** Describe what the visualizations show and the conclusions drawn.
    - Assigned to: S
    - Git Commit: `docs(analysis): Explain insights from data visualizations`
- [ ] **Completion:** Finalize `visualizations.pdf` and `queries_explanation.md`.
    - Assigned to: S
    - Git Commit: `docs(analysis): Finalize analysis report and visualizations`

---

## Part 4: Documentation & Submission

**Objective:** Ensure all project components are well-documented and prepared for submission.

### Task 4.1: Comprehensive Documentation (S & M Collaborative)

- [ ] **4.1.1 Project Overview (README.md):** Write a concise overview of the project.
    - Assigned to: S
    - Git Commit: `docs: Draft README.md project overview`
- [ ] **4.1.2 Database Setup Instructions (README.md/separate doc):** Provide clear setup instructions.
    - Assigned to: S
    - Git Commit: `docs: Add database setup instructions to README.md`
- [ ] **4.1.3 Query Explanation:** Ensure `queries_explanation.md` (or comments) thoroughly explain all queries.
    - Assigned to: M
    - Git Commit: `docs: Add detailed explanations for all SQL queries`
- [ ] **4.1.4 Data Analysis Methodology:** Detail methodology for custom analysis (if applicable).
    - Assigned to: M
    - Git Commit: `docs: Document custom analysis methodology`
- [ ] **Completion:** Ensure all documentation is complete and in place.
    - Assigned to: S & M
    - Git Commit: `docs: Complete all project documentation`

### Task 4.2: Final Review & Submission Preparation (S & M Joint Responsibility)

- [ ] **4.2.1 Cross-check Requirements:** Verify all evaluation criteria are met.
    - Assigned to: S & M
    - Git Commit: `chore: Cross-check project against submission requirements`
- [ ] **4.2.2 Folder Structure:** Organize files into a clear and logical directory.
    - Assigned to: S & M
    - Git Commit: `refactor: Organize project files into logical structure`
- [ ] **4.2.3 Final Test:** Run through setup, web queries, and analysis queries to confirm functionality.
    - Assigned to: S & M
    - Git Commit: `test: Perform final end-to-end project testing`
- [ ] **4.2.4 Prepare Submission:** Package the project as required (PDF, GitHub repo, etc.).
    - Assigned to: S & M
    - Git Commit: `chore: Prepare final project submission package`
- [ ] **Completion:** Project is ready for final submission.
    - Assigned to: S & M
    - Git Commit: `chore: Project ready for final submission`