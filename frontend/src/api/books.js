import axios from "axios"

export default {
	getBooks(userId, next) {
    axios.get('api/books', {
      params: {
        user: userId
      }
    })
    .then(function(res) {
      next(res.data.map(book => {
        return {
          id: book.book_id,
          title: book.title,
          genres: eval(book.genres),
          rating: book.rating ? book.rating : undefined
        }
      }))
    })
    .catch(function(err) {
      console.log(err)
      next([])
    })
	},

  getRecommended(userId, n, next) {
    axios.get('api/recommended', {
      params: {
        user: userId,
        n: n
      }
    })
    .then(function(res) {
      next(res.data.map(book => {
        return {
          id: book.book_id,
          title: book.title,
          genres: eval(book.genres)    
        }
      }))
    })
    .catch(function(err) {
      console.log(err)
      next([])
    })
  },

  addRating(userId, bookId, rating, next) {
    axios.post('api/rating', {
      user: userId,
      id: bookId,
      rating
    })
    .then(function() {
      next(true)
    })
    .catch(function(err) {
      console.log(err)
      next(false)
    })
  },

  removeRating(userId, bookId, next) {
    axios.delete('api/rating', {
      data: {
        user: userId,
        id: bookId
      }
    })
    .then(function() {
      next(true)
    })
    .catch(function(err) {
      console.log(err)
      next(false)
    })
  },

  editRating(userId, bookId, rating, next) {
    axios.put('api/rating', {
      user: userId,
      id: bookId,
      rating
    })
    .then(function() {
      next(true)
    })
    .catch(function(err) {
      console.log(err)
      next(false)
    })
  }
}