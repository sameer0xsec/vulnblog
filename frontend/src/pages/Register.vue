<template>
  <h2>Register</h2>
  <form @submit.prevent="submit">
    <input v-model="form.username" placeholder="username" />
    <input v-model="form.email" placeholder="email" />
    <input v-model="form.password" type="password" placeholder="password" />
    <input v-model="form.role" placeholder="role (try 'admin')" />
    <button type="submit">Register</button>
  </form>
  <p>{{ msg }}</p>
</template>

<script>
import { api } from "../api";
export default {
  data() { return { form: { username: "", email: "", password: "", role: "" }, msg: "" }; },
  methods: {
    async submit() {
      // VULN: "role" field passed straight through; see backend auth.py mass assignment.
      const data = await api("/auth/register", { method: "POST", body: JSON.stringify(this.form) });
      this.msg = JSON.stringify(data);
    }
  }
};
</script>
