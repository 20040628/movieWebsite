// delete a movie
function deleteMovie(movieId) {
    fetch("/delete", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            movie_id: movieId
        }),
    })
    .then(
        window.location.href = "/manageMovie"
    )
}

// delete a genre
function deleteGenre(genreId) {
    fetch("/delete_genre", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            genre_id: genreId
        }),
    })
    .then(
        location.reload()
    )
}

// delete a comment
function deleteComment(commentId) {
    fetch("/delete_comment", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            comment_id: commentId
        }),
    })
    .then(
        location.reload()
    )
}
