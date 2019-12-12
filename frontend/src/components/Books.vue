<template>
  <div v-if="loggedIn" id="books">
    <b-row class="m-2">
      <div v-for="book in books" :key="book.id" class="col-xl-2 col-lg-3 col-md-4 col-xs-6 m-3">
        <b-card border-variant="secondary">

          <b-card-text>
            <h4>{{ book.title }}</h4>
            <p>{{ book.genres.join(", ") }}</p>
          </b-card-text>

          <template v-slot:footer>
            <p v-if="isBookRated(book)"><b>{{ book.rating }} / 5</b></p>
            <p v-else><b>N/A</b></p>
            <b-button v-if="isBookRated(book)" @click="showEditRating(book)" variant="info">
              Edit Rating
            </b-button>
            <b-button v-else v-b-modal.addModal @click="showAddRating(book)" variant="info">
              Add Rating
            </b-button>
          </template>

        </b-card>
      </div>
    </b-row>

    <b-modal id="editModal" title="Edit Rating" ok-title="Submit" ok-variant="info" cancel-title="Delete" cancel-variant="danger" @cancel="removeRating" @ok="editRating">
      <h3>{{ book.title }}</h3>
      <b-form-input v-model="book.rating" type="range" min="0" max="5" />
      <strong>Rating: {{ book.rating }}</strong>
    </b-modal>

    <b-modal id="addModal" title="Add Rating" ok-title="Submit" ok-variant="info" ok-only @ok="addRating">
      <h3>{{ book.title }}</h3>
      <b-form-input v-model="book.rating" type="range" min="0" max="5" />
      <strong>Rating: {{ book.rating }}</strong>
    </b-modal>

  </div>
  <div v-else>
    <h1 class="display-5 mt-4">please sign in</h1>
  </div>
</template>

<script>
  // @ is an alias to /src
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'Books',
  props: {
    n: Number,
    title: String,
    onlyRated: Boolean,
    genre: String
  },
  data() {
    return {
      book: {
        id: "",
        rating: 0,
        title: ""
      }
    }
  },
  computed: {
    ...mapState({
      recommended: state => state.books.recommended
    }),
    ... mapGetters('books', {
      filter: 'filter'
    }),
    ...mapGetters('user', [
      'loggedIn'
    ]),
    books() {
      if(this.n) {
        return this.recommended.slice(0,this.n)
      } else {
        return this.filter(this.title, this.onlyRated, this.genre)
      }
    }
  },
  methods: {
    isBookRated(book) {
      return book.rating != undefined
    },
    showEditRating(book) {
      this.book.id = book.id
      this.book.rating = book.rating
      this.book.title = book.title
      this.$bvModal.show('editModal')
    },
    showAddRating(book) {
      this.book.id = book.id
      this.book.title = book.title
      this.$bvModal.show('addModal')
    },
    addRating() {
      this.$store.dispatch('books/addRating', this.book)
      this.$store.dispatch('books/getRecommended')
    },
    removeRating() {
      this.$store.dispatch('books/removeRating', this.book)
      this.$store.dispatch('books/getRecommended')
    },
    editRating() {
      this.$store.dispatch('books/editRating', this.book)
    }
  },
  created() {
    this.$store.dispatch('books/getBooks')
    this.$store.dispatch('books/getRecommended')
  },
  watch: {
    loggedIn: function() {
      this.$store.dispatch('books/getBooks')
      this.$store.dispatch('books/getRecommended')
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
