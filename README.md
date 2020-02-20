# RadioCo Alexa

Radioco Alexa contains the server and the lambda required to create an Alexa skill.


## Components

### Lambda

The lambda is in the `alexa` folder and contains the `interaction models` required 
to create an Alexa skill

### Server

The server located in the `backend` folder processes RSS feed and exposes a Alexa api


## Getting Started

### Prerequisites and Installation

Have `docker` installed, change your `.env` variables and then run:

```
./run start_dev
```

You will need to create a superuser to be able to login into the admin panel and start adding some RSS.

```
./run manage createsuperuser
```

After creating the superuser login into the admin panel 
(http://127.0.0.1:8000/admin by default) and create some RSSFeed objects.


Run the following command manually or add it to a `cronjob` to import the feeds
```
./run manage importfeeds
```


A local postgres database is recommended to run this project in production.



## Authors

* **Iago Veloso** - [Github](https://github.com/iago1460/)

## License

This project is licensed under the GNU GPL v3 License - see the [LICENSE](LICENSE) file for details
