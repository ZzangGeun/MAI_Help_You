import os
import json

def merge_json_files(directory_path):
    merged_data = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                merged_data.extend(data)
    
    return merged_data

# 디렉토리 경로 설정
directory_path = r'C:\Users\ccg70\OneDrive\desktop\nexon_project\maple_db\src\crawling\maple_inven_data'

# JSON 파일 병합
merged_data = merge_json_files(directory_path)

# 병합된 데이터를 새 JSON 파일로 저장
output_path = os.path.join(directory_path, 'merged_posts.json')
with open(output_path, 'w', encoding='utf-8') as output_file:
    json.dump(merged_data, output_file, ensure_ascii=False, indent=4)

print(f"병합된 데이터가 {output_path}에 저장되었습니다.")