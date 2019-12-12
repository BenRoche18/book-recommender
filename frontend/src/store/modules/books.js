import booksApi from '@/api/books'

const state = {
  all: [],
  recommended: []
}

const getters = {
  filter: state => (title, onlyRated, genre) => {
    let reduced = state.all

    if(onlyRated) {
      reduced = reduced.filter(x => x.rating !== undefined)
    }

    if(title !== "")  {
      reduced = reduced.filter(x => x.title.toLowerCase().includes(title.toLowerCase()))
    }
    
    if(genre) {
      reduced = reduced.filter(x => x.genres.includes(genre))
    }

    return reduced.slice(0, 50)
  },
  genres: state => {
    return state.all.reduce((A, x) => {
      x.genres.forEach(genre => {
        if(!A.includes(genre)) {
          A.push(genre)
        }
      })
      return A
    }, [{value: null, text: "Select Genre"}])
  }
}

const actions = {
  getBooks({ commit, rootState }) {
    booksApi.getBooks(rootState.user.userId, books => {
      commit('setBooks', books)
    })
  },
  getRecommended({ commit, rootState }) {
    booksApi.getRecommended(rootState.user.userId, 100, books => {
      commit('setRecommended', books)
    })
  },
  addRating({ commit, rootState }, { id, rating }) {
    booksApi.addRating(rootState.user.userId, id, rating, success => {
      if(success) {
        commit('editRating', { id, rating })
      }
    })
  },
  removeRating({ commit, rootState },{ id }) {
    booksApi.removeRating(rootState.user.userId, id, success => {
      if(success) {
        commit('removeRating', id)
      }
    })
  },
  editRating({ commit, rootState }, { id, rating }) {
    booksApi.editRating(rootState.user.userId, id, rating, success => {
      if(success) {
        commit('editRating', { id, rating })
      }
    })
  }
}

const mutations = {
  setBooks(state, books) {
    state.all = books
  },
  setRecommended(state, books) {
    state.recommended = books
  },
  removeRating(state, bookId) {
    state.all.find(x => x.id === bookId).rating = undefined
  },
  editRating(state, { id, rating }) {
    state.all.find(x => x.id === id).rating = rating
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}