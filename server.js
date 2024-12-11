const express = require("express");
const path = require("path");

const app = express();

// 提供 public 文件夹中的静态文件
app.use(express.static("public"));

// 提供 Three.js 的构建文件
app.use("/build/", express.static(path.join(__dirname, "node_modules/three/build")));

// 提供 Three.js 的示例模块
app.use("/jsm/", express.static(path.join(__dirname, "node_modules/three/examples/jsm")));

// 提供 GSAP 的静态文件
app.use("/gsap/", express.static(path.join(__dirname, "node_modules/gsap")));

// 启动服务器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`server is running on port ${PORT}`);
});
