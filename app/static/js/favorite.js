function favorite(movieId, userId) {
    // send Ajax request
    $.ajax({
        type: 'POST',
        url: '/add_favorite',
        data: {
            movie_id: movieId,
            user_id: userId
        },
        success: function (response) {
            if (response.success) {
                $('#favorite-btn').html('<i class="fa fa-heart"></i> Unfavorite');
                $('#favorite-btn').attr('onclick', `removeFavorite('${movieId}', '${userId}')`);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert('Error：' + textStatus +'-'+ errorThrown);
        }
    });
}

function removeFavorite(movieId,userId) {
    // send Ajax request
    $.ajax({
        type: 'POST',
        url: '/remove_favorite',
        data: {
            movie_id: movieId,
            user_id: userId
        },
        success: function (response) {
            if (response.success) {
                $('#favorite-btn').html('<i class="fa fa-heart-o"></i> Favorite');
                $('#favorite-btn').attr('onclick', `favorite('${movieId}', '${userId}')`);
            }
        }
    });
}