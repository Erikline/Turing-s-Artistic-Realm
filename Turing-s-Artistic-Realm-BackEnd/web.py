import sys
from flask import Flask, request, jsonify, render_template_string,send_from_directory
import os
import json
import base64
import datetime
import hashlib
import hmac
import requests
import logging
import tempfile
from dotenv import load_dotenv
from PIL import Image, ImageOps
from io import BytesIO
import matplotlib.pyplot as plt
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'static/generated_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 加载 .env 文件中的变量
load_dotenv()

VOLCENGINE_ACCESS_KEY = os.getenv('VOLCENGINE_ACCESS_KEY')
VOLCENGINE_SECRET_KEY = os.getenv('VOLCENGINE_SECRET_KEY')
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')

# 配置日志
logging.basicConfig(level=logging.INFO)

# Volcengine API 配置
method = 'POST'
host = 'visual.volcengineapi.com'
region = 'cn-north-1'
endpoint = 'https://visual.volcengineapi.com'
service = 'cv'

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(key.encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'request')
    return kSigning

def formatQuery(parameters):
    request_parameters_init = ''
    for key in sorted(parameters):
        request_parameters_init += key + '=' + parameters[key] + '&'
    request_parameters = request_parameters_init[:-1]
    return request_parameters

def signV4Request(access_key, secret_key, service, req_query, req_body):
    if access_key is None or secret_key is None:
        print('No access key is available.')
        sys.exit()

    t = datetime.datetime.utcnow()
    current_date = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope
    canonical_uri = '/'
    canonical_querystring = req_query
    signed_headers = 'content-type;host;x-content-sha256;x-date'
    payload_hash = hashlib.sha256(req_body.encode('utf-8')).hexdigest()
    content_type = 'application/json'
    canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + \
                        '\n' + 'x-content-sha256:' + payload_hash + \
                        '\n' + 'x-date:' + current_date + '\n'
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + \
                        '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    algorithm = 'HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'request'
    string_to_sign = algorithm + '\n' + current_date + '\n' + credential_scope + '\n' + hashlib.sha256(
        canonical_request.encode('utf-8')).hexdigest()
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode(
        'utf-8'), hashlib.sha256).hexdigest()

    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + \
                           credential_scope + ', ' + 'SignedHeaders=' + \
                           signed_headers + ', ' + 'Signature=' + signature
    headers = {'X-Date': current_date,
               'Authorization': authorization_header,
               'X-Content-Sha256': payload_hash,
               'Content-Type': content_type
               }

    request_url = endpoint + '?' + canonical_querystring

    print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
    print('Request URL = ' + request_url)
    try:
        r = requests.post(request_url, headers=headers, data=req_body)
    except Exception as err:
        print(f'error occurred: {err}')
        raise
    else:
        print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
        print(f'Response code: {r.status_code}\n')
        resp_str = r.text.replace("\\u0026", "&")
        print(f'Response body: {resp_str}\n')
        return r

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def display_image_from_response(resp_str):
    try:
        data = json.loads(resp_str)
        binary_data = data['data']['binary_data_base64']

        if binary_data:
            for img_data in binary_data:
                image_data = base64.b64decode(img_data)
                image = Image.open(BytesIO(image_data))
                plt.imshow(image)
                plt.axis('off')  # 关闭坐标轴
                plt.show()
        else:
            print("暂无可用的图片数据")
    except json.JSONDecodeError:
        print("解析 JSON 时发生错误，请确保 resp_str 是有效的 JSON 字符串。")
    except Exception as e:
        print(f"发生错误: {e}")

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI 图像和视频生成</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 { color: #333; }
            form {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                padding: 20px;
                margin-bottom: 20px;
            }
            label { display: block; margin-bottom: 10px; }
            input[type="file"], input[type="text"] {
                width: 100%; padding: 5px; margin-bottom: 10px;
            }
            input[type="submit"] {
                background-color: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer;
            }
            input[type="submit"]:hover { background-color: #45a049; }
            video, img { max-width: 100%; margin-top: 20px; }
            model-viewer { width: 100%; margin-top: 20px; }
        </style>
        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    </head>
    <body>
        <h1>AI 图像和视频生成</h1>

        <form id="text-to-image-form">
            <h2>文本生成图片</h2>
            <label for="text">输入文本：</label>
            <input type="text" name="text" required>
            <input type="submit" value="生成图片">
        </form>
        <div id="text-image-result"></div>

        <form id="text-image-to-image-form" enctype="multipart/form-data">
            <h2>文本+图片生成图片</h2>
            <label for="text">输入文本：</label>
            <input type="text" name="text" required>
            <label for="image">选择图片：</label>
            <input type="file" name="image" accept="image/*" required>
            <input type="submit" value="生成图片">
        </form>
        <div id="text-image-result1"></div>

        <form id="image-to-3d-form" enctype="multipart/form-data">
            <h2>图片生成3D模型</h2>
            <label for="image">选择图片：</label>
            <input type="file" name="image" accept="image/*" required>
            <input type="submit" value="生成3D模型">
        </form>
        <div id="3d-result"></div>

        <form id="image-to-video-form" enctype="multipart/form-data">
            <h2>图片生成视频</h2>
            <label for="image">选择图片：</label>
            <input type="file" name="image" accept="image/*" required>
            <input type="submit" value="生成视频">
        </form>
        <div id="image-video-result"></div>

        <script>
            // 文本生成图片
            document.getElementById('text-to-image-form').addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(this);
                fetch('/text_to_image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    let resultHtml = '';
                    if (data.image_base64) {
                        resultHtml += `<img src="data:image/png;base64,${data.image_base64}" alt="Generated Image">`;
                    }
                    if (data.pe_result) {
                        resultHtml += `<p>${data.pe_result}</p>`;
                    }
                    if (data.error) {
                        resultHtml += `<p>${data.error}</p>`;
                    }
                    document.getElementById('text-image-result').innerHTML = resultHtml;
                })
                .catch(error => console.error('Error:', error));
            });

            // 文本+图片生成图片
            document.getElementById('text-image-to-image-form').addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(this);
                fetch('/text_image_to_image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    let resultHtml = '';
                    if (data.image_base64) {
                        resultHtml += `<img src="data:image/png;base64,${data.image_base64}" alt="Generated Image">`;
                    }
                    if (data.pe_result) {
                        resultHtml += `<p>${data.pe_result}</p>`;
                    }
                    if (data.vlm_result) {
                        resultHtml += `<p>${data.vlm_result}</p>`;
                    }
                    if (data.error) {
                        resultHtml += `<p>${data.error}</p>`;
                    }
                    document.getElementById('text-image-result1').innerHTML = resultHtml;
                })
                .catch(error => console.error('Error:', error));
            });

            // 图片生成3D模型
            document.getElementById('image-to-3d-form').addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(this);
                fetch('/image_to_3d', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.model_url) {
                        document.getElementById('3d-result').innerHTML = `
                            <model-viewer src="${data.model_url}" ar ar-modes="webxr scene-viewer quick-look" environment-image="neutral" auto-rotate camera-controls></model-viewer>`;
                    } else {
                        document.getElementById('3d-result').innerHTML = `<p>${data.error}</p>`;
                    }
                })
                .catch(error => console.error('Error:', error));
            });

            // 图片生成视频
            document.getElementById('image-to-video-form').addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(this);
                fetch('/image_to_video', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.generation_id) {
                        const interval = setInterval(() => {
                            fetch(`/get_video/${data.generation_id}`)
                            .then(response => response.json())
                            .then(videoData => {
                                if (videoData.video_url) {
                                    clearInterval(interval);
                                    document.getElementById('image-video-result').innerHTML = `
                                        <video controls>
                                            <source src="${videoData.video_url}" type="video/mp4">
                                            Your browser does not support the video tag.
                                        </video>`;
                                } else {
                                    document.getElementById('image-video-result').innerHTML = `<p>${videoData.message}</p>`;
                                }
                            });
                        }, 10000); // 轮询间隔
                    } else {
                        document.getElementById('image-video-result').innerHTML = `<p>${data.error}</p>`;
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/text_to_image', methods=['POST'])
def text_to_image():
    text = request.form.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # 调用实际的 API 获取生成的 Base64 图片数据
        query_params = {
            'Action': 'CVProcess',
            'Version': '2022-08-31',
        }
        formatted_query = formatQuery(query_params)

        body_params = {
            "req_key": "high_aes_general_v20_L",
            "prompt": text
        }
        formatted_body = json.dumps(body_params)

        # 调用签名后的请求
        resp = signV4Request(VOLCENGINE_ACCESS_KEY, VOLCENGINE_SECRET_KEY, service, formatted_query, formatted_body)
        if resp.status_code != 200:
            logging.error(f"API Error: {resp.status_code} - {resp.text}")
            return jsonify({"error": "API request failed", "details": resp.text}), resp.status_code

        # 从 API 响应中解析 Base64 图片数据
        response = resp.json()
        image_data = response.get('data', {}).get('binary_data_base64', [])
        if not image_data:
            return jsonify({"error": "No image generated"}), 500

        # 解码 Base64 数据并保存为图片
        decoded_image = base64.b64decode(image_data[0])
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename = f"generated_image_{timestamp}.png"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(file_path, "wb") as f:
            f.write(decoded_image)

        image_url = f"http://localhost:5000/static/generated_images/{filename}"
        return jsonify(
            {"image_url": image_url, "pe_result": response.get('data', {}).get('pe_result', 'AI 生成图片成功！')})


    except Exception as e:
        logging.error(f"Error in text_to_image: {str(e)}")
        return jsonify({"error": str(e)}), 500



@app.route('/text_image_to_image', methods=['POST'])
def text_image_to_image():
    """
    接收文本和图片，调用生成图像的 API，将生成的图片解码并保存为文件，然后返回图片的 URL。
    """
    text = request.form.get('text')
    if 'image' not in request.files or not text:
        return jsonify({"error": "文本或图片未提供"}), 400

    image_file = request.files['image']
    temp_dir = tempfile.gettempdir()
    image_path = os.path.join(temp_dir, image_file.filename)

    try:
        # 保存临时图片文件
        image_file.save(image_path)
        base64_image = image_to_base64(image_path)

        # 调用生成图像的 API
        query_params = {
            'Action': 'CVProcess',
            'Version': '2022-08-31',
        }
        formatted_query = formatQuery(query_params)

        body_params = {
            "req_key": "byteedit_v2.0",
            "binary_data_base64": [base64_image],
            "prompt": text,
            "scale": 0.7
        }
        formatted_body = json.dumps(body_params)

        # 调用签名后的请求
        resp = signV4Request(VOLCENGINE_ACCESS_KEY, VOLCENGINE_SECRET_KEY, service, formatted_query, formatted_body)
        response = resp.json()

        # 获取返回的图像数据
        image_base64 = response.get('data', {}).get('binary_data_base64', [])
        pe_result = response.get('data', {}).get('pe_result', '')

        if image_base64:
            # 解码 Base64 数据并保存为图片文件
            decoded_image = base64.b64decode(image_base64[0])
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
            filename = f"generated_image_{timestamp}.png"
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # 保存解码后的图片文件
            with open(file_path, "wb") as f:
                f.write(decoded_image)

            # 返回图片的 URL 和其他结果
            image_url = f"http://localhost:5000/static/generated_images/{filename}"
            return jsonify({
                "success": True,
                "image_url": image_url,  # 图片 URL
                "pe_result": pe_result,
                "message": "生成成功"
            })
        else:
            return jsonify({"error": "未生成图像，请检查输入"}), 500
    except Exception as e:
        logging.error(f"Error in text_image_to_image: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # 确保删除临时图片文件
        if os.path.exists(image_path):
            os.remove(image_path)

def image_to_base64(image_path):
    """
    将图片文件转换为 Base64 字符串。
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error converting image to base64: {str(e)}")
        raise


@app.route('/image_to_3d', methods=['POST'])
def image_to_3d():
    if 'image' not in request.files:
        logging.error(f"Request files: {request.files}")  # 打印请求中的文件信息
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']

    # 定义保存 3D 模型的目录路径 (static/models)
    model_dir = os.path.join("static", "models")
    os.makedirs(model_dir, exist_ok=True)  # 确保目录存在

    # 临时保存上传的图片
    temp_dir = tempfile.gettempdir()
    image_path = os.path.join(temp_dir, image_file.filename)

    try:
        # 保存上传的图片
        image_file.save(image_path)

        # 调用 Stability AI 3D API
        with open(image_path, "rb") as img_file:
            response = requests.post(
                "https://api.stability.ai/v2beta/3d/stable-fast-3d",
                headers={"Authorization": f"Bearer {STABILITY_API_KEY}"},
                files={"image": img_file}
            )

        if response.status_code != 200:
            logging.error(f"Stability API Error: {response.json()}")
            return jsonify({"error": "Failed to generate 3D model", "details": response.json()}), response.status_code

        # 保存 API 返回的 3D 模型到 static/models 目录
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        model_filename = f"3d_model_{timestamp}.glb"
        model_path = os.path.join(model_dir, model_filename)

        with open(model_path, 'wb') as model_file:
            model_file.write(response.content)

        logging.info(f"3D model saved to {model_path}")  # 日志输出生成模型的位置

        # 返回模型下载的 URL 和 CSS 配置信息
        return jsonify({
            "message": "3D model generated successfully",
            "model_url": f"http://localhost:5000/static/models/{model_filename}"
        })

    except Exception as e:
        logging.error(f"Error in image_to_3d: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        # 删除临时保存的图片文件
        if os.path.exists(image_path):
            os.remove(image_path)


# 定义保存视频的目录
VIDEO_FOLDER = 'static/videos'
os.makedirs(VIDEO_FOLDER, exist_ok=True)

@app.route('/image_to_video', methods=['POST'])
def image_to_video():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    temp_path = f"./{image_file.filename}"
    resized_path = f"./resized_{image_file.filename}"

    try:
        # 保存上传的图片文件
        image_file.save(temp_path)

        # 使用 Pillow 调整图片尺寸
        from PIL import Image
        with Image.open(temp_path) as img:
            img = img.resize((768, 768), Image.LANCZOS)
            img.save(resized_path)

        # 调用 Stability AI Image-to-Video API
        with open(resized_path, "rb") as img_file:
            response = requests.post(
                "https://api.stability.ai/v2beta/image-to-video",
                headers={"Authorization": f"Bearer {STABILITY_API_KEY}"},
                files={"image": img_file},
                data={
                    "seed": 0,
                    "cfg_scale": 1.8,
                    "motion_bucket_id": 127
                },
            )

        # 检查 API 响应
        if response.status_code != 200:
            logging.error(f"API Error: {response.text}")
            return jsonify({"error": "Failed to generate video", "details": response.text}), response.status_code

        # 获取生成的 Generation ID
        json_response = response.json()
        generation_id = json_response.get('id')
        if not generation_id:
            return jsonify({"error": "No generation ID returned by API", "details": json_response}), 500

        # 返回生成 ID 给客户端
        return jsonify({"message": "Video generation in progress", "generation_id": generation_id})

    except Exception as e:
        logging.error(f"Error in image_to_video: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # 删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(resized_path):
            os.remove(resized_path)

@app.route('/get_video/<generation_id>', methods=['GET'])
def get_video(generation_id):
    try:
        # 调用 Stability AI 获取视频状态或结果
        response = requests.get(
            f"https://api.stability.ai/v2beta/image-to-video/result/{generation_id}",
            headers={
                'Authorization': f"Bearer {STABILITY_API_KEY}",
                'Accept': "video/*"  # Use 'application/json' if you expect JSON response
            },
        )

        if response.status_code == 202:
            return jsonify({"message": "Video generation in progress. Please try again later."})
        elif response.status_code == 200:
            # 保存视频文件
            video_path = f"./static/videos/{generation_id}.mp4"
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            with open(video_path, 'wb') as video_file:
                video_file.write(response.content)

            # 返回视频文件的 URL
            return jsonify({"message": "Video generation complete!", "video_url": f"http://localhost:5000/static/videos/{generation_id}.mp4"})
        else:
            logging.error(f"Error fetching video: {response.text}")
            return jsonify({"error": "Failed to fetch video", "details": response.text}), response.status_code

    except Exception as e:
        logging.error(f"Error in get_video: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/static/videos/<filename>', methods=['GET'])
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
