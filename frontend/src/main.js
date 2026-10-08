import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import Login from "./pages/Login.vue";
import Register from "./pages/Register.vue";
import Posts from "./pages/Posts.vue";
import PostDetail from "./pages/PostDetail.vue";
import Search from "./pages/Search.vue";
import Profile from "./pages/Profile.vue";
import Admin from "./pages/Admin.vue";

const routes = [
  { path: "/", component: Posts },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  { path: "/posts/:id", component: PostDetail },
  { path: "/search", component: Search },
  { path: "/profile", component: Profile },
  { path: "/admin", component: Admin },
];

const router = createRouter({ history: createWebHistory(), routes });
createApp(App).use(router).mount("#app");
