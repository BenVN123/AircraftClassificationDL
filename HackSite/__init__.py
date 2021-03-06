import os
from flask import Flask, render_template, request, flash, redirect, url_for, session, g
import secrets
from PIL import Image

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='uPqECIPsjfu7qQ93MwHiyDr73QyhyjUphSnehNAt',
        DATABASE=os.path.join(app.instance_path, 'HackSite.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import Predict
    from Predict import pred

    from . import db
    db.init_app(app)

    from HackSite.db import get_db

    def save_picture(form_picture):
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/temp', picture_fn)

        output_size = (100, 100)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)

        return picture_fn

    @app.before_request
    def load_logged_in_user():
        auth = session.get('user_id')

        if auth is None:
            g.user = None
        else:
            g.user = {'id':1, 'name':'auth'}

    @app.route('/', methods=('GET', 'POST'))
    def index():
        if request.method == 'POST':
            pic = request.form['uploaded_img']

            picture_file=save_picture(pic)

            output = pred(picture_file)
            output = output[0]

            if output == 0:
                output = 'Civilian'

            else:
                output = 'Military'
            os.remove(picture_file)

            return render_template('index.html', output=output)


        return render_template('index.html')

    @app.route('/questions', methods=('GET', 'POST'))
    def questions():
        db = get_db()
        questions = db.execute('SELECT * FROM question').fetchall()
        if request.method == 'POST':
            q = request.form['q']
            error = None
            
            if len(q) > 255:
                error = 'Question should not exceed 255 characters.'

            if error is None:
                db.execute('INSERT INTO question (body) VALUES (?)', (q,))
                db.commit()

                return redirect(url_for('questions'))

            flash(error)

        return render_template('questions.html', questions=questions)
    
    @app.route('/stats')
    def stats():
        return render_template('stats.html')

    @app.route('/about')
    def about():
        return render_template('about.html')
       
    @app.route('/auth', methods=('GET', 'POST'))
    def auth():
        if g.user:
            return redirect(url_for('index'))
        if request.method == 'POST':
            p = request.form['password']
            error = None

            if p != 'password:)':
                error = 'Invalid password.'

            if error is None:
                session['user_id'] = '1'
                
                return redirect(url_for('index'))

            flash(error)

        return render_template('auth.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    @app.route('/<int:id>', methods=('GET', 'POST'))
    def answer(id):
        db = get_db()
        answers = db.execute('SELECT * FROM answer WHERE question_id = ?', (id,)).fetchall()
        if request.method == 'POST':
            a = request.form['body']
            error = None

            if len(a) > 255:
                error = 'Max length: 255'

            if error is None:
                db.execute('INSERT INTO answer (question_id, body) VALUES (?,?)', (id, a))
                db.commit()
                return redirect(url_for('answer', id=id))

            flash(error)

        return render_template('answer.html', id=id, answers=answers)

    return app