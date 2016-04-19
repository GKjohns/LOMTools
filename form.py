from flask_wtf import Form
from wtforms import SelectField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, url

class URLForm(Form):
    sources = [('nytimes','The New York Times'),
               ('cbsnews', 'CBS News'),
               ('huffpo', 'The Huffington Post')]
    url = URLField('url', validators=[DataRequired(), url()])
    source = SelectField('source', validators=[DataRequired()],
        choices=sources)

class TweetPullerForm(Form):
    url = URLField('url', validators=[DataRequired(), url()])
