import sys
import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from flask import Flask, render_template, request, jsonify, abort

RATINGS_FILE = 'dataset/ratings.csv'
BOOKS_FILE = 'dataset/books.csv'
PREDICTIONS_FILE = 'dataset/predictions.csv'
K = 50				# number of features used in singular value decomposition
NUM_USERS = 5000	# existing dataset is condensed to only contain this many existing users (affects performance)
PORT = "8080"		# default port number if not given in command line

# Returns a list of n books recommended to given userId using collaboration-based filtering
def recommendBooks(userId, n=100):
	# find predictions for given userId (index starts from 0 so minus 1)
	try:
		userPredictions = predictions.iloc[userId-1].sort_values(ascending=False)
	except:
		# if user hasn't rated a book yet
		return None

	# find existing ratings by given userId
	currentRatings = ratingsData[ratingsData.user_id == userId]

	# filter predicted ratings to only contain books that haven't been rated yet
	# merge with book dataset
	# name predicted rating column
	# sort by descending predicted rating
	# truncate to only include top n books
	recommended = (booksData[~booksData['book_id'].isin(currentRatings['book_id'])].
		merge(pd.DataFrame(userPredictions), on='book_id').
		rename(columns = {userId-1: 'predicted_rating'}).
		sort_values('predicted_rating', ascending=False).
		iloc[:n, :-1])

	return recommended


# Returns predictions dataset that has been pre-computed
def readPredictions():
	predictions = pd.read_csv(PREDICTIONS_FILE)

	# convert column type to int as represents 'book_id'
	predictions.columns = predictions.columns.astype(int)
	predictions.columns.name = 'book_id'

	return predictions


# Returns a dataset where each column represents a book and each row represents a user with each cell as a predicted rating
def computePredictedRatings(ratingsData, booksData):
	ratingsMatrix, userMeanRatings, bookIds = computeRatingsMatrix(ratingsData, booksData)
	U, sigma, Vt = svd(ratingsMatrix)

	# compute predicted ratings by composing U, sigma, Vt and unnormalizing with users mean
	return pd.DataFrame(np.dot(np.dot(U, sigma), Vt) + userMeanRatings, columns=bookIds)


# Performs singular value decomposition on matrix, returning U, sigma and Vt matrices
def svd(matrix):
	# factorize ratingsMatrix using singular value decomposition
	# U represents user features, sigma is essentially weights and Vt is movie features
	U, sigma, Vt = svds(matrix, k=K)

	# convert sigma value into matrix
	return U, np.diag(sigma), Vt


# Returns noramlized matrix with 'book_id' as columns, 'user_id' as rows and 'rating' as cell along with user means and list of bookIds
def computeRatingsMatrix(ratingsData, booksData):
	# pivot to create required matrix
	ratings = ratingsData.pivot(index='user_id', columns='book_id', values='rating').fillna(0)
	bookIds = ratings.columns

	# convert DataFrame to numpy array
	ratings = ratings.to_numpy()

	# normalize ratings by each users mean
	userMeanRatings = np.mean(ratings, axis=1).reshape(-1, 1)
	return (ratings - userMeanRatings), userMeanRatings, bookIds


# Joins and condenses the 'books', 'book_tags' and 'tags' datasets from Goodbooks-10k
# Only includes genres specified in genre text file and with tag count above given threshold
# Saves a csv file with headings: book_id, title, genres
def condenseBookDatasets(tagThreshold=100):
	BOOKS_FILE = 'dataset/old_books.csv'
	BOOK_TAGS_FILE = 'dataset/book_tags.csv'
	TAGS_FILE = 'dataset/tags.csv'

	# load tags dataset linking 'tag_id' to 'tag_name' and filter
	tagsData = condenseTagsDataset(pd.read_csv(TAGS_FILE))

	# load existing book_tags dataset linking 'tag_id' to 'goodreads_book_id'
	bookTagsData = pd.read_csv(BOOK_TAGS_FILE)

	# merge datasets so 'goodreads_book_id' links to 'tag_name' (omitting records with no 'tag_name')
	# remove 'tag_id' field from dataset as 'tag'name' now linked
	bookTagsData = pd.merge(tagsData, bookTagsData, on='tag_id')

	# filter book tag records with 'count' less than threshold
	bookTagsData = bookTagsData[bookTagsData['count'] <= tagThreshold]
	
	# group records with same 'goodreads_book_id' putting 'tag_name' in array
	bookTagsData = bookTagsData.groupby('goodreads_book_id').tag_name.apply(list)
	
	# load existing books dataset (only relevant fields)
	booksData = pd.read_csv(BOOKS_FILE).loc[:, ['book_id', 'goodreads_book_id', 'title']]

	# merge books dataset with computed genre dataset (omitting irrelavant fields)
	booksData = pd.merge(booksData, bookTagsData, on='goodreads_book_id').loc[:, ['book_id', 'title', 'tag_name']]

	# rename 'tag_name' to 'genres'
	booksData.columns = ['book_id', 'title', 'genres']
	
	# save new books dataset
	booksData.to_csv('dataset/books.csv', index=False)


# Returns ratings and books dataset that only use first N users and the books they have rated
def condenseDatasets(ratingsData, booksData, N=100):
	ratingsData = condenseRatingsDataset(ratingsData, N)

	# find list of 'book_id' in condensed ratings
	bookIds = ratingsData.book_id.unique()

	# filter books dataset to only contain these 'book_id'
	booksData = booksData[booksData.book_id.isin(bookIds)]

	return ratingsData, booksData


# Returns dataset only containing ratings from first N users
def condenseRatingsDataset(ratingsData, N=100):
	return ratingsData[ratingsData.user_id <= N]

# Filters tag dataset to only include 'tag_name' in given genres text file that have a 'count' above the threshold
def condenseTagsDataset(tagsData):
	GENRES_FILE = 'dataset/genres.txt'

	# load genres from text file and reduce into an array
	genresData = open(GENRES_FILE, 'r')
	genres = genresData.read().lower().replace(' ', '-').split('\n')
	genresData.close()

	# filter records from tags dataset whose 'tag_name' isn't in genres
	return tagsData[tagsData.tag_name.isin(genres)]


def getUserRatings(ratingsData, userId):
	return ratingsData[ratingsData.user_id == userId]


# Returns dataset containing all books along with the rating from a given userId (null if not rated)
def getBooks(userId):
	return pd.merge(booksData, getUserRatings(ratingsData, userId), on="book_id", how="left")


def addRating(userId, bookId, rating):
	global ratingsData, predictions
	ratingsData = ratingsData.append({'user_id': userId, 'book_id': bookId, 'rating': rating}, ignore_index=True)

	# recompute predictions data
	print("Updating recommendations...")
	predictions = computePredictedRatings(ratingsData, booksData)


def removeRating(userId, bookId):
	global ratingsData, predictions
	ratingsData = ratingsData[(ratingsData.user_id != userId) | (ratingsData.book_id != bookId)]

	# recompute predictions data
	print("Updating recommendations...")
	predictions = computePredictedRatings(ratingsData, booksData)


def editRating(userId, bookId, rating):
	global ratingsData, predictions
	# remove
	ratingsData = ratingsData[(ratingsData.user_id != userId) | (ratingsData.book_id != bookId)]
	# add new
	ratingsData = ratingsData.append({'user_id': userId, 'book_id': bookId, 'rating': rating}, ignore_index=True)

	# recompute predictions data
	print("Updating recommendations...")
	predictions = computePredictedRatings(ratingsData, booksData)


def getUserIds():
	return ratingsData.user_id.unique().tolist()

# Setup flask backend
app = Flask(__name__, static_folder = "templates/static")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")
def index():
	return render_template('index.html')


@app.route('/api/books')
def books():
	try:
		userId = int(request.args.get('user'))
	except:
		# send bad request if user not given as query parameter
		abort(400)

	books = getBooks(userId)
	del books['user_id']
	return books.to_json(orient='records')


@app.route('/api/recommended')
def recommended():
	try:
		userId = int(request.args.get('user'))
	except:
		# send bad request if user not given as query parameter
		abort(400)

	try:
		n = int(request.args.get('n'))
		books = recommendBooks(userId, n)
		if books == None:
			return {}
	except:
		# use a default n if not given as parameter
		books = recommendBooks(userId)	

	return books.to_json(orient='records')


@app.route('/api/rating', methods=['POST'])
def postRating():
	req = request.get_json()
	try:
		addRating(int(req['user']), req['id'], int(req['rating']))
	except:
		abort(400)
	return "Rating Added"


@app.route('/api/rating', methods=['DELETE'])
def delRating():
	req = request.get_json()
	removeRating(int(req['user']), req['id'])
	try:
		removeRating(int(req['user']), req['id'])
	except:
		abort(400)
	return "Rating Removed"


@app.route('/api/rating', methods=['PUT'])
def putRating():
	req = request.get_json()
	try:
		editRating(int(req['user']), req['id'], int(req['rating']))
	except:
		abort(400)
	return "Rating Edited"


@app.route('/api/signin', methods=['POST'])
def signin():
	global usersLoggedIn

	req = request.get_json()
	try:
		if int(req['user']) not in getUserIds():
			return "Invalid user id", 400
		elif req['user'] not in usersLoggedIn:
			usersLoggedIn.append(req['user'])
	except:
		abort(400)
	return "Signed In Successfully"


@app.route('/api/signup', methods=['POST'])
def signup():
	global usersLoggedIn

	i = len(getUserIds()) + 1
	while str(i) in usersLoggedIn:
		i += 1
	usersLoggedIn.append(str(i))
	return str(i)


@app.route('/api/signout', methods=['POST'])
def signout():
	global usersLoggedIn

	req = request.get_json()
	try:
		usersLoggedIn.remove(str(req['user']))
	except:
		abort(400)
	return "Signed Out Successfully"



if __name__ == '__main__':
	print("Fetching datasets...")
	ratingsData, booksData = condenseDatasets(pd.read_csv(RATINGS_FILE), pd.read_csv(BOOKS_FILE), NUM_USERS)
	print("Computing recommendations...")
	predictions = computePredictedRatings(ratingsData, booksData)
	usersLoggedIn = []

	# overide PORT if given as argument
	if len(sys.argv) > 1:
		PORT = sys.argv[1]

	app.run("0.0.0.0", PORT)