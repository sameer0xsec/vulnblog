<template>
  <h2>Profile</h2>
  <input type="file" @change="onFile" />
  <button @click="upload">Upload avatar</button>
  <p>{{ msg }}</p>
  <p style="font-size:12px;color:#888;">
    Try uploading an .html file, then open /uploads/yourfile.html directly.
  </p>
</template>

<script>
import { getToken } from "../api";
export default {
  data() { return { file: null, msg: "" }; },
  methods: {
    onFile(e) { this.file = e.target.files[0]; },
    async upload() {
      const fd = new FormData();
      fd.append("file", this.file);
      const res = await fetch("http://localhost:5000/api/upload/avatar", {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}` },
        body: fd
      });
      this.msg = JSON.stringify(await res.json());
    }
  }
};
</script>
