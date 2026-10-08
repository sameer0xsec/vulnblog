<template>
  <h2>Search</h2>
  <form @submit.prevent="doSearch">
    <input v-model="q" placeholder="search posts..." />
    <button type="submit">Search</button>
  </form>
  <div v-if="data">
    <!-- VULN: reflected XSS — raw query string rendered as HTML.
         Try q = <img src=x onerror=alert(document.cookie)> -->
    <p>Showing results for: <span v-html="data.query"></span></p>
    <ul><li v-for="r in data.results" :key="r.id">{{ r.title }}</li></ul>
  </div>
</template>

<script>
import { api } from "../api";
export default {
  data() { return { q: "", data: null }; },
  methods: {
    async doSearch() {
      this.data = await api(`/posts/search?q=${encodeURIComponent(this.q)}`);
    }
  }
};
</script>
