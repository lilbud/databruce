# Changelog

## This file will contain a log of major changes to the database. Usually fixes or whatnot. I've been keeping this list in a local file but never added it here.

- 2024-08-02 - First release of the 2.0 version
- 2024-08-17 - Brucebase updated a ton of urls on their site. Changing urls from showing "early/late/morning/evening/etc" to just having an incrementing letter after the date that increments by date (for multi event dates) or by multiple unknown dates. This is still ongoing and as I catch the new URLs I'm updating them in the database
- 2024-08-18 - fixed songs on High Hopes having the incorrect release_id in 'release_tracks'. Was instead pointing to the BITUSA Live DVD
- 2024-08-22:
  - fixed setlist note numbering. For unknown reasons, sometimes the number attached to a note wouldn't match the number of notes. Like a note saying "2" when there is only a single note for a show. Managed to fix by removing number from `setlist_notes` and adding a similar function to `setlists_by_set_and_date`
    fix `songs_after_release`. It was showing far too high of a number for the number of times a song was played _after_ its first studio release. Like Price You Pay showing only 77 total plays and 120 after release. Simply had to put a "distinct" in the count
- 2024-09-11 - fix `nugs_releases`. Originally this table had a column pointing to `live.brucespringsteen.net`. However, as of today, they switched over fully to `nugs.net`. I had to update the URLs to match correctly
- 2024-09-15:
  - fix incorrect artist associated with Gloria. Mistakenly set to Roy Orbison when it should've been set to Leon Rene.
  - completely by accident managed to fix the setlist note numbering. Had to put a check in to make sure the note wasn't empty OR null, not just one or the either.
- 2024-09-23 - added venue full text search column.
- 2024-09-24:
  - added aliases and musicbrainz ids to 745/2101 venues.
  - added `updated_at` and `created_at` timestamps to every table. Something that probably should've been there from the beginning, but I'm figuring this all out as I go along. Took a while to sort out the triggers but now they'll fire on any column update which is nice.
- 2024-10-01 - modified the setlist notes and the stat counting. Now only counts shows that are marked as part of a tour. Many shows are either "interview" or "no tour", and shouldn't count when tallying show gaps/bustouts/debuts. Likely WIP for now but it should be good.
- 2024-10-08 - Updated most if not all of the tables. Swapped many values for IDs so that tables could be linked with foreign keys. Also working on a databruce website that may or may not ever end up public. And Django requires foreign keys in order to connect tables together. Also cleaned up and double checked many location names, ensuring that they were correct. Added musicbrainz_ids for the various locations in the database.
- 2024-10-14 - added musicbrainz ids to artists, bands, and songs.
- 2024-10-19 - added `tour_legs`, tracking the individual tour legs of a given tour. Typically a grouping of shows based on location, and usually preceded/followed by a gap in shows. Most of these were from Brucebase or Wikipedia, with a few I added on my own, just based on the schedule.
- 2024-10-31 - split the Broadway run into 2 separate tours. Mostly the same show but slightly different and also a different location
- 2024-11-11 - merged `events` and `event_details`, having them separate made no sense. Plus more often than not I'd have to join events when querying details just to get the date or something. Having them combined just makes things much easier.
- 2024-11-13 - major update because I forgot to push many of these to git. Merged all 3 location functions into a single file, much easier to manage that way. As well as a number of updates due to the change above in merging the event tables.
- 2024-11-20 - I updated the releases table to remove the duplicate entries. Originally had releases split by date, but the tracks already pointed to dates, meaning this was unnecessary.
- 2024-11-22
  - added a `snippet count` to the songs table. Which meant adding a new command to do that on an update.
  - fixed some `onstage` items missing the band_id
- 2024-11-23:
  - modified the event numbers. Now, only actual gigs are counted towards the event count, which also changes how the song gaps are calculated. Originally, _every_ event was counted, I didn't even think about skipping cancelled/rescheduled gigs. Plus also interviews/rehearsals and stuff. This means many of the song gaps will change pretty drastically, but it will be more accurate.
- 2024-11-24:
  - Updated the song stats. Was a bit screwy with counting soundchecks and stuff, now corrected. Also updated the "Piano Instrumental" on 1978-05-19 to 'For You'
- 2024-12-03:
  - Added event run tracking. "Runs" are events by the same act at the same venue on different days. Just another stat that might be useful for some. Especially when it comes to getting a list of songs he played during a run instead of just by tour.
- 2024-12-13:
  - added release notes to setlist notes. Basically a note for when a song was included on a retail audio/video release. Also cleaned up the SQL behind it a bit.
- 2025-04-01:
  - added instrument notes to the Devils and Dust shows. He'd rotate around between different keyboards and guitars from song to song.
- 2025-04-02:
  - added proper set structure to 1992/93 shows. Wasn't sure if he actually took a set break during this tour or not. Eventually found confirmation in Backstreets magazine that there was a 30min intermission halfway through the show (usually after Roll of the Dice).
- 2025-04-16:
  - redid archive_links table so that the "created" time is the date I actually added it to archive.org. Had to slightly update the archive function to account.
  - fix songs insert not matching table anymore. I added the `/song:` to all the song urls but never changed that in the insert command.
- 2025-04-23:
  - updated setlist notes so that they split on a semicolon, meaning several notes can be grouped in the song notes column.
- 2025-04-27:
  - Added "tour run" update command.
  - redid the onstage get function, it was kind of a mess with different loops and stuff. Much simpler though should hopefully still handle all cases.
  - moved httpx client to its own function. Realized that every single function was creating its own client instance, rather than just reusing the same one. Using one speeds up the connections as a new one isn't needed for every single request.
  - removed some unneeded dates
- 2025-04-28:
  - cleaned up the setlist notes handling of guests. Originally had song note with guests, but moved those to their own table a while back. Went back and added all the rest. This is ultimately cleaner in the long run, plus probably allows for getting a list of every song someone appeared on.
- 2025-04-29:
  - fixed relations update code. Was only updating the number of appearances and not the first/last events.
  - hopefully properly fixed the onstage code, which was silently failing and not erroring out for some reason.
  - continued moving guest notes to guests
- 2025-04-30:
  - fixed venue parser not grabbing detail from venue name. This could cause an issue where on insert a venue already exists, but without the split detail it's considered "new" and inserted anyway. Venue parser is still a mess.
  - added functions to onstage to get a relation/band id for a given url in the onstage tab. If it doesn't exist, it will insert it and return the new id. Before, if a relation or band didn't exist, it would insert NULL. This is fine for bands, but relations shouldn't be NULL.
- 2025-05-01:
  - fixed one script issue where the event id wasn't returning if the date was invalid.
  - updated setlists to insert "It Takes Two" and "Meeting in the Town Tonight" as proper setlist items. Before these were just snippet notes, which didn't get tallied for the song counts. Will probably go back and change a few other select snippets to be proper setlist items.
- 2025-05-02:
  - fixed event_id get. It was supposed to either return the existing ID for a URL OR create a new one by converting the date to YYYYMMDD and appending a number to the end. It wasn't working like that, instead erroring out and doing nothing, or returning an existing one.
  - Added Studio Sessions runs. Thought about adding these as "tour legs", but they're different enough.
  - checked setlists against 1974-1975 Brucebase, added some missing snippets and other info like noting slow/band versions of TR and Incident.
  - Earlier checked against 2008 as well, so that is up to date.
  - added event_id back to releases. This way, only partially released shows will get a setlist note. Full releases will instead get moved to the top row of the embed and somewhere on the event page on Databruce.
2025-05-04:
  - added `original` bool column to the songs table. True if Bruce, false if not. Figure its easier to check for a bool compared to having to check for "Bruce Springsteen" exactly.
  - added `guest` bool to onstage. Similar concept to the above, easier to check for a T/F than checking string matching.
  - removed the "political rally" tours. These are closer to a leg or a run rather than an actual proper tour. Because of these, they are now grouped under a "political rallies" tour, and each of them is a leg of that tour. 
2025-05-07
  - fixed some setlists with incorrect song_nums, as well as added a missing "People Get Ready" to a show or two.
2025-05-14:
  - added the album collections to the releases
  - removed a few pointless releases unless I feel they need to be added back.
  - added all the 2025 nugs releases to that table
  - added setlist for May 14, 2025 in Manchester
  - fixed event/setlist certainty script not counting for nugs releases
2025-05-15:
  - removed bit in locations where events were only counted before the current date. When really, every event should be counted for the location stats unless it is cancelled.
2025-05-20:
  - Checked 1978 against Brucebase and added notes for things like Growin Up story.
  - redid setlist position commands to ignore 1 song shows.
2025-05-22:
  - Added LOHAD EP to releases
  - fixed setlist notes not counting releases
2025-05-23:
  - started moving database to supabase. The bot points to it now, all that's left is updating the GH workflow.
  - corrected an issue with the `position` update. It wasn't sorting by song_num properly, and was marking the max id for a set as the closer. Which in many cases is correct, but if new songs were added after the fact, those got marked instead. Should be proper now.
2025-06-01:
  - mistakenly thought I could just move over to supabase without any issues. I was wrong. Apparently it just isn't possible to restore a dump of a local database to supabase and expect it to just function. At best, half the tables just get nuked for no reason at all. At worst, some tables just don't make it over. Was hoping to be able to use supabase when the heroku credits run out but that might not happen unless I can find a reliable way to load a pg_dump.