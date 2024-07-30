heroku pg:reset --app brucebot-discord --confirm brucebot-discord
heroku pg:push postgresql://postgres:password@localhost:5432/databruce DATABASE_URL --app brucebot-discord