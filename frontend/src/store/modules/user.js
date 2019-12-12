import userApi from '@/api/user'

const state = {
  userId: ""
}

const getters = {
  loggedIn: state => {
    if(state.userId) {
      return true
    } else {
      return false
    }
  }
}

const actions = {
  setUser({ commit }, user) {
    if(user) {
      document.cookie = "user=" + user.userId
    } else if(document.cookie) {
      user = { userId: document.cookie.split('=')[1] }
    }
    userApi.signin(user.userId, success => {
      if(success) {
        commit('setUser', user)
      }
    })
  },

  removeUser({ commit, state }) {
    document.cookie = "user=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
    userApi.signout(state.userId)
    commit('setUser', "")
  },

  signup({ commit }) {
    userApi.signup(userId => {
      if(userId) {
        commit('setUser', { userId })
      }
    })
  }
}

const mutations = {
  setUser(state, { userId }) {
    state.userId = userId
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}