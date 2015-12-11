attach '/home/nnm/play_stat.db' as play_stat;
-- Artist
insert into musicdb_artist (
    artist_id,
    name
)
select 
    artist_id,
    name
from play_stat.artist;
-- Albums
insert into musicdb_album (
    album_id,
    artist_id,
    -- genre,
    is_available,
    -- isactive,
    title,
    date,
    release_date,
    mbid,
    rg_peak,
    rg_gain,
    add_time,
    source,
    release_type
)
select 
    album_id,
    artist_id,
    -- genre,
    -- isavailable,
    isactive,
    title,
    date,
    release_date,
    mbid,
    rg_peak,
    rg_gain,
    datetime('now'),
    1,
    0
from play_stat.album;
-- Track
insert into musicdb_track (
    track_id,
    track_num,
    title,
    track_artist,
    length,
    disc,
    uri,
    rg_peak,
    rg_gain,
    album_id
)
select 
    track_id,
    track_num,
    title,
    track_artist,
    length,
    disc,
    uri,
    rg_peak,
    rg_gain,
    album_id
from play_stat.track;
-- Play Log
insert into musicdb_playlog (
    time,
    source,
    track_id
)
select 
    time,
    source,
    track_id
from play_stat.play_log;
