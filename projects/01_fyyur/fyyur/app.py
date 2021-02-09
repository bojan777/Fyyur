#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import os
import sys

from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for, 
    jsonify, 
    abort
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate 
from datetime import datetime
from models import app, db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

 
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
  locals = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()

  for place in places:
      locals.append({
          'city': place.city,
          'state': place.state,
          'venues': [{
              'id': venue.id,
              'name': venue.name,
          } for venue in venues if
              venue.city == place.city and venue.state == place.state]
      })
  return render_template('pages/venues.html', areas=locals)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()

  response = {
      "count": len(venues),
      "data": []
  }

  for venue in venues:
      response["data"].append({
          'id': venue.id,
          'name': venue.name,
      })

  return render_template('pages/search_venues.html', results=response, \
    search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
      filter(
          Show.venue_id == venue_id,
          Show.artist_id == Artist.id,
          Show.start_time < datetime.now()
      ).\
      all()


  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
      filter(
          Show.venue_id == venue_id,
          Show.artist_id == Artist.id,
          Show.start_time > datetime.now()
      ).\
      all()

  venue = Venue.query.filter_by(id=venue_id).first_or_404()

  data = {
          'id': venue.id,
          "name": venue.name,
          "genres": [venue.genres],
          "city": venue.city,
          "state": venue.state,
          "phone": venue.phone,
          "address": venue.address,
          "website": venue.website,
          "facebook_link": venue.facebook_link,
          "seeking_talent": venue.seeking_talent,
          "seeking_description": venue.seeking_description,
          "image_link": venue.image_link,  
          'past_shows': [{
              'artist_id': artist.id,
              "artist_name": artist.name,
              "artist_image_link": artist.image_link,
              "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
          } for artist, show in past_shows],
          'upcoming_shows': [{
              'artist_id': artist.id,
              'artist_name': artist.name,
              'artist_image_link': artist.image_link,
              'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
          } for artist, show in upcoming_shows],
          'past_shows_count': len(past_shows),
          'upcoming_shows_count': len(upcoming_shows)
      }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue = Venue()
      form.populate_obj(venue)
      venue.seeking_talent=(form.seeking_talent.data=='y')
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except ValueError as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Artist could not be listed.')
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))

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

  return render_template('pages/search_artists.html', results=response, \
    search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
      filter(
          Show.artist_id == artist_id,
          Show.venue_id == Venue.id,
          Show.start_time < datetime.now()
      ).\
      all()


    upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
      filter(
          Show.artist_id == artist_id,
          Show.venue_id == Venue.id,
          Show.start_time < datetime.now()
      ).\
      all()

    artist = Artist.query.filter_by(id=artist_id).first_or_404()


    data = {
            'id': artist.id,
            "name": artist.name,
            "genres": [artist.genres],
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,  
            'past_shows': [{
                'venue_id': venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for venue, show in past_shows],
            'upcoming_shows': [{
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for venue, show in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  print(form.seeking_venue.data)

  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  print(form.seeking_venue.data)
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
  print(venue_id)
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)


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
    flash('It was not possible to edit this Venue')
    db.session.rollback()
    return None  
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      print(form.seeking_venue.data)
      artist = Artist()
      form.populate_obj(artist)
      artist.seeking_venue=(form.seeking_venue.data=='y')
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
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))

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
  try:
    form = ShowForm(request.form)
    show = Show()
    form.populate_obj(show)
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

# if __name__ == '__main__':
#     app.run()

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)