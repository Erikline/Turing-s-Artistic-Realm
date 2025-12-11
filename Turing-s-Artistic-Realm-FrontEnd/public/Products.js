import * as THREE from "/build/three.module.js";
import vertexShader from "./shaders/galaxyVertex.js";
import fragmentShader from "./shaders/galaxyFragment.js";
import gsap from "/gsap/all.js";

//loading page
const loading = document.querySelector("#loading");

// loading persentage
const loadingPersentage = document.querySelector("#loading-persentage");
const fadeOutDuration = 1; //in seconds

// hide loading page
window.addEventListener("load", () => {
  gsap.to(loading, { opacity: 0, duration: fadeOutDuration });
  setTimeout(() => {
    loading.style.display = "none";
  }, fadeOutDuration * 1000);
});

// canvas
const canvas = document.querySelector(".tech-webgl");

// sizes
const sizes = {
  width: window.innerWidth,
  height: window.innerHeight,
};

// scene
const scene = new THREE.Scene();

/**
 * Galaxy
 */
const parameters = {};
parameters.count = 200000;
parameters.radius = 7;
parameters.branches = 3;
parameters.spin = 1;
parameters.randomness = 0.5;
parameters.randomnessPower = 3;
parameters.insideColor = "#ff6030";
parameters.outsideColor = "#1b3984";

let geometry = null;
let material = null;
let points = null;

const generateGalaxy = () => {
  if (points !== null) {
    geometry.dispose();
    material.dispose();
    scene.remove(points);
  }

  /**
   * Geometry
   */
  geometry = new THREE.BufferGeometry();

  const positions = new Float32Array(parameters.count * 3);
  const colors = new Float32Array(parameters.count * 3);
  const scales = new Float32Array(parameters.count * 1);
  const randomness = new Float32Array(parameters.count * 3);

  const insideColor = new THREE.Color(parameters.insideColor);
  const outsideColor = new THREE.Color(parameters.outsideColor);

  for (let i = 0; i < parameters.count; i++) {
    const i3 = i * 3;

    // Position
    const radius = Math.random() * parameters.radius;

    const branchAngle =
      ((i % parameters.branches) / parameters.branches) * Math.PI * 2;

    const randomX =
      Math.pow(Math.random(), parameters.randomnessPower) *
      (Math.random() < 0.5 ? 1 : -1) *
      parameters.randomness *
      radius;
    const randomY =
      Math.pow(Math.random(), parameters.randomnessPower) *
      (Math.random() < 0.5 ? 1 : -1) *
      parameters.randomness *
      radius;
    const randomZ =
      Math.pow(Math.random(), parameters.randomnessPower) *
      (Math.random() < 0.5 ? 1 : -1) *
      parameters.randomness *
      radius;

    positions[i3] = Math.cos(branchAngle) * radius;
    positions[i3 + 1] = 0;
    positions[i3 + 2] = Math.sin(branchAngle) * radius;

    randomness[i3] = randomX;
    randomness[i3 + 1] = randomY;
    randomness[i3 + 2] = randomZ;

    // Color
    const mixedColor = insideColor.clone();
    mixedColor.lerp(outsideColor, radius / parameters.radius);

    colors[i3] = mixedColor.r;
    colors[i3 + 1] = mixedColor.g;
    colors[i3 + 2] = mixedColor.b;

    // Scale
    scales[i] = Math.random();
  }

  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  geometry.setAttribute("aScale", new THREE.BufferAttribute(scales, 1));
  geometry.setAttribute(
    "aRandomness",
    new THREE.BufferAttribute(randomness, 3)
  );

  /**
   * Material
   */
  material = new THREE.ShaderMaterial({
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    vertexColors: true,
    vertexShader: vertexShader,
    fragmentShader: fragmentShader,
    uniforms: {
      uTime: { value: 0.0 },
      uSize: { value: 30.0 * renderer.getPixelRatio() },
    },
  });

  /**
   * Points
   */
  points = new THREE.Points(geometry, material);
  scene.add(points);
};

window.addEventListener("resize", () => {
  // Update sizes
  sizes.width = window.innerWidth;
  sizes.height = window.innerHeight;

  // Update camera
  camera.aspect = sizes.width / sizes.height;
  camera.updateProjectionMatrix();

  // Update renderer
  renderer.setSize(sizes.width, sizes.height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});

/**
 * Camera
 */
// Base camera
const camera = new THREE.PerspectiveCamera(
  75,
  sizes.width / sizes.height,
  0.1,
  100
);
// camera.position.x = 5;
camera.position.y = -2;
camera.position.z = 5;
camera.lookAt(0, 0, 0);
scene.add(camera);

/**
 * Renderer
 */
const renderer = new THREE.WebGLRenderer({
  canvas: canvas,
});
renderer.setSize(sizes.width, sizes.height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

/**
 * Generate Galaxy
 */
generateGalaxy();

/**
 * Animate
 */
const clock = new THREE.Clock();

const tick = () => {
  const elapsedTime = clock.getElapsedTime();

  // Update material
  material.uniforms.uTime.value = elapsedTime;

  // Render
  renderer.render(scene, camera);

  // Call tick again on the next frame
  window.requestAnimationFrame(tick);
};

tick();

// chat.js
document.addEventListener('DOMContentLoaded', () => {
    const modelSelect = document.getElementById('modelSelect');
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const fileInput = document.getElementById('fileInput');
    const chatMessages = document.getElementById('chat-messages');
    const modelContainer = document.getElementById('model-container');
    const uploadedImagePreview = document.getElementById('uploaded-image-preview');
    const imageContainer = document.getElementById('image-container');

    if (!modelSelect || !chatInput || !sendButton || !fileInput || !chatMessages || !modelContainer || !uploadedImagePreview || !imageContainer) {
        console.error('One or more required DOM elements are missing.');
        return;
    }

    sendButton.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });

    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        imageContainer.innerHTML = ''; // 清空之前的图片
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const imgWrapper = document.createElement('div');
                    imgWrapper.classList.add('image-wrapper');

                    const img = document.createElement('img');
                    img.src = event.target.result;
                    img.alt = `Uploaded Image ${i + 1}`;
                    imgWrapper.appendChild(img);

                    const deleteButton = document.createElement('button');
                    deleteButton.classList.add('delete-button');
                    deleteButton.innerHTML = '&times;';
                    deleteButton.addEventListener('click', () => {
                        imgWrapper.remove();
                    });
                    imgWrapper.appendChild(deleteButton);

                    imageContainer.appendChild(imgWrapper);
                };
                reader.readAsDataURL(file);
            }
        }
        uploadedImagePreview.style.display = 'flex';
    });

    function handleSendMessage() {
        const message = chatInput.value.trim();
        const selectedModel = modelSelect.value;
        const files = fileInput.files;

        if (message || files.length > 0) {
            let content = message || '';
            if (files.length > 0) {
                content += `<br>上传了文件: ${Array.from(files).map(file => file.name).join(', ')}`;
                Array.from(files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        const img = document.createElement('img');
                        img.src = event.target.result;
                        img.alt = `Uploaded Image`;
                        img.style.maxWidth = '100px';
                        img.style.maxHeight = '100px';
                        img.style.borderRadius = '5px';
                        img.style.objectFit = 'cover';
                        content += `<br>${img.outerHTML}`;
                        addMessageToChat('user', content);
                    };
                    reader.readAsDataURL(file);
                });
            } else {
                addMessageToChat('user', content);
            }

            sendToBackend(selectedModel, message, files);
            chatInput.value = '';
            fileInput.value = '';
            uploadedImagePreview.style.display = 'none';
            imageContainer.innerHTML = '';
        } else {
            addMessageToChat('system', `<p style="color: red;">请输入内容或选择文件！</p>`);
        }
    }

    function addMessageToChat(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', sender);
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${content}`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function sendToBackend(model, text, files) {
        const formData = new FormData();
        if (text) formData.append('text', text);
        for (let i = 0; i < files.length; i++) {
            formData.append('image', files[i]);
        }

        let endpoint = '';
        switch (model) {
            case 'T2I': endpoint = 'http://127.0.0.1:5000/text_to_image'; break;
            case 'I2I': endpoint = 'http://127.0.0.1:5000/text_image_to_image'; break;
            case 'I23D': endpoint = 'http://127.0.0.1:5000/image_to_3d'; break;
            case 'I2V': endpoint = 'http://127.0.0.1:5000/image_to_video'; break;
        }

        fetch(endpoint, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.model_url) {
                const cssConfig = data.css_config || {};
                const modelMessage = `
                    <model-viewer
                        src="${data.model_url}"
                        ar ar-modes="webxr scene-viewer quick-look"
                        environment-image="neutral" auto-rotate camera-controls
                        style="
                            width: ${cssConfig.width || '300px'} !important;
                            height: ${cssConfig.height || '400px'} !important;
                            background: transparent !important;
                            border-radius: ${cssConfig.border_radius || '8px'} !important;
                            --poster-color: transparent !important;
                            --progress-bar-color: hsl(var(--clr-white)) !important;
                            --progress-mask: transparent !important;
                            display: block !important;
                            margin: 0 auto !important;">
                    </model-viewer>
                `;
                addMessageToChat('model', modelMessage);
                modelContainer.style.display = 'block';
            } else if (data.image_url) {
                addMessageToChat('model', `<img src="${data.image_url}" alt="Generated Image" style="max-width: 100%; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px;">`);
            } else if (data.generation_id) {
                const interval = setInterval(() => {
                    fetch(`http://127.0.0.1:5000/get_video/${data.generation_id}`)
                    .then(response => response.json())
                    .then(videoData => {
                        if (videoData.video_url) {
                            clearInterval(interval);
                            addMessageToChat('model', `
                                <video controls style="max-width: 100%; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px;">
                                    <source src="${videoData.video_url}" type="video/mp4">
                                    Your browser does not support the video tag.
                                </video>
                            `);
                        } else if (videoData.message) {
                            addMessageToChat('model', `<p>${videoData.message}</p>`);
                        }
                    });
                }, 10000); // 轮询间隔
            } else if (data.error) {
                addMessageToChat('model', `<p style="color: red;">Error: ${data.error}</p>`);
            } else {
                addMessageToChat('model', `<p style="color: red;">发生未知错误，请稍后重试。</p>`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat('model', `<p style="color: red;">服务器错误，请稍后再试！</p>`);
        });
    }
});
