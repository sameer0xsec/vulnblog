<template>
  <div v-if="post">
    <h2>{{ post.title }}</h2>
    <!-- VULN: stored XSS — post body is rendered as raw HTML via v-html.
         A post body containing <img src=x onerror=...> executes for every reader. -->
    <div v-html="post.body"></div>
    <h3>Comments</h3>
    <div v-for="c in comments" :key="c.id" style="border-top:1px solid #eee;padding:8px 0;">
      <strong>{{ c.username }}:</strong>
      <!-- VULN: stored XSS on comments too -->
      <span v-html="c.body"></span>
    </div>
    <form @submit.prevent="addComment">
      <textarea v-model="newComment" placeholder="Write a comment (HTML allowed!)"></textarea>
      <button type="submit">Comment</button>
    </form>
  </div>
</template>

<script>
import { api } from "../api";
export default {
  data() { return { post: null, comments: [], newComment: "" }; },
  async mounted() {
    const id = this.$route.params.id;
    this.post = await api(`/posts/${id}`);
    this.comments = await api(`/comments/${id}`);
  },
  methods: {
    async addComment() {
      const id = this.$route.params.id;
      await api(`/comments/${id}`, { method: "POST", body: JSON.stringify({ body: this.newComment }) });
      this.newComment = "";
      this.comments = await api(`/comments/${id}`);
    }
  }
};
</script>
