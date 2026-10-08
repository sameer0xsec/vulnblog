<template>
  <nav style="display:flex;gap:16px;padding:16px;border-bottom:1px solid #ddd;">
    <router-link to="/">VulnBlog</router-link>
    <router-link to="/search">Search</router-link>
    <router-link to="/profile">Profile</router-link>
    <router-link v-if="role === 'admin'" to="/admin">Admin</router-link>
    <router-link to="/login">Login</router-link>
    <router-link to="/register">Register</router-link>
  </nav>
  <div style="max-width:900px;margin:0 auto;padding:16px;">
    <router-view />
  </div>
</template>

<script>
export default {
  data() {
    // VULN: admin link visibility is decided purely client-side by decoding
    // the JWT payload — not real access control, just UI sugar (see backend
    // where several admin routes forget to enforce it server-side too).
    let role = "user";
    try {
      const token = localStorage.getItem("token");
      if (token) role = JSON.parse(atob(token.split(".")[1])).role;
    } catch {}
    return { role };
  }
};
</script>
