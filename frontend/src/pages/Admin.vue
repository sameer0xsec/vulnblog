<template>
  <h2>Admin: Users</h2>
  <table>
    <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th><th>Password hash</th><th>Reset token</th></tr></thead>
    <tbody>
      <tr v-for="u in users" :key="u.id">
        <td>{{ u.id }}</td><td>{{ u.username }}</td><td>{{ u.email }}</td>
        <td>{{ u.role }}</td><td>{{ u.password }}</td><td>{{ u.reset_token }}</td>
      </tr>
    </tbody>
  </table>
  <p style="font-size:12px;color:#888;">
    This page is only "protected" by the nav link being hidden — the Vue route
    itself does no auth check, and PATCH /api/admin/users/:id on the backend
    only requires login, not admin (see VULNERABILITIES.md).
  </p>
</template>

<script>
import { api } from "../api";
export default {
  data() { return { users: [] }; },
  async mounted() { this.users = await api("/admin/users"); }
};
</script>
