#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import os
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate 
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ ='artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='band', lazy=True)


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  query = Venue.query.order_by('city','state','id').all()
  data = []

  prev_city = ""
  prev_state = ""
  i = -1
  for item in query:
    city = item.city
    state = item.state

    if (city != prev_city or state != prev_state):
      data.append({"city": city, "state": state, "venues":[]})
      i += 1
    num_upcoming_shows = db.session.query(Show).filter(Show.venue_id == item.id, str(Show.start_time) > str(datetime.now())).count()
    data[i]["venues"].append({"id": item.id, "name": item.name, "num_upcoming_shows": num_upcoming_shows})
    prev_city = city
    prev_state = state

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  query = Venue.query.filter(Venue.name.ilike(search)).all()
  query_length = len(query)

  response = {
    "count": query_length,
    "data": []
  }

  for i in range (query_length):
    item={}
    item['id'] = query[i].id
    item['name'] = query[i].name
    item['num_upcoming_shows'] = query_length
    response['data'].append(item)

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  query = Venue.query.filter_by(id=venue_id).first()
  query_shows = db.session.query(Show).filter(Show.venue_id == venue_id)
  past_shows = []
  upcoming_shows = []

  for item in query_shows:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == item.artist_id).one()
    
    show = {
        "artist_id": item.venue_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(item.start_time)
    }

    if (str(item.start_time) < str(datetime.now())):
        past_shows.append(show)
    else:
        upcoming_shows.append(show)
  
    query.past_shows = past_shows
    query.upcoming_shows = upcoming_shows
    query.past_shows_count = len(past_shows)
    query.upcoming_shows_count = len(upcoming_shows)
    print(query.past_shows)

  return render_template('pages/show_venue.html', venue=query)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    venue = Venue(name=form.name.data,
                  city=form.city.data,
                  state=form.state.data,
                  phone=form.phone.data,
                  genres=form.genres.data,
                  address=form.address.data, 
                  website =form.website.data, 
                  seeking_talent=(form.seeking_talent.data=='y'),
                  seeking_description=form.seeking_description.data,
                  image_link=form.image_link.data, 
                  facebook_link=form.facebook_link.data)

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')

  except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Artist could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')




@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue was successfully deleted!')
    return render_template('pages/home.html')
  except ValueError as e:
    error = True
    print(e)
    db.session.rollback()
    flash('Error : Venue could not be deleted!')
  finally:
    db.session.close()
  return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  query = Artist.query.all()
  return render_template('pages/artists.html', artists=query)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  query = Artist.query.filter(Artist.name.ilike(search)).all()
  query_length = len(query)

  response = {
    "count": query_length,
    "data": []
  }

  for i in range (query_length):
    item={}
    item['id'] = query[i].id
    item['name'] = query[i].name
    item['num_upcoming_shows'] = 0
    response['data'].append(item)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  query = Artist.query.filter_by(id=artist_id).first()
  query_shows = db.session.query(Show).filter(Show.artist_id == artist_id)

  past_shows = []
  upcoming_shows = []

  for item in query_shows:
    venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == item.venue_id).one()
    
    show = {
        "venue_id": item.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(item.start_time)
    }

    if (str(item.start_time) < str(datetime.now())):
        past_shows.append(show)
    else:
        upcoming_shows.append(show)
  
    query.past_shows = past_shows
    query.upcoming_shows = upcoming_shows
    query.past_shows_count = len(past_shows)
    query.upcoming_shows_count = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=query)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": [artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link  
    }

  return render_template('forms/edit_artist.html', form=form, artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(request.form)
  
  try:
    artist.name=form.name.data, 
    artist.city=form.city.data, 
    artist.state=form.state.data, 
    artist.phone=form.phone.data, 
    artist.genres=form.genres.data,
    artist.website =form.website.data, 
    artist.seeking_venue=form.seeking_venue.data,
    artist.seeking_description=form.seeking_description.data,
    artist.image_link=form.image_link.data, 
    artist.facebook_link=form.facebook_link.data
    
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except ValueError:
    flash('It was not possible to edit this Artist')
    db.session.rollback()
    return None  
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name=request.form.get('name'), 
    venue.city=request.form.get('city'), 
    venue.state=request.form.get('state'), 
    venue.phone=request.form.get('phone'), 
    venue.address=request.form.get('address'), 
    venue.genres=request.form.getlist('genres'),
    venue.website =request.form.get('website'), 
    venue.seeking_talent=(request.form['seeking_talent']=='y'), 
    venue.seeking_description=request.form.get('seeking_description'),
    venue.image_link=request.form.get('image_link'), 
    venue.facebook_link=request.form.get('facebook_link')

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except ValueError:
    flash('It was not possible to edit this Artist')
    return None  

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  try:
    print(form.seeking_venue.data)
    artist = Artist(name=form.name.data,
                  city=form.city.data,
                  state=form.state.data,
                  phone=form.phone.data,
                  genres=form.genres.data,
                  website =form.website.data, 
                  seeking_venue=(form.seeking_venue.data=='y'),
                  seeking_description=form.seeking_description.data,
                  image_link=form.image_link.data, 
                  facebook_link=form.facebook_link.data)

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

  except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Artist could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')




#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  query = Show.query.all()
  for item in query:
    item.artist_name = Artist.query.get(item.artist_id).name
    item.venue_name = Venue.query.get(item.venue_id).name
    item.artist_image_link = Artist.query.get(item.artist_id).image_link
    item.start_time = item.start_time.strftime("%m/%d/%Y, %H:%M:%S")
  return render_template('pages/shows.html', shows=query)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    show = Show(artist_id=request.form.get('artist_id'), 
                venue_id=request.form.get('venue_id'), 
                start_time=request.form.get('start_time'))


    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    return render_template('pages/home.html')

  except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Artist could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()
'''
# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
