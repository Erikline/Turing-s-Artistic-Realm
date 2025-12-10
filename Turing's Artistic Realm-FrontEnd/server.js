const express = require("express");
const path = require("path");

const app = express();

// 提供 public 文件夹中的静态文件
app.use(express.static(path.join(__dirname, "public")));

// Three.js 静态资源
app.use("/build/", express.static(path.join(__dirname, "node_modules/three/build")));
app.use("/jsm/", express.static(path.join(__dirname, "node_modules/three/examples/jsm")));

// GSAP 静态资源
app.use("/gsap/", express.static(path.join(__dirname, "node_modules/gsap")));

// 根路径重定向
app.get("/", (req, res) => {
    res.redirect("/Home.html");
});

// 启动服务器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`server is running on port ${PORT}`);
});
