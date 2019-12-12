LIVE VERSION AT: 



INSTRUCTIONS:

- Use 'python app.py <PORT>' to run server where <PORT> defaults to 8080 when not provided
- Developed using python 3.7.5
- The (single-page) interface was built using VueJS and is statically served by the server:
	> uses axios to perform API calls on server
	> built static files are stored in 'templates' dir
	> vuejs source files are stored in 'frontend' dir (omitting node_modules dir)


DESCRIPTION

The existing user/book data was computed from the Goodbooks dataset [1]. The function 'condenseBookDatasets' merges the Goodbooks dataset into a table of 'book_id', 'title' & 'genre':
	> only includes tags included in genre.txt
	> only keeps popular tags per book (above given threshold)

The parameter 'NUM_USERS' condenses the datasets to only contain books and ratings from this amount of users (trade-off between performance and speed)

The home page displays the user's recommendation. The recommendation algorithm used is a collaboration-based filter described in [2]. K (default 50) features are extracted from the current ratings used to compute prediction matrix.

The search books page is used to filter the books and allows the user to add/edit/delete their ratings. For each of these actions the server is notified and the predicitons matrix is re-computed (in-memory).

Sign in requires a user_id that links to their ratings stored in the dataset. Initially there will be 'NUM_USERS' user_ids (1 .. NUM_USERS). A new user_id is assigned when signing up, which is an increment of the biggest existing user_id:
	> The user_id is stored in a cookie until the user signs out (automatic login)
	> A new user_id wont be saved if no books were rated


REFERENCES
1) Z. Zajac. Goodbooks-10k: a new dataset for book recommendation. Dataset, 2017.
2) N. Becker. Matrix Factorization for Movie Recommendations in Python. Article, 2016