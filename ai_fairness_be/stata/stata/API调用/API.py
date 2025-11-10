import re
import subprocess
import os  # <-- 确保导入 os 模块


def modify_and_run(file_path, new_values):
    """
    修改 Python 文件中的指定变量值并执行文件。

    :param file_path: 需要修改的 Python 文件路径
    :param new_values: 字典，包含要修改的变量名及其新值
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换变量值
    for var, new_val in new_values.items():
        # 修正：确保 new_val 已经是字符串，再添加引号
        new_val_str = f'"{new_val}"' if isinstance(new_val, str) else str(new_val)

        # 修正：使用 f-string 或 str() 来正确处理非字符串值
        if isinstance(new_val, str):
            replacement_val = f'"{new_val}"'
        elif isinstance(new_val, list):
            replacement_val = f'{new_val}'  # 假设列表在代码中就是 [..., ...]
        else:
            replacement_val = str(new_val)

        pattern = rf"{var}\s*=\s*.*"
        # 使用修正后的 replacement_val
        replacement = f"{var} = {replacement_val}"
        content = re.sub(pattern, replacement, content)

    # 生成临时文件
    temp_file = file_path.replace('.py', '_modified.py')
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # 运行修改后的 Python 文件
    subprocess.run(['python', temp_file], check=True)


# --- 核心修改：将示例代码包裹起来 ---
if __name__ == "__main__":
    # 这段代码只会在你“直接运行 API.py”时执行
    # 当 run.py “导入 API.py”时，这段代码会被安全地跳过

    # --- 路径修正 ---
    # 动态获取当前脚本(API.py)所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 构建到 DeepSeek_R1_Example.py 的正确相对路径
    # (从 .../stata/stata/API调用/ 返回两级到 .../stata/)
    base_path = os.path.abspath(os.path.join(current_dir, '..', '..'))

    file_path = os.path.join(base_path, 'API调用', 'DeepSeek_R1_Example.py')
    output_dir_path = os.path.join(base_path, 'API调用', 'v3', 'output_for_experiment')

    print(f"[*] 正在使用模板文件: {file_path}")
    print(f"[*] 输出目录将设置为: {output_dir_path}")

    # 示例调用
    new_values = {
        "OPENROUTER_API_KEY": "yourAPI",
        "MODEL_NAME": "deepseek/deepseek-r1:free",
        "API_URL": "https://openrouter.ai/api/v1/chat/completions",
        "providers": ["Azure", "Chutes"],
        "output_dir": output_dir_path
    }
    modify_and_run(file_path, new_values)