// Main JavaScript functionality for IMDB Clone
const db = new DatabaseManager();

// Global variables
let currentPage = 1;
let currentFilters = {};

// Page initialization
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

function initializePage() {
    const currentPageName = getCurrentPage();
    
    switch (currentPageName) {
        case 'index':
            loadHomePage();
            break;
        case 'movies':
            loadMoviesPage();
            break;
        case 'series':
            loadSeriesPage();
            break;
        case 'people':
            loadPeoplePage();
            break;
        case 'search':
            loadSearchPage();
            break;
        case 'movie-details':
            loadMovieDetails();
            break;
        case 'series-details':
            loadSeriesDetails();
            break;
        case 'analysis':
            loadAnalysisPage();
            break;
        default:
            console.log('Unknown page:', currentPageName);
    }
    
    // Set up search functionality
    setupSearchHandlers();
    updateActiveNavigation();
}

function getCurrentPage() {
    const path = window.location.pathname;
    const filename = path.split('/').pop().split('.')[0];
    return filename || 'index';
}

function setupSearchHandlers() {
    const quickSearch = document.getElementById('quickSearch');
    if (quickSearch) {
        quickSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performQuickSearch();
            }
        });
    }
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
}

function updateActiveNavigation() {
    const currentPageName = getCurrentPage();
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === `${currentPageName}.html` || (currentPageName === 'index' && href === 'index.html')) {
            link.classList.add('active');
        }
    });
}

// Home Page Functions
async function loadHomePage() {
    try {
        await Promise.all([
            loadFeaturedMovies(),
            loadFeaturedSeries(),
            loadTopRated()
        ]);
    } catch (error) {
        console.error('Error loading home page:', error);
    }
}

async function loadFeaturedMovies() {
    const container = document.getElementById('featuredMovies');
    if (!container) return;
    
    try {
        showLoading('featuredMovies');
        const movies = await db.executeQuery('featured_movies');
        container.innerHTML = movies.map(movie => createMovieCard(movie)).join('');
    } catch (error) {
        console.error('Error loading featured movies:', error);
        showError('featuredMovies', 'Error loading featured movies');
    }
}

async function loadFeaturedSeries() {
    const container = document.getElementById('featuredSeries');
    if (!container) return;
    
    try {
        showLoading('featuredSeries');
        const series = await db.executeQuery('featured_series');
        container.innerHTML = series.map(show => createSeriesCard(show)).join('');
    } catch (error) {
        console.error('Error loading featured series:', error);
        showError('featuredSeries', 'Error loading featured series');
    }
}

async function loadTopRated() {
    const container = document.getElementById('topRated');
    if (!container) return;
    
    try {
        showLoading('topRated');
        const content = await db.executeQuery('top_rated');
        container.innerHTML = content.map(item => createContentCard(item)).join('');
    } catch (error) {
        console.error('Error loading top rated content:', error);
        showError('topRated', 'Error loading top rated content');
    }
}

// Movies Page Functions
async function loadMoviesPage() {
    try {
        await loadMovieFilters();
        await loadMoviesList();
    } catch (error) {
        console.error('Error loading movies page:', error);
    }
}

async function loadMovieFilters() {
    const filtersContainer = document.getElementById('movieFilters');
    if (!filtersContainer) return;
    
    const filterHTML = `
        <div class="filters-container">
            <div class="filter-group">
                <label for="genreFilter">Genre:</label>
                <select id="genreFilter" onchange="filterMovies()">
                    <option value="">All Genres</option>
                    <option value="Action">Action</option>
                    <option value="Comedy">Comedy</option>
                    <option value="Drama">Drama</option>
                    <option value="Thriller">Thriller</option>
                    <option value="Horror">Horror</option>
                    <option value="Romance">Romance</option>
                    <option value="Sci-Fi">Sci-Fi</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="yearFilter">Year:</label>
                <input type="number" id="yearFilter" placeholder="Year" onchange="filterMovies()">
            </div>
            <div class="filter-group">
                <label for="ratingFilter">Min Rating:</label>
                <input type="number" id="ratingFilter" min="0" max="10" step="0.1" placeholder="0.0" onchange="filterMovies()">
            </div>
            <div class="filter-group">
                <label for="adultFilter">Adult Content:</label>
                <select id="adultFilter" onchange="filterMovies()">
                    <option value="false">Hide Adult</option>
                    <option value="true">Show Adult</option>
                    <option value="">Show All</option>
                </select>
            </div>
            <div class="filter-group">
                <button onclick="clearFilters()">Clear Filters</button>
            </div>
        </div>
    `;
    
    filtersContainer.innerHTML = filterHTML;
}

async function loadMoviesList(filters = {}) {
    const container = document.getElementById('moviesList');
    if (!container) return;
    
    try {
        showLoading('moviesList');
        const movies = await db.executeQuery('movies_list');
        
        // Apply filters
        let filteredMovies = movies;
        if (filters.genre) {
            filteredMovies = filteredMovies.filter(movie => 
                movie.genres && movie.genres.toLowerCase().includes(filters.genre.toLowerCase())
            );
        }
        if (filters.year) {
            filteredMovies = filteredMovies.filter(movie => movie.year == filters.year);
        }
        if (filters.minRating) {
            filteredMovies = filteredMovies.filter(movie => movie.rating >= parseFloat(filters.minRating));
        }
        if (filters.adultFilter === 'false') {
            filteredMovies = filteredMovies.filter(movie => !movie.isAdult);
        } else if (filters.adultFilter === 'true') {
            filteredMovies = filteredMovies.filter(movie => movie.isAdult);
        }
        
        container.innerHTML = filteredMovies.map(movie => createMovieListItem(movie)).join('');
    } catch (error) {
        console.error('Error loading movies list:', error);
        showError('moviesList', 'Error loading movies');
    }
}

async function filterMovies() {
    const filters = {
        genre: document.getElementById('genreFilter')?.value || '',
        year: document.getElementById('yearFilter')?.value || '',
        minRating: document.getElementById('ratingFilter')?.value || '',
        adultFilter: document.getElementById('adultFilter')?.value || 'false'
    };
    
    currentFilters = filters;
    await loadMoviesList(filters);
}

function clearFilters() {
    document.getElementById('genreFilter').value = '';
    document.getElementById('yearFilter').value = '';
    document.getElementById('ratingFilter').value = '';
    document.getElementById('adultFilter').value = 'false';
    filterMovies();
}

// Series Page Functions
async function loadSeriesPage() {
    try {
        await loadSeriesFilters();
        await loadSeriesList();
    } catch (error) {
        console.error('Error loading series page:', error);
    }
}

async function loadSeriesFilters() {
    const filtersContainer = document.getElementById('seriesFilters');
    if (!filtersContainer) return;
    
    const filterHTML = `
        <div class="filters-container">
            <div class="filter-group">
                <label for="seriesGenreFilter">Genre:</label>
                <select id="seriesGenreFilter" onchange="filterSeries()">
                    <option value="">All Genres</option>
                    <option value="Drama">Drama</option>
                    <option value="Comedy">Comedy</option>
                    <option value="Action">Action</option>
                    <option value="Thriller">Thriller</option>
                    <option value="Crime">Crime</option>
                    <option value="Documentary">Documentary</option>
                    <option value="Horror">Horror</option>
                    <option value="Sci-Fi">Sci-Fi</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="seriesYearFilter">Start Year:</label>
                <input type="number" id="seriesYearFilter" placeholder="Year" onchange="filterSeries()">
            </div>
            <div class="filter-group">
                <label for="seriesStatusFilter">Status:</label>
                <select id="seriesStatusFilter" onchange="filterSeries()">
                    <option value="">All</option>
                    <option value="ongoing">Ongoing</option>
                    <option value="ended">Ended</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="seriesRatingFilter">Min Rating:</label>
                <input type="number" id="seriesRatingFilter" min="0" max="10" step="0.1" placeholder="0.0" onchange="filterSeries()">
            </div>
            <div class="filter-group">
                <button onclick="clearSeriesFilters()">Clear Filters</button>
            </div>
        </div>
    `;
    
    filtersContainer.innerHTML = filterHTML;
}

async function loadSeriesList(filters = {}) {
    const container = document.getElementById('seriesList');
    if (!container) return;
    
    try {
        showLoading('seriesList');
        const series = await db.executeQuery('series_list');
        
        // Apply filters
        let filteredSeries = series;
        if (filters.genre) {
            filteredSeries = filteredSeries.filter(show => 
                show.genres && show.genres.toLowerCase().includes(filters.genre.toLowerCase())
            );
        }
        if (filters.year) {
            filteredSeries = filteredSeries.filter(show => show.startYear == filters.year);
        }
        if (filters.minRating) {
            filteredSeries = filteredSeries.filter(show => show.rating >= parseFloat(filters.minRating));
        }
        if (filters.status === 'ongoing') {
            filteredSeries = filteredSeries.filter(show => !show.endYear);
        } else if (filters.status === 'ended') {
            filteredSeries = filteredSeries.filter(show => show.endYear);
        }
        
        container.innerHTML = filteredSeries.map(show => createSeriesListItem(show)).join('');
    } catch (error) {
        console.error('Error loading series list:', error);
        showError('seriesList', 'Error loading series');
    }
}

async function filterSeries() {
    const filters = {
        genre: document.getElementById('seriesGenreFilter')?.value || '',
        year: document.getElementById('seriesYearFilter')?.value || '',
        status: document.getElementById('seriesStatusFilter')?.value || '',
        minRating: document.getElementById('seriesRatingFilter')?.value || ''
    };
    
    await loadSeriesList(filters);
}

function clearSeriesFilters() {
    document.getElementById('seriesGenreFilter').value = '';
    document.getElementById('seriesYearFilter').value = '';
    document.getElementById('seriesStatusFilter').value = '';
    document.getElementById('seriesRatingFilter').value = '';
    filterSeries();
}

// People Page Functions
async function loadPeoplePage() {
    try {
        await loadPeopleList();
    } catch (error) {
        console.error('Error loading people page:', error);
    }
}

async function loadPeopleList() {
    const container = document.getElementById('peopleList');
    if (!container) return;
    
    try {
        showLoading('peopleList');
        const people = await db.executeQuery('people_list');
        container.innerHTML = people.map(person => createPersonCard(person)).join('');
    } catch (error) {
        console.error('Error loading people list:', error);
        showError('peopleList', 'Error loading people');
    }
}

// Search Functions
async function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput?.value?.trim();
    
    if (!query) return;
    
    window.location.href = `search.html?q=${encodeURIComponent(query)}`;
}

async function performQuickSearch() {
    const searchInput = document.getElementById('quickSearch');
    const query = searchInput?.value?.trim();
    
    if (!query) return;
    
    window.location.href = `search.html?q=${encodeURIComponent(query)}`;
}

async function loadSearchPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    
    if (query) {
        const searchInput = document.getElementById('searchQuery');
        if (searchInput) {
            searchInput.value = query;
        }
        await executeSearch(query);
    }
}

async function executeSearch(query) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer) return;
    
    try {
        showLoading('searchResults');
        const results = await db.executeQuery('search', [query]);
        
        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results">No results found for "' + query + '"</div>';
        } else {
            resultsContainer.innerHTML = `
                <div class="search-summary">${results.length} results found for "${query}"</div>
                ${results.map(result => createSearchResultItem(result)).join('')}
            `;
        }
    } catch (error) {
        console.error('Error executing search:', error);
        showError('searchResults', 'Error performing search');
    }
}

// Detail Pages
async function loadMovieDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const movieId = urlParams.get('id');
    
    if (!movieId) {
        console.error('No movie ID provided');
        return;
    }
    
    try {
        await Promise.all([
            loadMovieBasicInfo(movieId),
            loadMovieCastCrew(movieId)
        ]);
    } catch (error) {
        console.error('Error loading movie details:', error);
    }
}

async function loadMovieBasicInfo(movieId) {
    const container = document.getElementById('movieBasicInfo');
    if (!container) return;
    
    try {
        const movie = await db.executeQuery('movie_details', [movieId]);
        if (movie.length > 0) {
            container.innerHTML = createMovieDetailView(movie[0]);
        }
    } catch (error) {
        console.error('Error loading movie basic info:', error);
    }
}

async function loadMovieCastCrew(movieId) {
    const container = document.getElementById('castCrewInfo');
    if (!container) return;
    
    try {
        const castCrew = await db.executeQuery('movie_cast_crew', [movieId]);
        container.innerHTML = createCastCrewView(castCrew);
    } catch (error) {
        console.error('Error loading cast and crew:', error);
    }
}

async function loadSeriesDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const seriesId = urlParams.get('id');
    
    if (!seriesId) {
        console.error('No series ID provided');
        return;
    }
    
    try {
        await Promise.all([
            loadSeriesBasicInfo(seriesId),
            loadSeriesEpisodes(seriesId),
            loadSeriesCastCrew(seriesId)
        ]);
    } catch (error) {
        console.error('Error loading series details:', error);
    }
}

async function loadSeriesBasicInfo(seriesId) {
    const container = document.getElementById('seriesBasicInfo');
    if (!container) return;
    
    try {
        const series = await db.executeQuery('series_details', [seriesId]);
        if (series.length > 0) {
            container.innerHTML = createSeriesDetailView(series[0]);
        }
    } catch (error) {
        console.error('Error loading series basic info:', error);
    }
}

async function loadSeriesEpisodes(seriesId) {
    const container = document.getElementById('episodesInfo');
    if (!container) return;
    
    try {
        const episodes = await db.executeQuery('series_episodes', [seriesId]);
        container.innerHTML = createEpisodesView(episodes);
    } catch (error) {
        console.error('Error loading episodes:', error);
    }
}

async function loadSeriesCastCrew(seriesId) {
    const container = document.getElementById('seriesCastCrewInfo');
    if (!container) return;
    
    try {
        const castCrew = await db.executeQuery('series_cast_crew', [seriesId]);
        container.innerHTML = createCastCrewView(castCrew);
    } catch (error) {
        console.error('Error loading cast and crew:', error);
    }
}

// Analysis Page Functions
async function loadAnalysisPage() {
    try {
        await Promise.all([
            loadRatingTrends(),
            loadGenreAnalysis(),
            loadYearAnalysis()
        ]);
    } catch (error) {
        console.error('Error loading analysis page:', error);
    }
}

async function loadRatingTrends() {
    const container = document.getElementById('ratingTrends');
    if (!container) return;
    
    try {
        const trends = await db.executeQuery('rating_trends');
        container.innerHTML = createRatingTrendsChart(trends);
    } catch (error) {
        console.error('Error loading rating trends:', error);
    }
}

async function loadGenreAnalysis() {
    const container = document.getElementById('genreAnalysis');
    if (!container) return;
    
    try {
        const genreData = await db.executeQuery('genre_analysis');
        container.innerHTML = createGenreChart(genreData);
    } catch (error) {
        console.error('Error loading genre analysis:', error);
    }
}

async function loadYearAnalysis() {
    const container = document.getElementById('yearAnalysis');
    if (!container) return;
    
    try {
        const yearData = await db.executeQuery('year_analysis');
        container.innerHTML = createYearChart(yearData);
    } catch (error) {
        console.error('Error loading year analysis:', error);
    }
}

// HTML Creation Functions
function createMovieCard(movie) {
    return `
        <div class="content-card" onclick="viewMovieDetails('${movie.id}')">
            <div class="card-content">
                <h4>${movie.title}</h4>
                <p class="year">${movie.year}</p>
                <p class="rating">★ ${movie.rating || 'N/A'}</p>
                <p class="genres">${(movie.genres || '').substring(0, 50)}${movie.genres && movie.genres.length > 50 ? '...' : ''}</p>
            </div>
        </div>
    `;
}

function createSeriesCard(series) {
    const years = series.endYear ? `${series.startYear}-${series.endYear}` : `${series.startYear}-`;
    return `
        <div class="content-card" onclick="viewSeriesDetails('${series.id}')">
            <div class="card-content">
                <h4>${series.title}</h4>
                <p class="year">${years}</p>
                <p class="rating">★ ${series.rating || 'N/A'}</p>
                <p class="genres">${(series.genres || '').substring(0, 50)}${series.genres && series.genres.length > 50 ? '...' : ''}</p>
            </div>
        </div>
    `;
}

function createContentCard(content) {
    return `
        <div class="content-card" onclick="viewDetails('${content.id}', '${content.type}')">
            <div class="card-content">
                <h4>${content.title}</h4>
                <p class="type">${content.type}</p>
                <p class="year">${content.year}</p>
                <p class="rating">★ ${content.rating}</p>
            </div>
        </div>
    `;
}

function createMovieListItem(movie) {
    return `
        <div class="list-item" onclick="viewMovieDetails('${movie.id}')">
            <div class="item-info">
                <h3>${movie.title}</h3>
                <p class="details">${movie.year} • ${formatRuntime(movie.runtime)} • ${movie.genres || ''}</p>
                <p class="rating">★ ${movie.rating || 'N/A'} (${movie.votes || 0} votes)</p>
            </div>
        </div>
    `;
}

function createSeriesListItem(series) {
    const years = series.endYear ? `${series.startYear}-${series.endYear}` : `${series.startYear}-`;
    return `
        <div class="list-item" onclick="viewSeriesDetails('${series.id}')">
            <div class="item-info">
                <h3>${series.title}</h3>
                <p class="details">${years} • ${series.genres || ''}</p>
                <p class="rating">★ ${series.rating || 'N/A'} (${series.votes || 0} votes)</p>
            </div>
        </div>
    `;
}

function createPersonCard(person) {
    const lifespan = person.deathYear ? `${person.birthYear}-${person.deathYear}` : `${person.birthYear}-`;
    return `
        <div class="person-card" onclick="viewPersonDetails('${person.id}')">
            <div class="person-info">
                <h3>${person.name}</h3>
                <p class="profession">${person.profession || 'N/A'}</p>
                <p class="lifespan">${lifespan}</p>
            </div>
        </div>
    `;
}

function createSearchResultItem(result) {
    if (result.type === 'title') {
        return `
            <div class="search-result" onclick="viewDetails('${result.id}', '${result.titleType}')">
                <h3>${result.title}</h3>
                <p class="result-meta">${result.titleType} (${result.year}) ★ ${result.rating || 'N/A'}</p>
            </div>
        `;
    } else {
        return `
            <div class="search-result" onclick="viewPersonDetails('${result.id}')">
                <h3>${result.name}</h3>
                <p class="result-meta">${result.profession} (${result.birthYear}${result.deathYear ? '-' + result.deathYear : ''})</p>
            </div>
        `;
    }
}

function createMovieDetailView(movie) {
    return `
        <div class="movie-detail">
            <h1>${movie.title}</h1>
            <div class="movie-meta">
                <p><strong>Year:</strong> ${movie.year}</p>
                <p><strong>Runtime:</strong> ${formatRuntime(movie.runtime)}</p>
                <p><strong>Genres:</strong> ${movie.genres || 'N/A'}</p>
                <p><strong>Rating:</strong> ★ ${movie.rating || 'N/A'} (${movie.votes || 0} votes)</p>
            </div>
        </div>
    `;
}

function createSeriesDetailView(series) {
    const years = series.endYear ? `${series.startYear}-${series.endYear}` : `${series.startYear}-Present`;
    return `
        <div class="series-detail">
            <h1>${series.title}</h1>
            <div class="series-meta">
                <p><strong>Years:</strong> ${years}</p>
                <p><strong>Genres:</strong> ${series.genres || 'N/A'}</p>
                <p><strong>Rating:</strong> ★ ${series.rating || 'N/A'} (${series.votes || 0} votes)</p>
            </div>
        </div>
    `;
}

function createCastCrewView(castCrew) {
    if (!castCrew || castCrew.length === 0) {
        return '<p>No cast and crew information available.</p>';
    }
    
    return `
        <div class="cast-crew">
            <h3>Cast & Crew</h3>
            <div class="cast-crew-list">
                ${castCrew.map(person => `
                    <div class="cast-crew-item" onclick="viewPersonDetails('${person.id}')">
                        <h4>${person.name}</h4>
                        <p>${person.category || 'N/A'}</p>
                        <p>${person.characters || person.job || ''}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function createEpisodesView(episodes) {
    if (!episodes || episodes.length === 0) {
        return '<p>No episode information available.</p>';
    }
    
    return `
        <div class="episodes">
            <h3>Episodes</h3>
            <div class="episodes-list">
                ${episodes.map(episode => `
                    <div class="episode-item">
                        <h4>S${episode.season}E${episode.episode}: ${episode.title}</h4>
                        <p class="rating">★ ${episode.rating || 'N/A'}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function createRatingTrendsChart(trends) {
    return `
        <div class="chart-container">
            <h3>Rating Trends Over Time</h3>
            <div class="simple-chart">
                ${trends.map(trend => `
                    <div class="chart-bar">
                        <div class="bar" style="height: ${trend.avgRating * 10}%"></div>
                        <span class="label">${trend.year}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function createGenreChart(genreData) {
    return `
        <div class="chart-container">
            <h3>Popular Genres</h3>
            <div class="genre-list">
                ${genreData.map(genre => `
                    <div class="genre-item">
                        <span class="genre-name">${genre.name}</span>
                        <span class="genre-count">${genre.count} titles</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function createYearChart(yearData) {
    return `
        <div class="chart-container">
            <h3>Content by Year</h3>
            <div class="year-list">
                ${yearData.map(year => `
                    <div class="year-item">
                        <span class="year-label">${year.year}</span>
                        <span class="year-count">${year.count} titles</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Navigation Functions
function viewMovieDetails(movieId) {
    window.location.href = `movie-details.html?id=${movieId}`;
}

function viewSeriesDetails(seriesId) {
    window.location.href = `series-details.html?id=${seriesId}`;
}

function viewPersonDetails(personId) {
    window.location.href = `person-details.html?id=${personId}`;
}

function viewDetails(id, type) {
    if (type === 'movie') {
        viewMovieDetails(id);
    } else if (type && type.includes('tv')) {
        viewSeriesDetails(id);
    } else {
        viewMovieDetails(id);
    }
}

// Utility Functions
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading">Loading...</div>';
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="error">${message}</div>`;
    }
}

function formatRuntime(minutes) {
    if (!minutes) return 'N/A';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
}

function formatRating(rating) {
    return rating ? `★ ${rating}/10` : 'Not rated';
}

function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Export functions for global use
window.performSearch = performSearch;
window.performQuickSearch = performQuickSearch;
window.filterMovies = filterMovies;
window.filterSeries = filterSeries;
window.clearFilters = clearFilters;
window.clearSeriesFilters = clearSeriesFilters;
window.viewMovieDetails = viewMovieDetails;
window.viewSeriesDetails = viewSeriesDetails;
window.viewPersonDetails = viewPersonDetails;
window.executeSearch = executeSearch;
