import pandas as pd
import json
import os

def clean_response(response):
    """清理response中的所有空格"""
    return json.loads(json.dumps(response).replace(" ", ""))

def process_files(assessor_folder, changed_id_file, data_file, output_folder):
    """处理评估者数据，并合并到原始数据集"""
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 读取 changed ID 数据
    with open(changed_id_file, 'r', encoding='utf-8') as f:
        changed_id_list = json.load(f)
    changed_id_df = pd.DataFrame({'ID': range(len(changed_id_list)), 'LEEC_ID': changed_id_list})
    
    # 读取数据集
    data_df = pd.read_excel(data_file)
    data_df.rename(columns={'ID': 'LEEC_ID'}, inplace=True)
    
    # 处理 assessor 文件夹中的所有 JSON 文件
    for file_name in os.listdir(assessor_folder):
        if file_name.endswith('.json'):
            file_path = os.path.join(assessor_folder, file_name)
            
            # 读取 JSON 数据
            with open(file_path, 'r', encoding='utf-8') as f:
                assessor_df = pd.DataFrame(json.load(f))
                
            # 清理 response 列
            assessor_df['response'] = assessor_df['response'].apply(clean_response)
            
            # 拆分 response 列
            if 'response' in assessor_df.columns:
                response_expanded = assessor_df['response'].apply(pd.Series)
                response_expanded = response_expanded.add_prefix('llm_')
                assessor_df = pd.concat([assessor_df.drop(columns=['response']), response_expanded], axis=1)
            
            # 合并数据集
            merged_df = assessor_df.merge(changed_id_df, on='ID', how='left').merge(data_df, on='LEEC_ID', how='left')
            
            # 删除空的 llm 列
            llm_columns = [col for col in merged_df.columns if col.startswith('llm_')]
            empty_llm_columns = [col for col in llm_columns if merged_df[col].isna().all() or merged_df[col].astype(str).str.strip().eq('').all()]
            
            if empty_llm_columns:
                print(f"\n删除的空列: {empty_llm_columns}")
                merged_df = merged_df.drop(columns=empty_llm_columns)
            
            # 保存合并后的数据
            output_path = os.path.join(output_folder, f"merged_{os.path.splitext(file_name)[0]}.xlsx")
            merged_df.to_excel(output_path, index=False)
            print(f"保存文件: {output_path}")
