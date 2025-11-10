import os
import glob
import json
import requests
import time
import logging
import sys

# =========== OpenRouter Configuration ===========
OPENROUTER_API_KEY = "121212112121"
MODEL_NAME = "google/gemini-pro"
API_URL = "http://localhost:5000/api/run-analysis"

# =========== Logging Configuration ===========
log_file = "logfile.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)


def extract_wait_seconds(response_json: dict) -> int:
    try:
        raw_message = response_json['error']['metadata']['raw']
        wait_message = raw_message['message']
        if 'Try again in' in wait_message:
            return int(wait_message.split(' ')[-2])
        return -1
    except Exception as e:
        logging.error(f"Error extracting wait seconds: {e}")
        return -1


def chat_round(messages: list[dict], max_new_tokens: int = 10000, temperature: float = 1.0) -> str:
    """
    Calls OpenRouter API with DeepSeek-V3 model and handles errors gracefully.
    If an error occurs, it prints the response, waits for 2 seconds, and retries.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    providers = "google"
    current_provider_idx = 0
    response_json = None

    while True:
        try:
            provider_name = providers[current_provider_idx]
            payload = {
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": temperature
            }

            logging.info(f"Sending API request to {provider_name}...")

            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()

            response_json = response.json()
            if 'choices' in response_json:
                logging.info(f"Response received successfully from {provider_name}.")
                return response_json['choices'][0]['message']['content'].strip()

            wait_seconds = extract_wait_seconds(response_json)
            if wait_seconds != -1:
                logging.warning(f"Rate limit hit. Retrying after {wait_seconds} seconds.")
                time.sleep(wait_seconds)
            else:
                logging.warning(f"Unknown error from {provider_name}, switching provider.")

            current_provider_idx = (current_provider_idx + 1) % len(providers)

        except Exception as e:
            logging.error(f"API Request failed: {e}")
            time.sleep(3)
            current_provider_idx = (current_provider_idx + 1) % len(providers)


def generate_predictions(dataset_path: str, donelength: int, batch_size: int = 10) -> list:
    """
    Reads the dataset and processes it in batches using the OpenRouter API.
    """
    ids, changed_labels, label_values, responses, true_answers = [], [], [], [], []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    true_answer_path = os.path.join(current_dir, "刑期_list.json")

    with open(true_answer_path, 'r', encoding='utf-8') as f:
        true_answer = json.load(f)
    with open(dataset_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    batch_data = test_data[donelength:min(donelength + batch_size, len(test_data))]

    logging.info(f"Processing {len(batch_data)} samples from {dataset_path}.")

    for idx, data in enumerate(batch_data):
        prompt = data['prompt']
        messages = [{"role": "user", "content": prompt}]

        response = chat_round(messages)

        ids.append(data['ID'])
        changed_labels.append(data['changed_label'])
        label_values.append(data['label_value'])
        true_answers.append(true_answer[data['ID']]["true_answer"])
        responses.append(response)

        logging.info(f"Processed ID {data['ID']} - Label: {data['changed_label']} - Response: {response}")

    return ids, changed_labels, label_values, responses, true_answers


def handle_one_label(dataset_path: str, output_path: str, lendone: int, batch_size: int = 10) -> int:
    with open(dataset_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    total = len(test_data)

    while lendone < total:
        ids, changed_labels, label_values, responses, true_answers = generate_predictions(dataset_path, lendone, batch_size)

        if lendone != 0 and os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []

        for i in range(len(responses)):
            item = {
                "ID": ids[i],
                "changed_label": changed_labels[i],
                "label_value": label_values[i],
                "response": responses[i],
                "true_answer": true_answers[i]
            }
            data.append(item)

        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(data, f_out, ensure_ascii=False, indent=4)

        lendone += len(responses)
        logging.info(f"Processed {lendone}/{total} entries for {dataset_path}.")

    logging.info(f"Finished processing {dataset_path}. Output saved to {output_path}.")
    return lendone


current_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = r'F:\Pycharm Projects\FarinessLegal\LLM-Fairness-main\LLM-Fairness-main\stata\API调用\v3\dateset_for_experiment'
output_dir = "F:/Pycharm Projects/ai_fairness_demo-main/ai_fairness_be/raw_output_data/google/gemini-pro"
os.makedirs(output_dir, exist_ok=True)
input_files = glob.glob(os.path.join(input_dir, '*_changed.json'))

start_file = os.path.join(input_dir, "victim_age_changed.json")

if start_file in input_files:
    print("kaishila")
    start_index = input_files.index(start_file) + 1
else:
    print("shayemei")
    start_index = 0

input_files = input_files[:start_index]  # 处理 start_index 之前的文件

for input_file in reversed(input_files):
    output_file_name = os.path.basename(input_file).replace('_changed.json', '_deepseekr1.json')
    output_file = os.path.join(output_dir, output_file_name)

    logging.info(f"Processing File: {input_file}")

    lenofanswer = 0
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            lenofanswer = len(existing_data)

    with open(input_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    while lenofanswer < len(test_data):
        lenofanswer = handle_one_label(input_file, output_file, lenofanswer)

    logging.info(f"Completed processing {input_file}. Results saved in {output_file}.")
