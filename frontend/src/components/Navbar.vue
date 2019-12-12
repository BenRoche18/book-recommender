<template>
  <div>
    <b-navbar toggleable="lg" type="dark" variant="info">
      <b-navbar-brand to="/">Book Recommender</b-navbar-brand>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav>

        <b-navbar-nav>
          <b-nav-item to="/books">Search Books</b-nav-item>
        </b-navbar-nav>

        <!-- Right aligned nav items -->
        <b-navbar-nav class="ml-auto">
          <b-nav-item v-if="loggedIn" @click="signOut">
            <b-badge class="mr-2">{{ userId }}</b-badge>
            Sign Out
          </b-nav-item>
          <b-nav-item v-if="!loggedIn" v-b-modal.signinModal>Sign In</b-nav-item>
          <b-nav-item v-if="!loggedIn" @click="signup">Sign Up</b-nav-item>
        </b-navbar-nav>

      </b-collapse>
    </b-navbar>

    <b-modal id="signinModal" title="Sign In" ok-title="Signin" ok-variant="info" ok-only @ok="signIn">
      <b-form-input v-model="idInput" type="number" placeholder="Enter User ID"/>
    </b-modal>

    <b-modal ref="signupModal" title="Sign Up" ok-variant="info" ok-only>
      <p>You have been assigned the user id: {{ userId }}</p>
    </b-modal>

  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'Navbar',
  data() {
    return {
      idInput: ""
    }
  },
  computed: {
    ...mapState({
      userId: state => state.user.userId
    }),
    ...mapGetters('user', [
      'loggedIn'
    ])
  },
  methods: {
    signIn(bvModalEvt) {
      if(this.idInput) {
        this.$store.dispatch('user/setUser', { userId: this.idInput })
      } else {
        bvModalEvt.preventDefault()
      }
    },
    signOut() {
      this.$store.dispatch('user/removeUser')
    },
    signup() {
      this.$store.dispatch('user/signup')
      this.$refs['signupModal'].show()
    }
  },
  created() {
    this.$store.dispatch('user/setUser')
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
