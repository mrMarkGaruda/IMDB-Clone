// Search-specific functionality
async function performAdvancedSearch() {
    const searchTerm = document.getElementById('searchTerm').value;
    const filters = {
        type: document.getElementById('typeFilter').value,
        genre: document.getElementById('genreFilter').value,
        yearFrom: document.getElementById('yearFromFilter').value,
        yearTo: document.getElementById('yearToFilter').value,
        minRating: document.getElementById('minRatingFilter').value,
        sort: document.getElementById('sortFilter').value
    };

    if (!searchTerm.trim()) {
        document.getElementById('searchResults').innerHTML = '<div class="text-center">Please enter a search term</div>';
        return;
    }

    try {
        showLoading('searchResults');
        const results = await db.searchContent(searchTerm, filters);
        
        // Apply additional filters
        let filteredResults = results;
        
        if (filters.yearFrom) {
            filteredResults = filteredResults.filter(item => {
                const year = item.year || item.startYear;
                return year >= parseInt(filters.yearFrom);
            });
        }
        
        if (filters.yearTo) {
            filteredResults = filteredResults.filter(item => {
                const year = item.year || item.startYear;
                return year <= parseInt(filters.yearTo);
            });
        }

        if (filteredResults.length === 0) {
            document.getElementById('searchResults').innerHTML = '<div class="text-center">No results found for your search</div>';
            document.getElementById('searchResultsCount').textContent = '0 results found';
            return;
        }

        // Sort results
        if (filters.sort === 'rating') {
            filteredResults.sort((a, b) => b.rating - a.rating);
        } else if (filters.sort === 'year') {
            filteredResults.sort((a, b) => {
                const yearA = a.year || a.startYear;
                const yearB = b.year || b.startYear;
                return yearB - yearA;
            });
        } else if (filters.sort === 'title') {
            filteredResults.sort((a, b) => a.title.localeCompare(b.title));
        }

        document.getElementById('searchResults').innerHTML = filteredResults.map(createContentCard).join('');
        document.getElementById('searchResultsCount').textContent = `${filteredResults.length} results found for "${searchTerm}"`;
        
    } catch (error) {
        console.error('Error performing search:', error);
        showError('searchResults', 'Error performing search');
    }
}

async function findCollaborations() {
    const person1 = document.getElementById('person1').value.trim();
    const person2 = document.getElementById('person2').value.trim();
    
    if (!person1 || !person2) {
        document.getElementById('collaborationResults').innerHTML = '<div class="error">Please enter both person names</div>';
        return;
    }
    
    if (person1.toLowerCase() === person2.toLowerCase()) {
        document.getElementById('collaborationResults').innerHTML = '<div class="error">Please enter different person names</div>';
        return;
    }
    
    try {
        document.getElementById('collaborationResults').innerHTML = '<div class="loading">Searching for collaborations...</div>';
        
        // Mock collaboration data - in real app, this would query the database
        const collaborations = await findPersonCollaborations(person1, person2);
        
        if (collaborations.length === 0) {
            document.getElementById('collaborationResults').innerHTML = `
                <div class="text-center">No collaborations found between ${person1} and ${person2}</div>
            `;
            return;
        }
        
        const collaborationHtml = `
            <h4>Collaborations between ${person1} and ${person2}</h4>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Year</th>
                            <th>Type</th>
                            <th>${person1}'s Role</th>
                            <th>${person2}'s Role</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${collaborations.map(collab => `
                            <tr>
                                <td><a href="#" onclick="viewDetails('${collab.id}')">${collab.title}</a></td>
                                <td>${collab.year}</td>
                                <td>${collab.type}</td>
                                <td>${collab.person1Role}</td>
                                <td>${collab.person2Role}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        document.getElementById('collaborationResults').innerHTML = collaborationHtml;
        
    } catch (error) {
        console.error('Error finding collaborations:', error);
        document.getElementById('collaborationResults').innerHTML = '<div class="error">Error searching for collaborations</div>';
    }
}

async function findPersonCollaborations(person1, person2) {
    // Mock data - in real implementation, this would query the database
    // for movies/shows where both people worked together
    const mockCollaborations = [
        {
            id: 'tt0111161',
            title: 'The Shawshank Redemption',
            year: 1994,
            type: 'Movie',
            person1Role: 'Andy Dufresne (Actor)',
            person2Role: 'Ellis Boyd Redding (Actor)'
        },
        {
            id: 'tt0114814',
            title: 'The Shawshank Redemption: Behind the Scenes',
            year: 1995,
            type: 'Documentary',
            person1Role: 'Himself (Actor)',
            person2Role: 'Himself (Actor)'
        }
    ];
    
    // Simple matching - in real app, this would be much more sophisticated
    if ((person1.toLowerCase().includes('tim') && person2.toLowerCase().includes('morgan')) ||
        (person1.toLowerCase().includes('morgan') && person2.toLowerCase().includes('tim'))) {
        return mockCollaborations;
    }
    
    return [];
}

function clearSearchFilters() {
    document.getElementById('searchTerm').value = '';
    document.getElementById('typeFilter').selectedIndex = 0;
    document.getElementById('genreFilter').selectedIndex = 0;
    document.getElementById('yearFromFilter').value = '';
    document.getElementById('yearToFilter').value = '';
    document.getElementById('minRatingFilter').value = '';
    document.getElementById('sortFilter').selectedIndex = 0;
    document.getElementById('adultContentToggle').checked = false;
    
    document.getElementById('searchResults').innerHTML = '';
    document.getElementById('searchResultsCount').textContent = '';
}

// Export functions
window.performAdvancedSearch = performAdvancedSearch;
window.findCollaborations = findCollaborations;
window.clearSearchFilters = clearSearchFilters;
