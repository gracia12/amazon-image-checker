# How to test locally

1. Download [Postgres App](https://postgresapp.com/) and run it using the default settings
2. Install `requirements.txt` and `test_requirements.txt` using pip
3. Set the following local environment variables:
4. ![img.png](readme/env_var.png)
5. `DATABASE_URL=postgres://postgres:postgres@localhost:5432/postgres`
6. [How to find](https://www.loom.com/share/c2a34ce03f564adfb3ea41839acb6474) `SLACK_WEBHOOK_URL`
7. Go to [this URL](https://airtable.com/appJRCGueDxxL03DF/tblmITTii8gS7qol1/viwrdzhDjx06V3g9i?blocks=hide) and
   then [follow these steps](https://www.loom.com/share/10b0b9b3945348e8946878799a3220fb) to find `AIRTABLE_BASE_ID`
   , `AIRTABLE_TABLE`, `AIRTABLE_VIEW` - make sure to use [AB test data **
   dev** table](https://airtable.com/appJRCGueDxxL03DF/tbl8ZL55ckXGjZcrf/viwdurtqdJHU7C4fw?blocks=hide)
8. Go to [this URL](https://airtable.com/create/tokens) and
   then [generate new token](https://www.loom.com/share/1933f4f1915e40268fb31748d66ad29e) and store it
   in `AIRTABLE_API_KEY`
9. How to get `LWA_*` and `SP_API_*` from `merchants` table from Heroku's postrgres (use the same credentials as in
   production)

# How to deploy to production

1. Connect the [GitHub repository](https://github.com/ohadnav/amazon-image-checker) to
   Heroku ([article](https://devcenter.heroku.com/articles/git))
2. By default, everytime you push new code to `master` the project rebuilds itself (it'll also happen by default if you
   create a new Heroku app)
3. By default, `scheduler/clock.py` runs periodically
4. Heroku needs the following addons Heroku Postgres and Heroku Scheduler, and Papertrail is also recommended
5. [How to set](https://devcenter.heroku.com/articles/config-vars) environment variables for production:
6. Environment variables are the same as local variables with the following exceptions:
7. The environment variables `LWA_*` and `SP_API_*` do not end with `_TEST`
8. Go to [this URL](https://airtable.com/appJRCGueDxxL03DF/tblmITTii8gS7qol1/viwrdzhDjx06V3g9i?blocks=hide) and
   then [follow these steps](https://www.loom.com/share/10b0b9b3945348e8946878799a3220fb) to find `AIRTABLE_BASE_ID`
   , `AIRTABLE_TABLE`, `AIRTABLE_VIEW` - make sure to use [AB test data **
   prod** table](https://airtable.com/appJRCGueDxxL03DF/tblmITTii8gS7qol1/viwrdzhDjx06V3g9i?blocks=hide)
9. Note that `DATABASE_URL` should be set automatically by Heroku Postgres
10. If that's the first run (i.e. the app was previously successfully run)
    - [that's the SQL query](https://data.heroku.com/dataclips/pvhbhujkwdvprzfuojfkqevtiviq) to create the tables at
    Postgres, can also be found [sql/create_tables.sql](readme/create_tables.sql)

# How to define the AWS - SP API and LWA variables

1. [How to define AWS](https://www.loom.com/share/2724f5fcf9844ff3a0012066ba249c7d) for SP API
2. [How to define LWA](https://www.loom.com/share/55b988571983489cbee66fd029f659a9) from Seller Central
3. [How to rotate LWA secret](https://www.loom.com/share/151335bbe95e454597931a18ccbecd57) - NEEDS TO BE DONE EVERY 90
   DAYS

# How to use the tool

1. [How to create new AB test](https://www.loom.com/share/184ca1fe52c4422b88efa71bf9b78b71)
2. How to stop active AB test change the status in Airtable to inactive
