<template>
  <div class="books">
    <b-form inline class="px-4 py-3 bg-secondary">
      <b-form-input v-model="title" placeholder="Search by title" class="mr-3" />
      <b-form-select v-model="genre" :options="genres" class="mr-3" placeholder="asd" />
      <b-form-checkbox v-model="onlyRated" switch><span class="text-light">My Rated</span></b-form-checkbox>
    </b-form>
    <Books v-bind:title="title" :onlyRated="onlyRated" :genre="genre" />
  </div>
</template>

<script>
// @ is an alias to /src
import Books from '../components/Books.vue'
import { mapGetters } from 'vuex'

export default {
  name: 'books',
  components: {
    Books
  },
  data() {
    return {
      title: "",
      onlyRated: false,
      genre: null
    }
  },
  computed: mapGetters('books', [
    'genres'
  ])
}
</script>