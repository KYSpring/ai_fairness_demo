import pandas as pd
import json
import os
import re
import ast


# ==============================================================================
# 1. 我们从 json_trans.py 中“借用”并整合了强大的清理函数
#    现在这个脚本是完全自包含的，不再需要 from json_trans import ...
# ==============================================================================

def clean_response(response_str, file_name="unknown", index=0):
    """
    一个强大的清理函数，用于将 LLM 返回的“脏”JSON 字符串转换为干净的 Python 字典。
    """
    if not isinstance(response_str, str):
        return response_str  # 如果已经是字典或其他类型，直接返回

    if response_str == "PROHIBITED_CONTENT" or not response_str.strip() or response_str.strip() == "```":
        return None

    try:
        # 核心逻辑：尝试从字符串中用正则表达式提取出被 {} 包裹的部分
        match = re.search(r'\{.*\}', response_str, re.DOTALL)
        if not match:
            return None  # 如果找不到 {}，说明不是有效的 JSON

        json_part = match.group(0)

        # 将提取出的部分解析为字典
        parsed_dict = json.loads(json_part)

        if isinstance(parsed_dict, list):
            return parsed_dict[0] if parsed_dict else None
        return parsed_dict

    except json.JSONDecodeError:
        # print(f"警告: clean_response 无法解析 JSON: {response_str}") # 可在需要时取消注释
        return None


def extract_sentence(data_cell):
    """
    一个健壮的函数，用于从 true_answer 列中提取“刑期”。
    它能处理已经是字典的情况，也能处理需要解析的字符串。
    """
    if isinstance(data_cell, dict):
        return data_cell.get('刑期', None)

    if isinstance(data_cell, str) and data_cell.strip() and "Error occured" not in data_cell:
        try:
            s = data_cell.replace('‘', "'").replace('’', "'")
            s = s.replace('“', '"').replace('”', '"')
            s = s.replace('：', ':')
            answer_dict = ast.literal_eval(s)
            if isinstance(answer_dict, dict):
                return answer_dict.get('刑期', None)
        except (ValueError, SyntaxError):
            return None
    return None


# ==============================================================================
# 2. 这是您提供的原始 process_files 函数，我们只在其中进行了必要的“升级”
# ==============================================================================

def process_files(input_folder, changed_id_file, data_file, output_folder):
    """处理文件夹内所有 JSON 文件，并合并到原始数据集（最终升级版）"""
    os.makedirs(output_folder, exist_ok=True)

    with open(changed_id_file, 'r', encoding='utf-8') as f:
        changed_id_list = json.load(f)
    changed_id_df = pd.DataFrame({'ID': range(len(changed_id_list)), 'LEEC_ID': changed_id_list})

    data_df = pd.read_excel(data_file)
    data_df.rename(columns={'ID': 'LEEC_ID'}, inplace=True)

    # 在合并前，预先删除 data_df 中可能存在的冲突列
    if 'true_answer' in data_df.columns:
        data_df = data_df.drop(columns=['true_answer'])
    if 'response' in data_df.columns:
        data_df = data_df.drop(columns=['response'])

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.json'):
            file_path = os.path.join(input_folder, file_name)

            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    # 【升级点 1】: 使用通用变量名 df_from_json
                    df_from_json = pd.DataFrame(json.load(f))
                except (json.JSONDecodeError, ValueError):
                    print(f"警告: 文件 {file_name} 是空的或格式错误，跳过。")
                    continue

            # 【升级点 2】: 使用更强大的逻辑来处理 response 列
            if 'response' in df_from_json.columns:
                # 从列表中提取字符串，然后应用我们强大的 clean_response 函数
                cleaned_series = df_from_json['response'].str[0].apply(
                    lambda x: clean_response(x, file_name)
                ).dropna()

                if not cleaned_series.empty:
                    # 使用 apply(pd.Series) 展开，与原始脚本结构保持一致
                    response_expanded = cleaned_series.apply(pd.Series)
                    response_expanded = response_expanded.add_prefix('llm_')

                    df_from_json = df_from_json.drop(columns=['response'])
                    df_from_json = pd.concat([df_from_json.loc[response_expanded.index], response_expanded], axis=1)

            # 合并数据集 (变量名已统一为 df_from_json)
            merged_df = df_from_json.merge(changed_id_df, on='ID', how='left').merge(data_df, on='LEEC_ID', how='left')

            # 【升级点 3】: 加入 true_answer 解析逻辑
            if 'true_answer' in merged_df.columns:
                print(f"[*] 正在从 '{file_name}' 的 'true_answer' 列提取真实刑期...")
                merged_df['real_sentence'] = merged_df['true_answer'].apply(extract_sentence)
                success_count = merged_df['real_sentence'].notna().sum()
                total_count = merged_df['true_answer'].notna().sum()
                print(f"[*] 刑期提取完成！成功提取 {success_count} / {total_count} 条记录。")

            # 删除空的 llm 列 (逻辑与原始脚本保持一致)
            llm_columns = [col for col in merged_df.columns if col.startswith('llm_')]
            if llm_columns:
                empty_llm_columns = [col for col in llm_columns if merged_df[col].isna().all() or (
                            merged_df[col].astype(str).str.strip() == '').all()]
                if empty_llm_columns:
                    print(f"\n删除的空列: {empty_llm_columns}")
                    merged_df = merged_df.drop(columns=empty_llm_columns)

            # 保存合并后的数据
            output_path = os.path.join(output_folder, f"merged_{os.path.splitext(file_name)[0]}.xlsx")
            merged_df.to_excel(output_path, index=False)
            print(f"保存文件: {output_path}")


# ==============================================================================
# 3. 添加一个独立的测试启动器，与您的主逻辑完全分离
# ==============================================================================

"""if __name__ == '__main__':
    print("--- 正在以独立模式运行 data_process_leec_bias.py 进行测试 ---")

    input_json_folder = r"F:\Pycharm Projects\FarinessLegal\LLM-Fairness-main\LLM-Fairness-main\results\t0\deepseek_r1_32b_t0\output_for_experiment_t0"
    helpers_base_dir = r'F:\Pycharm Projects\ai_fairness_demo-main\ai_fairness_be\stata\stata\dataprocess'
    changed_id_path = os.path.join(helpers_base_dir, 'changedID_触发词版ID_list.json')
    data_file_path = os.path.join(helpers_base_dir, '有触发词数据集.xlsx')
    output_merged_folder = r'F:\Pycharm Projects\ai_fairness_demo-main\deepseek_r1_32b_t0\merged'

    if not os.path.exists(input_json_folder):
        print(f"!!! 错误: 输入文件夹不存在! {input_json_folder}")
    else:
        print("\n[*] 所有路径检查通过，开始调用 process_files 函数...")
        process_files(
            input_folder=input_json_folder,
            changed_id_file=changed_id_path,
            data_file=data_file_path,
            output_folder=output_merged_folder
        )
        print("\n--- 测试运行结束 ---")"""