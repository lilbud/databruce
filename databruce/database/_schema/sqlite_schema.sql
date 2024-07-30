BEGIN TRANSACTION;
DROP TABLE IF EXISTS "TAGS";
CREATE TABLE IF NOT EXISTS "TAGS" (
	"event_id"	TEXT,
	"tags"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("event_id"),
	UNIQUE("event_id","tags")
);
DROP TABLE IF EXISTS "COUNTRIES";
CREATE TABLE IF NOT EXISTS "COUNTRIES" (
	"country_id"	INTEGER,
	"country_name"	TEXT NOT NULL DEFAULT '',
	"num_events"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("country_id" AUTOINCREMENT),
	UNIQUE("country_name")
);
DROP TABLE IF EXISTS "VENUES";
CREATE TABLE IF NOT EXISTS "VENUES" (
	"venue_id"	TEXT,
	"name"	TEXT NOT NULL DEFAULT '',
	"city"	TEXT NOT NULL DEFAULT '',
	"state"	TEXT NOT NULL DEFAULT '',
	"country"	TEXT NOT NULL DEFAULT '',
	"num_events"	INTEGER DEFAULT 0,
	PRIMARY KEY("venue_id")
);
DROP TABLE IF EXISTS "THUMBNAILS";
CREATE TABLE IF NOT EXISTS "THUMBNAILS" (
	"event_id"	TEXT NOT NULL,
	"img_url"	TEXT NOT NULL,
	PRIMARY KEY("event_id","img_url")
);
DROP TABLE IF EXISTS "RELEASES";
CREATE TABLE IF NOT EXISTS "RELEASES" (
	"release_id"	INTEGER DEFAULT 0,
	"brucebase_id"	TEXT NOT NULL DEFAULT '',
	"release_name"	TEXT NOT NULL DEFAULT '',
	"release_type"	TEXT NOT NULL DEFAULT '',
	"release_date"	TEXT NOT NULL DEFAULT '',
	"event_id"	TEXT NOT NULL DEFAULT '',
	"nugs_url"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("release_id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "SONGS";
CREATE TABLE IF NOT EXISTS "SONGS" (
	"song_id"	TEXT,
	"song_name"	TEXT NOT NULL DEFAULT '',
	"short_name"	TEXT NOT NULL DEFAULT '',
	"first_played"	TEXT NOT NULL DEFAULT '',
	"last_played"	TEXT NOT NULL DEFAULT '',
	"num_plays_public"	INTEGER DEFAULT 0,
	"num_plays_private"	INTEGER DEFAULT 0,
	"opener"	INTEGER DEFAULT 0,
	"closer"	INTEGER DEFAULT 0,
	"cover"	INTEGER DEFAULT 0,
	"sniponly"	INTEGER DEFAULT 0,
	"original_artist"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("song_id")
);
DROP TABLE IF EXISTS "SETLISTS";
CREATE TABLE IF NOT EXISTS "SETLISTS" (
	"setlist_song_id"	INTEGER,
	"event_id"	TEXT NOT NULL DEFAULT '',
	"set_name"	TEXT NOT NULL DEFAULT '',
	"song_num"	TEXT NOT NULL DEFAULT '',
	"song_id"	TEXT DEFAULT '',
	"song_note"	TEXT NOT NULL DEFAULT '',
	"segue"	INTEGER DEFAULT 0,
	"premiere"	INTEGER DEFAULT 0,
	"debut"	INTEGER DEFAULT 0,
	"position"	TEXT NOT NULL DEFAULT '',
	"last"	TEXT NOT NULL DEFAULT '',
	"next"	TEXT NOT NULL DEFAULT '',
	"last_time_played"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("setlist_song_id" AUTOINCREMENT),
	UNIQUE("event_id","set_name","song_num","song_id"),
	FOREIGN KEY("song_id") REFERENCES "SONGS"("song_id")
);
DROP TABLE IF EXISTS "NUGS_RELEASES";
CREATE TABLE IF NOT EXISTS "NUGS_RELEASES" (
	"release_id"	INTEGER,
	"nugs_id"	INTEGER NOT NULL DEFAULT 0,
	"event_id"	TEXT NOT NULL DEFAULT '',
	"release_date"	TEXT NOT NULL DEFAULT '',
	"nugs_url"	TEXT NOT NULL DEFAULT '',
	"thumbnail_url"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("release_id" AUTOINCREMENT),
	FOREIGN KEY("event_id") REFERENCES "EVENTS"("event_id")
);
DROP TABLE IF EXISTS "BOOTLEGS";
CREATE TABLE IF NOT EXISTS "BOOTLEGS" (
	"id"	INTEGER NOT NULL,
	"slid"	INTEGER NOT NULL DEFAULT 0,
	"mbid"	TEXT NOT NULL DEFAULT '',
	"event_id"	TEXT NOT NULL DEFAULT '',
	"category"	TEXT NOT NULL DEFAULT '',
	"title"	TEXT NOT NULL DEFAULT '',
	"label"	TEXT NOT NULL DEFAULT '',
	"source"	TEXT NOT NULL DEFAULT '',
	"source_info"	TEXT NOT NULL DEFAULT '',
	"version_info"	TEXT NOT NULL DEFAULT '',
	"transfer"	TEXT NOT NULL DEFAULT '',
	"editor"	TEXT NOT NULL DEFAULT '',
	"type"	TEXT NOT NULL DEFAULT '',
	"catalog_number"	TEXT NOT NULL DEFAULT '',
	"media_type"	TEXT NOT NULL DEFAULT '',
	"jungleland_artwork"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "SNIPPETS";
CREATE TABLE IF NOT EXISTS "SNIPPETS" (
	"event_id"	TEXT NOT NULL DEFAULT '',
	"setlist_song_id"	INTEGER DEFAULT '',
	"set_name"	TEXT NOT NULL DEFAULT '',
	"song_id"	TEXT NOT NULL DEFAULT '',
	"snippet_id"	TEXT NOT NULL DEFAULT '',
	"snippet_pos"	TEXT NOT NULL DEFAULT 1,
	"snippet_note"	TEXT NOT NULL DEFAULT '',
	UNIQUE("event_id","song_id","snippet_id"),
	FOREIGN KEY("song_id") REFERENCES "SONGS"("song_id"),
	FOREIGN KEY("setlist_song_id") REFERENCES "SETLISTS"("setlist_song_id"),
	FOREIGN KEY("snippet_id") REFERENCES "SONGS"("song_id"),
	FOREIGN KEY("event_id") REFERENCES "EVENTS"("event_id")
);
DROP TABLE IF EXISTS "BANDS";
CREATE TABLE IF NOT EXISTS "BANDS" (
	"band_id"	TEXT DEFAULT 0,
	"name"	TEXT NOT NULL DEFAULT '',
	"appearances"	INTEGER NOT NULL DEFAULT 0,
	"first_appearance"	TEXT NOT NULL DEFAULT '',
	"last_appearance"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("band_id"),
	FOREIGN KEY("last_appearance") REFERENCES "EVENTS"("event_id"),
	FOREIGN KEY("first_appearance") REFERENCES "EVENTS"("event_id")
);
DROP TABLE IF EXISTS "TOURS";
CREATE TABLE IF NOT EXISTS "TOURS" (
	"tour_id"	TEXT,
	"tour_name"	TEXT NOT NULL DEFAULT '' UNIQUE,
	"first_show"	TEXT NOT NULL DEFAULT '',
	"last_show"	TEXT NOT NULL DEFAULT '',
	"num_shows"	INTEGER DEFAULT 0,
	"num_songs"	INTEGER DEFAULT 0,
	PRIMARY KEY("tour_id"),
	FOREIGN KEY("last_show") REFERENCES "EVENTS"("event_id"),
	FOREIGN KEY("first_show") REFERENCES "EVENTS"("event_id")
);
DROP TABLE IF EXISTS "CITIES";
CREATE TABLE IF NOT EXISTS "CITIES" (
	"city_id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL DEFAULT '',
	"state"	TEXT NOT NULL DEFAULT '',
	"country"	TEXT NOT NULL DEFAULT '',
	"num_events"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("city_id" AUTOINCREMENT),
	UNIQUE("name","state")
);
DROP TABLE IF EXISTS "RELATIONS";
CREATE TABLE IF NOT EXISTS "RELATIONS" (
	"relation_id"	INTEGER NOT NULL,
	"brucebase_id"	TEXT NOT NULL DEFAULT '',
	"relation_name"	TEXT NOT NULL DEFAULT '',
	"appearances"	INTEGER NOT NULL DEFAULT 0,
	"first_appearance"	TEXT NOT NULL DEFAULT '',
	"last_appearance"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("relation_id" AUTOINCREMENT),
	UNIQUE("brucebase_id")
);
DROP TABLE IF EXISTS "ON_STAGE";
CREATE TABLE IF NOT EXISTS "ON_STAGE" (
	"onstage_id"	INTEGER NOT NULL,
	"event_id"	TEXT NOT NULL DEFAULT '',
	"relation_id"	TEXT NOT NULL DEFAULT '',
	"band_id"	TEXT NOT NULL DEFAULT '',
	"note"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("onstage_id" AUTOINCREMENT),
	UNIQUE("event_id","relation_id","band_id"),
	FOREIGN KEY("relation_id") REFERENCES "RELATIONS"("brucebase_id"),
	FOREIGN KEY("event_id") REFERENCES "EVENTS"("event_id")
);
DROP TABLE IF EXISTS "EVENT_DETAILS";
CREATE TABLE IF NOT EXISTS "EVENT_DETAILS" (
	"event_id"	TEXT,
	"band"	TEXT NOT NULL DEFAULT '',
	"publicity"	TEXT NOT NULL DEFAULT '',
	"tour"	TEXT NOT NULL DEFAULT '',
	"bootleg"	INTEGER DEFAULT 0,
	"official"	INTEGER DEFAULT 0,
	"nugs_id"	TEXT NOT NULL DEFAULT 0,
	"event_type"	TEXT NOT NULL DEFAULT '',
	"event_title"	TEXT NOT NULL DEFAULT '',
	"event_certainty"	TEXT NOT NULL DEFAULT '',
	"setlist_certainty"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("event_id"),
	FOREIGN KEY("event_id") REFERENCES "EVENTS"("event_id")
);
DROP TABLE IF EXISTS "EVENTS";
CREATE TABLE IF NOT EXISTS "EVENTS" (
	"event_num"	INTEGER NOT NULL,
	"event_id"	TEXT,
	"event_date"	TEXT NOT NULL DEFAULT '',
	"day_of_week"	TEXT NOT NULL DEFAULT '',
	"early_late"	TEXT NOT NULL DEFAULT '',
	"brucebase_url"	TEXT NOT NULL DEFAULT '',
	"venue_id"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("event_id"),
	UNIQUE("event_date","event_id","brucebase_url"),
	FOREIGN KEY("venue_id") REFERENCES "VENUES"("venue_id")
);
DROP TABLE IF EXISTS "STATES";
CREATE TABLE IF NOT EXISTS "STATES" (
	"state_id"	INTEGER NOT NULL,
	"state_abbrev"	TEXT NOT NULL DEFAULT '',
	"state_name"	TEXT NOT NULL DEFAULT '',
	"state_country"	INTEGER NOT NULL DEFAULT '',
	"num_events"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("state_id" AUTOINCREMENT),
	UNIQUE("state_abbrev"),
	UNIQUE("state_abbrev","state_country"),
	FOREIGN KEY("state_country") REFERENCES "COUNTRIES"("country_id")
);
DROP TABLE IF EXISTS "RELEASE_TRACKS";
CREATE TABLE IF NOT EXISTS "RELEASE_TRACKS" (
	"track_id"	INTEGER,
	"release_id"	INTEGER DEFAULT '',
	"track_num"	INTEGER DEFAULT 0,
	"song_id"	TEXT DEFAULT '',
	"event_id"	TEXT DEFAULT '',
	"note"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("track_id"),
	FOREIGN KEY("release_id") REFERENCES "RELEASES"("release_id")
);
DROP VIEW IF EXISTS "EVENTS_WITH_INFO";
CREATE VIEW "EVENTS_WITH_INFO" AS 
SELECT
	e.event_id,
	e.event_date ||
	(CASE WHEN e.early_late != '' THEN ' (' || e.early_late || ')' ELSE '' END) AS event_date,
	e.brucebase_url,
	v.name || ', ' || v.city || ', ' ||
	(CASE WHEN v.state != '' THEN v.state ELSE v.country END) AS venue_location,
	'/venue:' || e.venue_id AS venue_url,
	'Bruce Springsteen' ||
    (CASE
        WHEN e1.band != '' AND e1.tour NOT IN ('tour_no', '') THEN ' & ' || b.name
        ELSE ''
    END) AS artist
FROM EVENTS e
LEFT JOIN VENUES v USING (venue_id)
LEFT JOIN EVENT_DETAILS e1 USING (event_id)
LEFT JOIN BANDS b ON b.band_id = e1.band;
DROP VIEW IF EXISTS "OPENERS_CLOSERS";
CREATE VIEW "OPENERS_CLOSERS" AS
SELECT song_id, position, num FROM (
	SELECT
		DISTINCT(s.song_id),
		s.position,
		count(*) AS num
	FROM SETLISTS s
	WHERE s.position != ''
	group by s.song_id, s.position
) 
GROUP BY song_id, position, num
ORDER BY song_id;
DROP VIEW IF EXISTS "SETLIST_NOTES";
CREATE VIEW "SETLIST_NOTES" AS
WITH "existing_setlist_notes" AS (
	SELECT
		setlist_song_id,
		event_id,
		song_note AS note
	FROM "SETLISTS"
	WHERE song_note != ''
),
"snippet_notes" AS (
	SELECT
		setlist_song_id,
		event_id,
		(CASE
			WHEN snippet_note != '' THEN snippet_note
			ELSE 'includes ' || group_concat(song_name, ', ') OVER (PARTITION BY setlist_song_id ORDER BY CAST(snippet_pos AS INT) ASC)
		END) AS note
	FROM "SNIPPETS"
	LEFT JOIN "SONGS" s1 USING (song_id)
	ORDER BY setlist_song_id, CAST(snippet_pos AS INT)
),
"generated_setlist_notes" AS (
	SELECT
		s.setlist_song_id,
		s.event_id,
		(CASE
			WHEN s1.original_artist != '' THEN s1.original_artist || '. ' ELSE ''
		END) ||
		(CASE
			WHEN s.premiere = 1 AND s.next != 'last' THEN 'First Time Played'
			WHEN s.debut = 1 AND s.premiere = 0 THEN 'Tour Debut, last since [' || e.event_id || '] (' || s.last || ' shows)'
			WHEN s.last != 'first' AND CAST(s.last AS INT) >= 50 AND s.debut = 0 THEN 'Bustout, last since [' || e.event_id || '] (' || s.last || ' shows)'
			WHEN s.last = 'first' AND s.next = 'last' THEN 'Only Time Played'
		END) AS note
	FROM "SETLISTS" s
	LEFT JOIN "SONGS" s1 USING (song_id)
	LEFT JOIN "EVENTS" e ON e.event_id = s.last_time_played
),
"all_notes" AS (
	SELECT setlist_song_id, event_id, note FROM (
		SELECT setlist_song_id, event_id, note FROM "generated_setlist_notes"
		UNION ALL
		SELECT setlist_song_id, event_id, note FROM "snippet_notes"
		UNION ALL
		SELECT setlist_song_id, event_id, note FROM "existing_setlist_notes"
	) WHERE note IS NOT NULL GROUP BY setlist_song_id, event_id, note ORDER BY setlist_song_id
),
"unique_notes" AS (
	SELECT
		MIN(a.setlist_song_id),
		a.event_id,
		a.note,
		'[' || ROW_NUMBER() OVER (PARTITION BY a.event_id ORDER BY MIN(setlist_song_id)) || ']' AS num
	FROM "all_notes" a
	WHERE note IS NOT NULL
	GROUP BY a.event_id, a.note
)
SELECT
	a.setlist_song_id,
	a.event_id,
	a.note,
	u.num
FROM "all_notes" a
LEFT JOIN "unique_notes" u ON u.event_id = a.event_id AND u.note = a.note
WHERE a.note IS NOT NULL
ORDER BY a.setlist_song_id;
DROP VIEW IF EXISTS "BOOTLEGS_BY_DATE";
CREATE VIEW "BOOTLEGS_BY_DATE" AS
SELECT
	distinct(b.event_id),
	(CASE WHEN e.early_late != '' THEN e.event_date || ' (' || e.early_late || ') ' ELSE e.event_date END) AS date,
	e1.venue_location,
	count(*)
FROM "BOOTLEGS" b
LEFT JOIN "EVENTS" e USING(event_id)
LEFT JOIN "EVENTS_WITH_INFO" e1 USING(event_id)
WHERE b.category NOT IN ('aud_comp', 'aud_inter', 'vid_comp', 'vid_inter')
AND b.event_id NOT LIKE '%,%'
GROUP BY b.event_id, e.early_late, e.event_date, e1.venue_location
ORDER BY b.event_id ASC;
DROP VIEW IF EXISTS "SETLISTS_BY_DATE";
CREATE VIEW "SETLISTS_BY_DATE" AS
SELECT event_id, replace(group_concat(song_name, ', '), '>,', '>') AS setlist FROM
(SELECT
	s.setlist_song_id,
	s.event_id,
	(CASE 
		WHEN s1.short_name != '' THEN s1.short_name ELSE s1.song_name
	END) ||
	(CASE
		WHEN s.segue = 1 THEN ' >' ELSE ''
	END) AS song_name
FROM "SETLISTS" s
LEFT JOIN "SONGS" s1 USING(song_id)
WHERE s.set_name IN ('Show', 'Set 1', 'Set 2', 'Encore')
ORDER BY s.setlist_song_id ASC)
GROUP BY event_id;
COMMIT;
