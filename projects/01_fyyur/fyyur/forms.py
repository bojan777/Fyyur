from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, RadioField
from wtforms.validators import DataRequired, AnyOf, URL




state_choices = [
        ('AL', 'AL'),
        ('AK', 'AK'),
        ('AZ', 'AZ'),
        ('AR', 'AR'),
        ('CA', 'CA'),
        ('CO', 'CO'),
        ('CT', 'CT'),
        ('DE', 'DE'),
        ('DC', 'DC'),
        ('FL', 'FL'),
        ('GA', 'GA'),
        ('HI', 'HI'),
        ('ID', 'ID'),
        ('IL', 'IL'),
        ('IN', 'IN'),
        ('IA', 'IA'),
        ('KS', 'KS'),
        ('KY', 'KY'),
        ('LA', 'LA'),
        ('ME', 'ME'),
        ('MT', 'MT'),
        ('NE', 'NE'),
        ('NV', 'NV'),
        ('NH', 'NH'),
        ('NJ', 'NJ'),
        ('NM', 'NM'),
        ('NY', 'NY'),
        ('NC', 'NC'),
        ('ND', 'ND'),
        ('OH', 'OH'),
        ('OK', 'OK'),
        ('OR', 'OR'),
        ('MD', 'MD'),
        ('MA', 'MA'),
        ('MI', 'MI'),
        ('MN', 'MN'),
        ('MS', 'MS'),
        ('MO', 'MO'),
        ('PA', 'PA'),
        ('RI', 'RI'),
        ('SC', 'SC'),
        ('SD', 'SD'),
        ('TN', 'TN'),
        ('TX', 'TX'),
        ('UT', 'UT'),
        ('VT', 'VT'),
        ('VA', 'VA'),
        ('WA', 'WA'),
        ('WV', 'WV'),
        ('WI', 'WI'),
        ('WY', 'WY')
    ]



genres_choices=[
        ('Alternative', 'Alternative'),
        ('Blues', 'Blues'),
        ('Classical', 'Classical'),
        ('Country', 'Country'),
        ('Electronic', 'Electronic'),
        ('Folk', 'Folk'),
        ('Funk', 'Funk'),
        ('Hip_Hop', 'Hip-Hop'),
        ('Heavy_Metal', 'Heavy Metal'),
        ('Instrumental', 'Instrumental'),
        ('Jazz', 'Jazz'),
        ('Musical_Theatre', 'Musical Theatre'),
        ('Pop', 'Pop'),
        ('Punk', 'Punk'),
        ('R_B', 'R&B'),
        ('Reggae', 'Reggae'),
        ('Rock_n_Roll', 'Rock n Roll'),
        ('Soul', 'Soul'),
        ('Other', 'Other')
    ]




class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    seeking_description = StringField(
        'seeking_description'
    )
    seeking_talent = RadioField('seeking_talent', choices=[('y','Yes'),('n','No')], default='y')


    def validate(self):
        """Define a custom validate method in your Form:"""
        rv = Form.validate(self)
        if not rv:
            return False
        if not set(self.genres.data).issubset(dict(genres_choices).keys()):
            self.genres.errors.append('Invalid genre.')
            return False
        if self.state.data not in dict(state_choices).keys():
            self.state.errors.append('Invalid state.')
            return False
        # if pass validation
        return True











class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    seeking_description = StringField(
        'seeking_description'
    )
    seeking_venue = RadioField('seeking_venue', choices=[('y','Yes'),('n','No')], default = 'y')

    def validate(self):
        """Define a custom validate method in your Form:"""
        rv = Form.validate(self)
        if not rv:
            return False
        if not set(self.genres.data).issubset(dict(genres_choices).keys()):
            self.genres.errors.append('Invalid genre.')
            return False
        if self.state.data not in dict(state_choices).keys():
            self.state.errors.append('Invalid state.')
            return False
        # if pass validation
        return True








