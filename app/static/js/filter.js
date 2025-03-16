function filterMovies() {
    var genreSelect = document.getElementById('genre-select');
    var scoreSelect = document.getElementById('score-select');
    var searchInput = document.getElementById('search-input');

    var selectedGenreId = genreSelect.value;
    var selectedScoreOrder = scoreSelect.value;
    var searchValue = searchInput.value.trim();

    // Build URL parameter
    var url = "/allMovie?genre_id=" + selectedGenreId;

    // If ranking is selected, add the corresponding parameters
    if (selectedScoreOrder !== "Null") {
        url += "&sort_order=" + selectedScoreOrder;
    }

    // If search value is not empty, add the search parameter
    if (searchValue !== "") {
        url += "&search=" + encodeURIComponent(searchValue);
    }

    window.location.href = url;
}
