from flask import Flask, redirect, render_template, request, url_for, g
from model import get_format_tweets
from form import URLForm, TweetPullerForm
from Scrapers import NYT_Scraper, CBSNews_Scraper, HuffPo_Scraper



app = Flask(__name__)
app.config['SECRET_KEY'] = 'snoopaloop'

@app.route('/')
def home():
    return render_template('home.html', form=URLForm(request.form))

@app.route('/scrape/', methods=['post'])
def scrape():
    url = URLForm(request.form).url.data
    source = URLForm(request.form).source.data
    if source == 'nytimes':
        text_dict =  NYT_Scraper(url).dump_all()
    if source == 'cbsnews':
        text_dict = CBSNews_Scraper(url).dump_all()
    if source == 'huffpo':
        text_dict = HuffPo_Scraper(url).dump_all()

    return render_template('results.html', text_dict=text_dict)

@app.route('/pull_tweets/', methods=['post'])
def pull_tweets():
    data = TweetPullerForm(request.form).url.data
    formatted_tweets = get_format_tweets(data)
    if formatted_tweets == []:
        return render_template('formatted_tweets.html',
                               tweets=['No tweets on this page!'])
    else:
        return render_template('formatted_tweets.html',
                               tweets=formatted_tweets)

# @app.route('/results/')
# def results():
#     print request.data
#     return render_template('results.html', text=)
