# g2.server
G2 flask based server hosted on public clouds

## Installation on PythonAnywhere

- In your PA account (a free beginner is enough), from your home directory (e.g. /home/foobar) clone this repository:

        git clone https://github.com/J0rdyZ65/g2.server.git

- Create a new web app and set the project_home in the corresponding WSGI configuration file (typically located at */var/www/foobar_pythonanywhere_com_wsgi.py*) to '/home/foobar/g2.server'

- In the web dashboard enable the force HTTPS

- Add to the .bashrc file in the home directory the following line:
 
         export FLASK_APP=g2.server/flaskr

- Initialize the database running the following command from your home directory:

        flask init-db

- Create a daily (or hourly if your PA account allows it) task to purge the stale database entries using the following command:

        flask purge-db
