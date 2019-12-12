<template>
  <div class="home">
    <b-form inline class="px-4 py-3 bg-secondary">
      <label for="nRange" class="text-light">Number of recommendations to display: {{ n }}</label>
      <b-form-input id="nRange" v-model="n" type="range" min="1" max="100"></b-form-input>
    </b-form>
    <Books title="" :n="parseInt(n)"/>
  </div>
</template>

<script>
// @ is an alias to /src
import Books from '../components/Books.vue'

export default {
  name: 'home',
  components: {
    Books
  },
  data() {
    return {
      n: 5
    }
  }
}
</script>
