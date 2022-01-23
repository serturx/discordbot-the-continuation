from enum import Enum


class _Errors(Enum):
    not_connected_to_voice = "I'm not connected to a voice channel!"
    user_not_connected_to_voice = "You're not connected to a voice channel!"
    already_connected = "I'm already connected to a voice channel!"
    not_playing = "I'm not playing anything right now!"
    not_paused = "I'm not paused!"
    queue_empty = "The queue is empty!"
    invalid_remove_index = "The index you want to remove is invalid!",
    invalid_skip_index = "The index you want to skip to is invalid!"
    skip_error = "There is no song to skip to!"

    query_not_found = "Couldn't find the song"




class _Status(Enum):
    connecting_to_voice = "Connecting..."
    queue_finished_playing = "Finished playing the queue!"
    join_success = "Joined!"
    added_to_queue = "Added to queue!"
    shuffle_enabled = "Shuffle is now enabled"
    shuffle_disabled = "Shuffle is now disabled"


class StatusMessages(Enum):
    Errors = _Errors
    Status = _Status
