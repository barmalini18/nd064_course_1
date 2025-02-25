import sqlite3

import logging
import sys
from datetime import datetime
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# global connection counter
connection_count = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global connection_count
    connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error('A non-existing article is accessed and a 404 page is returned.'.format(id=post_id)) 
      return render_template('404.html'), 404
    else:
      app.logger.info('Article "{title}" retrieved.'.format(title=post['title']))  
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The "About Us" page is retrieved.')
    return render_template('about.html')

# Build the /healthz endpoint for the TechTrends application. The endpoint should return the following response:
#    An HTTP 200 status code
#    A JSON response containing the result: OK - healthy message
@app.route('/healthz')
def healthz():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute('SELECT * FROM posts')
        connection.close()
        response = app.response_class(
                response=json.dumps({"result":"OK - healthy"}),
                status=200,
                mimetype='application/json'
        )
    except Exception:
         response = app.response_class(
                response=json.dumps({"result":"Error - unhealthy"}),
                status=500,
                mimetype='application/json'
        )
    return response

#Build a /metrics endpoint that would return the following:
#   An HTTP 200 status code
#   A JSON response with the following metrics:
#       Total amount of posts in the database
#       Total amount of connections to the database. For example, accessing an article will query the database, hence will count as a connection.
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_count = len(posts)
    response = app.response_class(
            response=json.dumps({"db_connection_count": connection_count, "post_count": post_count}),
            status=200,
            mimetype='application/json'
    )
    connection.close()
    return response


# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('Article "{title}" created.'.format(title=title))
            return redirect(url_for('index'))

    return render_template('create.html')

# Extend the TechTrends application to log the following events:
# An existing article is retrieved. The title of the article should be recorded in the log line.
# A non-existing article is accessed and a 404 page is returned.
# The "About Us" page is retrieved.
# A new article is created. The title of the new article should be recorded in the logline.

# start the application on port 3111
if __name__ == "__main__":
   ################################################## 
   # Setup logging                                  #
   # followed this video-tutorial                   #
   # https://www.youtube.com/watch?v=pxuXaaT1u3k    #
   # for more professional logging look and feel    # 
   ##################################################
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler =  logging.StreamHandler(sys.stderr)
    handlers = [stderr_handler, stdout_handler]
    format="%(asctime)s, %(levelname)s, %(message)s"
    datefmt="%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
        format=format,
        datefmt=datefmt,
      #  filename="basic.log",
    )
    app.run(host='0.0.0.0', port='3111')
