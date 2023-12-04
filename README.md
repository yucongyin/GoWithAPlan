# GoWithAPlan
GoWithAPlan is a travel planner application that assists users in creating, managing, and sharing their  travel itineraries. The application integrates with various mapping and location services to provide users  with the latest information on places of interest, weather, and other relevant data to help them plan  their trips more efficiently.
# to run it locally

## Environment Setup
Pull the code from this repository 
Set up the following Environmental variables in your system
```
export POSTGRES_USER=
export POSTGRES_HOST=
export POSTGRES_PORT=
```
Notice: if you don't set them up, you will be using my AWS RDS postgres database endpoint by default, and since you do not have my password, you won't be able to run the application properly

Add a file called `credentials.py` to your project repository
```
google_api=''
openweather_api=''
postgres_password=''
```
`google_api` your google api token
`openweather_api` your openweather api token
`postgres_possword` from the last step, I mentioned you should create a database, this is the password for your database user

## Run the code
Once you have the environment setup, run `database_init.py` first, this will create a database called `gowithaplan` and create two tables `itinerary` and `locations` in that database
Once the execution for last step is done, run `app.py`
Now the application should be running locally on your computer, visit `localhost:5000` or `127.0.0.1:5000` or `your_ipv4:5000` to access the ui.
