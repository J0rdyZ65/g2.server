# g2.server
G2 flask based server hosted on public clouds

## Installation on PythonAnywhere

- In your PA account (a free beginner is enough), from your home directory (e.g. /home/foobar) clone this repository:

        git clone https://github.com/J0rdyZ65/g2.server.git

- Create a new web app and set the project_home in the corresponding WSGI configuration file (typically located at */var/www/foobar_pythonanywhere_com_wsgi.py*) to '/home/foobar/g2.server'

- In the web dashboard enable the force HTTPS

- Add to the .bashrc file in the home directory the following line:
 
        export FLASK_APP=g2.server/flaskr
        
- Create the instance folder in your home direcory:

        cd
        mkdir instance

- Create the *config.py* file in the instance folder using your preferred editor or the PA web editor:

        cd instance
        vi config.py

- The *config.py* file should contain at least the following four variables:

        # G2 server auth url
        G2_SERVER_AUTH_URL = '<url-to-be-inserted-by-the-user>'
        # Base URL of this server
        G2_SERVER_AUTH_COMPLETE_URL = '<your-pushbullet-redirect-url-on-success>'
        # G2 client id as registered on the pushbullet site
        PUSHBULLET_G2_CLIENT_ID = '<your-pushbullet-client-id-here>'
        # G2 client secret as registered on the pushbullet site
        PUSHBULLET_G2_CLIENT_SECRET = '<your-pushbullet-client-secret-here>'

- Initialize the database running the following command from your home directory:

        flask init-db

- Create a daily (or hourly if your PA account allows it) task to purge the stale database entries using the following command:

        flask purge-db
