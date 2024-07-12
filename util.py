from datetime import datetime

def save_json_to_file(functionName, data):
    # 현재 시간으로 파일 이름 생성
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{functionName}_{current_time}.json"

    # 파일로 저장
    with open(file_name, 'w') as file:
        file.write(data)

    print(f"Position summary saved to {file_name}")