Setlist Notes:
    add note when track is included on retail release

    all notes:
        existing (ones in the setlist table)
        snippet (comma list of snippets for song)
        stat_notes:
            First Time Played
                premiere true
                `[X] First Time Played`
            Bustout
                premiere false, last >= 50, next != last
                `[X] Bustout, LTP YYYY-MM-DD (XX Shows)`
            Tour Debut
                debut true, tour NOT rehearsal or non-tour, last is not empty or equal to first
                `[X] Tour Debut, LTP YYYY-MM-DD (XX Shows)`
            Only Time Played
                last = first, next = last
                get count of plays for valid sets and make sure it equals 1
                `[X] Only Time Played`

        release_note
            Release
                join `releases`, if present there then add note
                `[X] Released On [RELEASE NAME]`
        
        
        
    <!-- Position Stats? 
        Taken from LTTMP by Justin Mason
        Note for when a song is Show/Set Opener or Closer a number of times
        LTTMP seems to cut off at 9 times, could probably go with no cap
        `[X] NUM/MAX of times as [Position]`
            OR
        `[X] Only Time as [Position]` -->