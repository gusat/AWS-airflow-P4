class SqlQueries:
    # Table Drop Queries
    staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
    staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
    songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
    user_table_drop = "DROP TABLE IF EXISTS users;"
    song_table_drop = "DROP TABLE IF EXISTS songs;"
    artist_table_drop = "DROP TABLE IF EXISTS artists;"
    time_table_drop = "DROP TABLE IF EXISTS time;"

    # Table Creation Queries
    staging_events_table_create = """
        CREATE TABLE IF NOT EXISTS staging_events (
            artist VARCHAR,
            auth VARCHAR,
            firstName VARCHAR,
            gender CHAR(1),
            itemInSession INT, 
            lastName VARCHAR,
            length FLOAT,
            level VARCHAR,
            location VARCHAR,
            method VARCHAR,
            page VARCHAR,
            registration BIGINT,
            sessionId INT,
            song VARCHAR,
            status INT,
            ts BIGINT,
            userAgent VARCHAR,
            userId INT
        );
    """

    staging_songs_table_create = """
        CREATE TABLE IF NOT EXISTS staging_songs (
            num_songs INT,
            artist_id VARCHAR,
            artist_latitude FLOAT,
            artist_longitude FLOAT,
            artist_location VARCHAR,
            artist_name VARCHAR,
            song_id VARCHAR,
            title VARCHAR,
            duration FLOAT,
            year INT
        );
    """

    songplay_table_create = """
        CREATE TABLE IF NOT EXISTS songplays (
            songplay_id VARCHAR PRIMARY KEY,
            start_time TIMESTAMP NOT NULL,
            user_id INT NOT NULL,
            level VARCHAR,
            song_id VARCHAR NOT NULL,
            artist_id VARCHAR NOT NULL,
            session_id INT,
            location VARCHAR,
            user_agent VARCHAR
        );
    """

    user_table_create = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT PRIMARY KEY,
            first_name VARCHAR,
            last_name VARCHAR,
            gender CHAR(1),
            level VARCHAR NOT NULL
        );
    """

    song_table_create = """
        CREATE TABLE IF NOT EXISTS songs (
            song_id VARCHAR PRIMARY KEY,
            title VARCHAR,
            artist_id VARCHAR NOT NULL,
            year INT,
            duration FLOAT
        );
    """

    artist_table_create = """
        CREATE TABLE IF NOT EXISTS artists (
            artist_id VARCHAR PRIMARY KEY,
            name VARCHAR,
            location VARCHAR,
            latitude FLOAT,
            longitude FLOAT
        );
    """

    time_table_create = """
        CREATE TABLE IF NOT EXISTS time (
            start_time TIMESTAMP PRIMARY KEY,
            hour INT,
            day INT,
            week INT,
            month INT,
            year INT,
            weekday INT
        );
    """

    #Table Insert Queries
    
    songplay_table_insert = """
        SELECT
            md5(events.sessionid || events.start_time) songplay_id,
            events.start_time, 
            events.userid, 
            events.level, 
            songs.song_id, 
            songs.artist_id, 
            events.sessionid,   
            events.location, 
            events.useragent
        FROM
            (SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
            FROM staging_events
            WHERE page='NextSong') events
        LEFT JOIN staging_songs songs
        ON events.song = songs.title
            AND events.artist = songs.artist_name
            AND events.length = songs.duration
            WHERE songs.song_id IS NOT NULL;
    """

    user_table_insert = """
        SELECT DISTINCT userid, firstname, lastname, gender, level
        FROM staging_events
        WHERE page='NextSong'
    """

    song_table_insert = """
        SELECT DISTINCT song_id, title, artist_id, year, duration
        FROM staging_songs
    """

    artist_table_insert = """
        SELECT DISTINCT artist_id, artist_name, artist_location, artist_latitude, artist_longitude
        FROM staging_songs
    """

    time_table_insert = """
        SELECT start_time, EXTRACT(hour FROM start_time), EXTRACT(day FROM start_time), EXTRACT(week FROM start_time),
               EXTRACT(month FROM start_time), EXTRACT(year FROM start_time), EXTRACT(dayofweek FROM start_time)
        FROM songplays
    """
    