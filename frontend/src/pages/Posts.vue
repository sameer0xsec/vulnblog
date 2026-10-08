<template>
  <h2>Posts</h2>
  <div v-for="p in posts" :key="p.id" style="border:1px solid #eee;padding:12px;margin-bottom:8px;">
    <router-link :to="`/posts/${p.id}`">{{ p.title }}</router-link>
    <p style="font-size:12px;color:#888;">by {{ p.username }}</p>
  </div>
</template>

<script>
import { api } from "../api";
export default {
  data() { return { posts: [] }; },
  async mounted() { this.posts = await api("/posts/"); }
};
</script>
