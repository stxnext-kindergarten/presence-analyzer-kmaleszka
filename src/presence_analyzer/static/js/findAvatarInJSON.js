function findAvatarInJSON(json_array, user_id) {
    for (var i = 0; i < json_array.length; i++)
    {
        if (json_array[i].user_id == user_id) {
            return json_array[i].avatar_url;
        }
    }
}