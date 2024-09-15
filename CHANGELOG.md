# Changelog
## This file will contain a log of major changes to the database. Usually fixes or whatnot. I've been keeping this list in a local file but never added it here.

- 2024-08-02 - First release of the 2.0 version
- 2024-08-17 - Brucebase updated a ton of urls on their site. Changing urls from showing "early/late/morning/evening/etc" to just having an incrementing letter after the date that increments by date (for multi event dates) or by multiple unknown dates. This is still ongoing and as I catch the new URLs I'm updating them in the database
- 2024-08-18 - fixed songs on High Hopes having the incorrect release_id in 'release_tracks'. Was instead pointing to the BITUSA Live DVD
- 2024-08-22 - fixed setlist note numbering. For unknown reasons, sometimes the number attached to a note wouldn't match the number of notes. Like a note saying "2" when there is only a single note for a show. Managed to fix by removing number from `setlist_notes` and adding a similar function to `setlists_by_set_and_date`
- 2024-08-22 - fix `songs_after_release`. It was showing far too high of a number for the number of times a song was played *after* its first studio release. Like Price You Pay showing only 77 total plays and 120 after release. Simply had to put a "distinct" in the count
- 2024-09-11 - fix `nugs_releases`. Originally this table had a column pointing to `live.brucespringsteen.net`. However, as of today, they switched over fully to `nugs.net`. I had to update the URLs to match correctly
- 2024-09-15 - fix incorrect artist associated with Gloria. Mistakenly set to Roy Orbison when it should've been set to Leon Rene.
