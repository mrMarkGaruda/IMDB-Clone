// Database manager for IMDB Clone frontend
class DatabaseManager {
    constructor() {
        this.apiBaseUrl = '/api';
    }

    async executeQuery(queryType, params = []) {
        try {
            const url = new URL(`${this.apiBaseUrl}/${queryType}`);
            
            // Add parameters as query string for GET requests
            if (params.length > 0) {
                if (Array.isArray(params[0])) {
                    // Handle object parameters
                    Object.keys(params[0]).forEach(key => {
                        if (params[0][key]) {
                            url.searchParams.append(key, params[0][key]);
                        }
                    });
                } else {
                    // Handle array parameters
                    params.forEach((param, index) => {
                        if (param) {
                            url.searchParams.append(`param${index}`, param);
                        }
                    });
                }
            }

            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Database query error:', error);
            // Return mock data as fallback
            return this.getMockData(queryType, params);
        }
    }

    // Fallback mock data for development/testing
    getMockData(queryType, params = []) {
        const mockData = {
            featured_movies: [
                {
                    id: 'tt0111161',
                    title: 'The Shawshank Redemption',
                    year: 1994,
                    rating: 9.3,
                    genres: 'Drama'
                },
                {
                    id: 'tt0068646',
                    title: 'The Godfather',
                    year: 1972,
                    rating: 9.2,
                    genres: 'Crime, Drama'
                },
                {
                    id: 'tt0468569',
                    title: 'The Dark Knight',
                    year: 2008,
                    rating: 9.0,
                    genres: 'Action, Crime, Drama'
                }
            ],
            featured_series: [
                {
                    id: 'tt0903747',
                    title: 'Breaking Bad',
                    startYear: 2008,
                    endYear: 2013,
                    rating: 9.5,
                    genres: 'Crime, Drama, Thriller'
                },
                {
                    id: 'tt0944947',
                    title: 'Game of Thrones',
                    startYear: 2011,
                    endYear: 2019,
                    rating: 9.3,
                    genres: 'Action, Adventure, Drama'
                },
                {
                    id: 'tt1475582',
                    title: 'Sherlock',
                    startYear: 2010,
                    endYear: 2017,
                    rating: 9.1,
                    genres: 'Crime, Drama, Mystery'
                }
            ],
            top_rated: [
                {
                    id: 'tt0111161',
                    title: 'The Shawshank Redemption',
                    type: 'movie',
                    year: 1994,
                    rating: 9.3
                },
                {
                    id: 'tt0068646',
                    title: 'The Godfather',
                    type: 'movie',
                    year: 1972,
                    rating: 9.2
                },
                {
                    id: 'tt0903747',
                    title: 'Breaking Bad',
                    type: 'tv',
                    year: 2008,
                    rating: 9.5
                }
            ],
            movies_list: [
                {
                    id: 'tt0111161',
                    title: 'The Shawshank Redemption',
                    year: 1994,
                    runtime: 142,
                    rating: 9.3,
                    votes: 2500000,
                    genres: 'Drama',
                    isAdult: false
                },
                {
                    id: 'tt0068646',
                    title: 'The Godfather',
                    year: 1972,
                    runtime: 175,
                    rating: 9.2,
                    votes: 1800000,
                    genres: 'Crime, Drama',
                    isAdult: false
                },
                {
                    id: 'tt0468569',
                    title: 'The Dark Knight',
                    year: 2008,
                    runtime: 152,
                    rating: 9.0,
                    votes: 2700000,
                    genres: 'Action, Crime, Drama',
                    isAdult: false
                }
            ],
            series_list: [
                {
                    id: 'tt0903747',
                    title: 'Breaking Bad',
                    startYear: 2008,
                    endYear: 2013,
                    rating: 9.5,
                    votes: 1900000,
                    genres: 'Crime, Drama, Thriller'
                },
                {
                    id: 'tt0944947',
                    title: 'Game of Thrones',
                    startYear: 2011,
                    endYear: 2019,
                    rating: 9.3,
                    votes: 2000000,
                    genres: 'Action, Adventure, Drama'
                }
            ],
            people_list: [
                {
                    id: 'nm0000142',
                    name: 'Robert De Niro',
                    birthYear: 1943,
                    profession: 'Actor'
                },
                {
                    id: 'nm0000093',
                    name: 'Brad Pitt',
                    birthYear: 1963,
                    profession: 'Actor, Producer'
                },
                {
                    id: 'nm0000158',
                    name: 'Tom Hanks',
                    birthYear: 1956,
                    profession: 'Actor, Producer'
                }
            ],
            search: [
                {
                    id: 'tt0111161',
                    title: 'The Shawshank Redemption',
                    type: 'title',
                    titleType: 'movie',
                    year: 1994,
                    rating: 9.3
                }
            ],
            movie_details: [
                {
                    id: 'tt0111161',
                    title: 'The Shawshank Redemption',
                    year: 1994,
                    runtime: 142,
                    genres: 'Drama',
                    rating: 9.3,
                    votes: 2500000
                }
            ],
            series_details: [
                {
                    id: 'tt0903747',
                    title: 'Breaking Bad',
                    startYear: 2008,
                    endYear: 2013,
                    genres: 'Crime, Drama, Thriller',
                    rating: 9.5,
                    votes: 1900000
                }
            ],
            movie_cast_crew: [
                {
                    id: 'nm0000209',
                    name: 'Tim Robbins',
                    category: 'actor',
                    characters: 'Andy Dufresne'
                },
                {
                    id: 'nm0000151',
                    name: 'Morgan Freeman',
                    category: 'actor',
                    characters: 'Ellis Boyd Redding'
                }
            ],
            series_cast_crew: [
                {
                    id: 'nm0186505',
                    name: 'Bryan Cranston',
                    category: 'actor',
                    characters: 'Walter White'
                },
                {
                    id: 'nm0666739',
                    name: 'Aaron Paul',
                    category: 'actor',
                    characters: 'Jesse Pinkman'
                }
            ],
            series_episodes: [
                {
                    season: 1,
                    episode: 1,
                    title: 'Pilot',
                    rating: 8.2
                },
                {
                    season: 1,
                    episode: 2,
                    title: 'Cat\'s in the Bag...',
                    rating: 8.3
                }
            ],
            rating_trends: [
                { year: 2020, avgRating: 7.2 },
                { year: 2021, avgRating: 7.5 },
                { year: 2022, avgRating: 7.3 },
                { year: 2023, avgRating: 7.6 }
            ],
            genre_analysis: [
                { name: 'Drama', count: 15000 },
                { name: 'Comedy', count: 12000 },
                { name: 'Action', count: 10000 },
                { name: 'Thriller', count: 8000 }
            ],
            year_analysis: [
                { year: 2020, count: 5000 },
                { year: 2021, count: 5200 },
                { year: 2022, count: 4800 },
                { year: 2023, count: 5100 }
            ]
        };

        return mockData[queryType] || [];
    }
}
