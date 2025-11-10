import os
import sys
import threading
import subprocess
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from pathlib import Path

# --- 1. 初始化 Flask 和 CORS ---
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

# --- 2. 动态添加所有必要的脚本路径 ---
# 这是解决 "No module named" 问题的核心
script_dir = os.path.dirname(os.path.abspath(__file__))
script_dir_path = Path(script_dir)
# 添加 stata_final.py, json_trans.py, data_process_leec_bias.py 所在的目录
stata_dataprocess_path = os.path.join(script_dir, 'stata', 'stata', 'dataprocess')
# 添加 API.py 所在的目录
api_call_path = os.path.join(script_dir, 'stata', 'stata', 'API调用')

sys.path.append(stata_dataprocess_path)
sys.path.append(api_call_path)

try:
    # --- 3. 导入本地脚本 ---
    # 现在 Python 知道去哪里找它们了
    from API import modify_and_run as run_api_experiment
    from stata_final import main as run_stata_analysis
except ImportError as e:
    print(f"!!! 严重错误: 无法导入必要的模块: {e}")
    print(f"请确保以下路径在 sys.path 中:")
    print(f"- {stata_dataprocess_path}")
    print(f"- {api_call_path}")
    sys.exit(1)

# --- 4. 定义容器内部的固定路径 ---
APP_ROOT = script_dir_path
STATA_ROOT = script_dir_path
# 修正 API 模板文件的路径，指向它在子目录中的真实位置
API_TEMPLATE_PATH = STATA_ROOT / 'stata'/ 'stata' / 'API调用' /'DeepSeek_R1_Example.py'
RAW_JSON_OUTPUT_DIR = APP_ROOT / 'raw_output_data'
ANALYSIS_RESULTS_DIR = APP_ROOT / 'analysis_results'


def run_full_analysis_in_background(model_config):
    """
    这个函数将在一个单独的线程中被调用，
    它按顺序执行“阶段一”和“阶段二”。
    """
    try:
        model_name = model_config.get("MODEL_NAME", "default_model")
        logging.info(f"--- [后台线程] 启动：开始为模型 {model_name} 执行完整分析 ---")

        # --- 阶段一: 运行 API 实验以生成数据 ---
        logging.info(f"--- [阶段一] 正在调用 LLM API 生成原始 JSON... ---")

        api_config = {
            "OPENROUTER_API_KEY": model_config.get("OPENROUTER_API_KEY"),
            "MODEL_NAME": model_config.get("MODEL_NAME"),
            "API_URL": model_config.get("API_URL"),
            "providers": model_config.get("providers", ["Azure", "Chutes"]),
            "temperature": model_config.get("temperature", 0.0),
            "output_dir": (RAW_JSON_OUTPUT_DIR / model_name).as_posix()
        }

        os.makedirs(api_config["output_dir"], exist_ok=True)

        if not API_TEMPLATE_PATH.exists():
            logging.error(f"!!! [后台线程] 找不到 API 模板文件: {API_TEMPLATE_PATH}")
            raise FileNotFoundError(f"找不到 API 模板文件: {API_TEMPLATE_PATH}")

        run_api_experiment(str(API_TEMPLATE_PATH), api_config)

        logging.info(f"--- [阶段一] 原始 JSON 文件已生成至: {api_config['output_dir']} ---")

        # --- 阶段二: 运行 Stata 分析脚本 ---
        logging.info(f"--- [阶段二] 正在调用 Stata 分析已生成的 JSON 文件... ---")

        stata_path_base = ANALYSIS_RESULTS_DIR
        stata_model_name = model_name
        stata_input_dir = api_config["output_dir"]  # Stata 的输入 = 阶段一的输出

        os.makedirs(stata_path_base, exist_ok=True)

        # stata_final.py 脚本会自己找到它需要的 params.json 等文件
        # 我们不需要在这里指定 json_path
        run_stata_analysis(
            path_base=stata_path_base,
            model=stata_model_name,
            output_for_experiment_dir=stata_input_dir,
            params_list=["victim_sexual_orientation"]  # 示例：您可以让前端传递这个列表
        )

        logging.info(f"--- [阶段二] Stata 分析完成！结果保存在: {stata_path_base / stata_model_name} ---")
        logging.info(f"--- [后台线程] 任务 {model_name} 已全部完成 ---")

    except Exception as e:
        logging.error(f"!!! [后台线程] 任务 {model_name} 失败: {e}", exc_info=True)


@app.route('/api/run-analysis', methods=['POST','GET'])
def handle_analysis_request():
    """
    接收前端的分析请求，并启动一个后台线程来执行。
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体为空"}), 400

    model_config = {
        "OPENROUTER_API_KEY": data.get("api_key"),
        "MODEL_NAME": data.get("model_name"),
        "API_URL": data.get("api_url"),
        "providers": data.get("provider_name"),
        "temperature": data.get("temperature", 0.0)
    }

    if not model_config["OPENROUTER_API_KEY"] or not model_config["MODEL_NAME"] or not model_config["API_URL"]:
        return jsonify({"error": "缺少 'api_key', 'model_name' 或 'api_url' 参数"}), 400

    logging.info(f"[*] 收到 API 请求：准备在后台启动 {model_config['MODEL_NAME']} 的完整分析...")

    thread = threading.Thread(
        target=run_full_analysis_in_background,
        args=(model_config,)
    )
    thread.start()

    return jsonify({
        "message": f"分析任务已成功启动。请在后端 Docker 日志中查看进度。"
    }), 202


@app.route('/test', methods=['GET'])
def test_connection():
    """这是一个用于测试前后端连接的简单接口"""
    return jsonify({"message": "success"})


if __name__ == '__main__':
    if not os.getenv('STATA_PATH'):
        print("!!! 警告: 环境变量 STATA_PATH 未设置! Stata 调用可能会失败。")

    print(f"[*] Flask API 服务器正在启动，监听 0.0.0.0:5000 ...")
    app.run(debug=True, host='0.0.0.0', port=5000)