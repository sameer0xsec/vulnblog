<template>
  <h2>Login</h2>
  <form @submit.prevent="submit">
    <input v-model="username" placeholder="username" />
    <input v-model="password" type="password" placeholder="password" />
    <button type="submit">Login</button>
  </form>
  <p>{{ msg }}</p>
  <p style="font-size:12px;color:#888;">Try username <code>admin' -- </code> with any password.</p>
</template>

<script>
import { api } from "../api";
export default {
  data() { return { username: "", password: "", msg: "" }; },
  methods: {
    async submit() {
      const data = await api("/auth/login", { method: "POST", body: JSON.stringify({ username: this.username, password: this.password }) });
      if (data.token) {
        localStorage.setItem("token", data.token);
        this.msg = "Logged in as " + data.user.username;
      } else {
        this.msg = data.error || "Login failed";
      }
    }
  }
};
</script>
