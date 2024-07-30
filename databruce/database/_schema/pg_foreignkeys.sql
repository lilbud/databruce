BEGIN TRANSACTION;
ALTER TABLE "SETLISTS"
    DROP CONSTRAINT IF EXISTS "fk_setlists_songs",
    ADD CONSTRAINT "fk_setlists_songs" FOREIGN KEY("song_id") REFERENCES "SONGS"("song_id");

ALTER TABLE "RELEASE_TRACKS"
    DROP CONSTRAINT IF EXISTS "fk_releasetracks_releases",
    ADD CONSTRAINT "fk_releasetracks_releases" FOREIGN KEY("release_id") REFERENCES "RELEASES"("release_id");

ALTER TABLE "NUGS_RELEASES"
    DROP CONSTRAINT IF EXISTS "fk_nugs_events",
    ADD CONSTRAINT "fk_nugs_events" FOREIGN KEY("event_id") REFERENCES "EVENTS"("event_id");

ALTER TABLE "SNIPPETS"
	DROP CONSTRAINT IF EXISTS "fk_songs",
	DROP CONSTRAINT IF EXISTS "fk_snippet_songs",
	DROP CONSTRAINT IF EXISTS "fk_snippet_setlists",
	DROP CONSTRAINT IF EXISTS "fk_snippet_events",
    ADD CONSTRAINT "fk_songs" FOREIGN KEY("song_id") REFERENCES "SONGS"("song_id"),
    ADD CONSTRAINT "fk_snippet_songs" FOREIGN KEY("snippet_id") REFERENCES "SONGS"("song_id"),
    ADD CONSTRAINT "fk_snippet_setlists" FOREIGN KEY("setlist_song_id") REFERENCES "SETLISTS"("setlist_song_id"),
    ADD CONSTRAINT "fk_snippet_events" FOREIGN KEY("event_id") REFERENCES "EVENTS"("event_id");

ALTER TABLE "BANDS"
    DROP CONSTRAINT IF EXISTS "fk_bands_events_first",
    DROP CONSTRAINT IF EXISTS "fk_bands_events_last",
    ADD CONSTRAINT "fk_bands_events_first" FOREIGN KEY("first_appearance") REFERENCES "EVENTS"("event_id"),
    ADD CONSTRAINT "fk_bands_events_last" FOREIGN KEY("last_appearance") REFERENCES "EVENTS"("event_id");

ALTER TABLE "TOURS"
	DROP CONSTRAINT IF EXISTS "fk_tours_events_last",
	DROP CONSTRAINT IF EXISTS "fk_tours_events_first",
	ADD CONSTRAINT "fk_tours_events_last" FOREIGN KEY("last_show") REFERENCES "EVENTS"("event_id"),
	ADD CONSTRAINT "fk_tours_events_first" FOREIGN KEY("first_show") REFERENCES "EVENTS"("event_id");

ALTER TABLE "ON_STAGE"
    DROP CONSTRAINT IF EXISTS "fk_onstage_relations",
	DROP CONSTRAINT IF EXISTS "fk_onstage_events",
    ADD CONSTRAINT "fk_onstage_relations" FOREIGN KEY("relation_id") REFERENCES "RELATIONS"("brucebase_id"),
	ADD CONSTRAINT "fk_onstage_events" FOREIGN KEY("event_id") REFERENCES "EVENTS"("event_id");

ALTER TABLE "EVENT_DETAILS"
    DROP CONSTRAINT IF EXISTS "fk_details_events",
    ADD CONSTRAINT "fk_details_events" FOREIGN KEY("event_id") REFERENCES "EVENTS"("event_id");

ALTER TABLE "EVENTS"
    DROP CONSTRAINT IF EXISTS "fk_event_venue",
    ADD CONSTRAINT "fk_event_venue" FOREIGN KEY("venue_id") REFERENCES "VENUES"("venue_id");

ALTER TABLE "STATES"
    DROP CONSTRAINT IF EXISTS "fk_state_country",
    ADD CONSTRAINT "fk_state_country" FOREIGN KEY("state_country") REFERENCES "COUNTRIES"("country_id");
COMMIT;