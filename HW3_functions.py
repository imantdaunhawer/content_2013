import json
import requests
import re
import pdb


def get_imdb_id(movies, row):
    '''
    Gets and formats the id from a movie in movies[row].
    Returns: id is a string of length 7.
    '''
    imdb_id = str(movies.iloc[row].imdbID)
    return imdb_id

def format_imdb_id(imdb_id):
    '''Formats a given imdb_id, such that it becomes a string of length 7 with
    trailing zeros in front if neccessary.'''
    if len(imdb_id) < 7:
        imdb_id = imdb_id.zfill(7)
    return imdb_id

def fetch_reviews(movies, row):
    imdb_id = format_imdb_id(get_imdb_id(movies, row))
    api_key = 'j8w2ckhwfsexthfs7a5q2z38' # TODO make sure to not publish this key on github
    
    # get the rotten tomatoes ID from the Alias API
    url = 'http://api.rottentomatoes.com/api/public/v1.0/movies_alias.json'
    options = dict(id = imdb_id,
               type = 'imdb',
               apikey = api_key)
    alias = json.loads(requests.get(url, params=options).text)
    with open("data/movie_alias.json") as json_file: # TODO: remove example file when valid key is available
        alias = json.load(json_file)
    try:
        rt_id = json.dumps(alias['id'])
        title = json.dumps(alias["title"])
    # return None if there is no matching rt_id
    except KeyError:
        return None
    
    # get the top 20 critics movies from the Movie Reviews API
    url = "http://api.rottentomatoes.com/api/public/v1.0/movies/%s/reviews.json" % rt_id
    options = dict(review_type = "top_critic",
                   page_limit = 20,
                   page = 1,
                   country='us',
                   apikey = api_key)
    reviews = json.loads(requests.get(url, params=options).text)
    with open("data/movie_reviews.json") as json_file: # TODO: remove example file when valid key is available
        reviews = json.load(json_file)
    df = pd.read_json(json.dumps(reviews["reviews"][:20]))  # dataframe that contains 20 reviews max
    
    # rename/add columns to the df
    df = df.rename(columns={'date': 'review_date', 'freshness': 'fresh'})
    df["rtid"] = rt_id
    df["imdb"] = imdb_id
    df["title"] = title
    # adjust data types
    df[['critic', 'fresh', "imdb", "publication", "quote", "rtid", "title"]] = \
        df[['critic', 'fresh', "imdb", "publication", "quote", "rtid", "title"]].astype(str)
    
    return df[["critic", "fresh", "imdb", "publication", "quote", "review_date", "rtid", "title"]]

    # TODO: Remove this when RT key is available
# Replaces the original reviews with 

def get_tmdb_info(imdb_id):
    '''retrieve the tmdb_id and title for a movie by imdb_id'''
    api_key = "be1efe7dd1efba809de99666fb2124ab"    # TODO: remove key before pushing to github
    url = "https://api.themoviedb.org/3/find/tt%s?external_source=imdb_id&api_key=%s" % (imdb_id, api_key)
    data = json.loads(requests.get(url).text)
    data = data["movie_results"][0]
    return data["id"], data["title"]

def fetch_tmdb_reviews(movies, row):
    '''retrieves the imdb user reviews for a particular movie and returns them in a json file (dict)'''
    imdb_id = format_imdb_id(get_imdb_id(movies, row))
    tmdb_id, title = get_tmdb_info(imdb_id)
    api_key = "be1efe7dd1efba809de99666fb2124ab"    # TODO: remove key before pushing to github
    url = "http://api.themoviedb.org/3/movie/%s/reviews?api_key=%s" % (tmdb_id, api_key)
    data = json.loads(requests.get(url).text)
    reviews = data["results"]
    reviews = [' '.join(d["content"].encode("utf8").split()) for d in reviews]
    reviews = [re.sub('[^A-Za-z0-9]+', ' ', s) for s in reviews]
    return reviews
    