from datetime import datetime
import os
import json

def save_json_to_file(functionName, data):
    if data:
        # 현재 시간으로 파일 이름 생성
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{functionName}_{current_time}.json"
        
        # data 폴더 경로 생성
        directory = "data"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 전체 파일 경로 생성
        file_path = os.path.join(directory, file_name)

        # 데이터 문자열로 변환
        data_str = json.dumps(data, indent=4)

        # 파일로 저장
        with open(file_path, 'w') as file:
            file.write(data_str)

        print(f"Data saved to {file_path}")