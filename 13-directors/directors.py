#!./venv/bin/python3
import pandas as pd
import numpy as np

MOVIE_DATA = 'movie_metadata.csv'
NUM_TOP_DIRECTORS = 20
MIN_MOVIES = 4
MIN_YEAR = 1960


def parse_csv():
    '''Extracts movies from csv
    returns: DataFrame
    '''
    # Only get these columns.
    cols = ['director_name', 'movie_title', 'title_year', 'imdb_score']
    # Load CSV into DataFrame, Panda's 2-d array.
    df = pd.read_csv(MOVIE_DATA, usecols=cols)

    # Remove any rows that contain NaN
    # Remove directors with too few movies.
    # Remove movies too old.
    '''
    Create groups for each director, which means each unique entry in the
    director name column gets a group. 
    Apply 2 filters, where x is a group. The title year is the same in all groups, so using the mean is conveninent
    '''
    df = df.groupby('director_name').filter(
        lambda x: len(x) >= MIN_MOVIES and x['title_year'].mean() >= MIN_YEAR)

    return df


def get_top_directors(df):
    '''
    data: DataFrame
    return: DataFrame sorted by best directors
    '''
    # This returns the entire df, but sorted according to
    # average score.
    groups = df.groupby('director_name')['imdb_score']
    # Stole it from stackoverflow so not sure of this line,
    # but we create a new DF sorted such that first directors
    # listed have the highest average score.
    df = df.iloc[(-groups.transform('mean')).argsort()]

    return df


def print_results(df):
    '''Print directors ordered by highest average rating. For each director
    print his/her movies also ordered by highest rated movie.
    '''
    fmt_director_entry = '{counter}. {director:<53} {avg:0.1f}'
    sep_line = '-' * 60
    fmt_movie_entry = '{year}] {title:<50} {score}'

    # Hacky, but make a list of names.
    directors = df['director_name'].unique()[:NUM_TOP_DIRECTORS]

    # Organize the entire DF so we have each dir's movies (with all info)
    directors_group = df.groupby('director_name')

    for i, director in enumerate(directors, 1):
        avg = directors_group['imdb_score'].get_group(director).mean()
        print(fmt_director_entry.format(counter=i, director=director, avg=avg))

        print(sep_line)

        curr_director = directors_group.get_group(director).sort_values(
            by=['imdb_score'], ascending=False)

        for i, movie in curr_director.iterrows():
            print(
                fmt_movie_entry.format(year=int(movie['title_year']),
                                       title=movie['movie_title'],
                                       score=movie['imdb_score']))
        print()


def main():
    director_data = parse_csv()
    print_results(get_top_directors(director_data))


if __name__ == '__main__':
    # Cause movie name was being truncated.
    pd.set_option('display.max_columns', None)
    main()