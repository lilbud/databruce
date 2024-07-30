# databruce

A PostgreSQL database of Bruce Springsteen's performing career.

### A Brief History
The short version is that this project started in SQLite (which is archived [here](https://github.com/lilbud/Databruce-sqlite)), then after a while moved over to PostgreSQL. I moved over primarily because the bot I wrote to interface with the database moved to Heroku, which required me to move over to Postgres whether I liked it or not. The past year has been spent using various workarounds to import that data into Heroku Postgres. Though recently I said screw it and just went fully with Postgres, leaving SQLite behind. I could go on, but then this README would be novel length.

I'll go into more detail on both Databruce AND Brucebot on my website, and links will be here at some point.

See `CREDITS.md` for an incomplete list of sources and those who've helped.

### Differences from Databruce-sqlite
- Database has been redone in Postgres
- I rewrote all the data collection functions. Mainly so that they were decent, but also incorporating some basic exception/error handling. As well as incorporating async whenever possible. Means that an update now only takes 10sec instead of 20-30sec.
- The following data is now available
    - Setlist opener/closer stats
    - Various song snippets that have been played (Detroit Medley, Reunion Tenth Ave, etc.)
    - Stats on first/only time played, proper premiere/debut indication
    - Better location information, city/state/country
    - Full list of bootlegs that are available
    - and more I'm probably forgetting.