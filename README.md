# Turing-s-Artistic-Realm 🎨

欢迎来到图灵的艺术领域！本项目使用 Three.js 库实现优质的交互界面，并接入生成式AI大模型实现文生图、文+图生图、图生3D的功能。

后端是一个简单的 Node.js/Express 服务器，主要负责托管前端静态资源。

## 🚀 快速开始

按照以下步骤在本地运行项目并查看粒子模拟效果。

### 环境要求

*   已安装 [Node.js](https://nodejs.org/) (推荐 LTS 版本) 和 npm。
*   已安装 [Git](https://git-scm.com/) (用于克隆仓库)。

### 安装与设置

1.  **克隆仓库：**
    ```bash
    git clone https://github.com/Erikline/Turing-s-Artistic-Realm.git
    cd Turing-s-Artistic-Realm
    ```

2.  **安装依赖项：**
    在项目目录中打开您的终端（例如 VS Code 集成终端）并运行：
    ```bash
    npm install
    ```
    此命令会根据 `package.json` 文件安装必要的依赖包（主要是用于服务器的 `Express`）。

### 运行项目

1.  **启动服务器：**
    在同一个终端中，运行：
    ```bash
    npm start
    ```
    这将执行 `package.json` 中定义的 `node server.js` 命令。

2.  **确认服务器正在运行：**
    您应该会在终端看到以下消息：
    ```
    server is running on port 3000
    ```

3.  **在浏览器中查看：**
    打开您的网页浏览器并访问：
    [http://localhost:3000](http://localhost:3000)

    您现在应该能看到 p5.js 画布正在渲染粒子模拟效果。

## 🛠️ 技术栈

*   **前端:** HTML, CSS, JavaScript
*   **创意编码库:** Three.js
*   **后端:** Node.js
*   **Web 服务器:** Express.js (用于托管静态文件)
*   **包管理器:** npm

## 🤝 贡献

欢迎提交贡献、问题 (Issues) 和功能请求！请随时查看 [问题页面](https://github.com/Erikline/Turing-s-Artistic-Realm/issues)。

## 📄 许可证 (License)

本项目根据 **[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)** 条款进行许可。

## ✨ 效果展示 / Screenshots
![](https://raw.githubusercontent.com/Erikline/Turing-s-Artistic-Realm/main/%E9%A6%96%E9%A1%B5.png)
![](https://raw.githubusercontent.com/Erikline/Turing-s-Artistic-Realm/main/%E4%BA%BA%E6%9C%BA%E4%BA%A4%E4%BA%92%E9%A1%B5.png)

