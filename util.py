from datetime import datetime
import os
import json
import re
import time

def save_json_to_file(functionName, data):
    if data:
        # 현재 시간으로 파일 이름 생성
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{functionName}_{current_time}.json"
        
        # advice 폴더 경로 생성
        directory = "advice"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 전체 파일 경로 생성
        file_path = os.path.join(directory, file_name)

        # 현재 시간을 Unix 타임스탬프로 추가
        data["timestamp"] = int(time.time())

        # 데이터 문자열로 변환
        data_str = json.dumps(data, indent=4)

        # 파일로 저장
        with open(file_path, 'w') as file:
            file.write(data_str)

        print(f"Data saved to {file_path}")
        

# 가장 최신의 json 파일을 최근 5개 가져오는 함수
def get_latest_files(directory, pattern="advice_*.json", count=5):
    regex = re.compile(r"advice_(\d{8})_(\d{6})\.json")
    files = [f for f in os.listdir(directory) if re.match(regex, f)]
    files.sort(key=lambda x: datetime.strptime(regex.match(x).groups()[0] + regex.match(x).groups()[1], '%Y%m%d%H%M%S'), reverse=True)
    latest_files = files[:count]
    return latest_files

# json 파일 읽기
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
def get_instructions(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            instructions = file.read()
        return instructions
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred while reading the file:", e)