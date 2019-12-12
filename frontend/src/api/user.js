import axios from "axios"

export default {
	signup(next) {
    axios.post('api/signup')
    .then(function(res) {
      next(res.data)
    })
    .catch(function(err) {
      console.log(err)
      next(0)
    })
	},
  signin(userId, next) {
    axios.post('api/signin', {
      user: userId 
    })
    .then(function() {
      next(true)
    })
    .catch(function(err) {
      console.log(err)
      next(false)
    })
  },
  signout(userId) {
    axios.post('api/signout', {
      user: userId 
    })
    .catch(function(err) {
      console.log(err)
    })
  }
}