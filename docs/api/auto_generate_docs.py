"""
실제 API 응답 데이터를 기반으로 자동 문서 생성 스크립트

실행방법:
    python docs/api/auto_generate_docs.py
"""

import json
import os
from pathlib import Path
from datetime import datetime

class APIDocGenerator:
    """API 문서 자동 생성기"""
    
    def __init__(self, data_dir="tests/data"):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / data_dir
        self.output_dir = Path(__file__).parent
        self.api_data = {}
        
    def load_test_data(self):
        """테스트 데이터 로드"""
        print("📂 테스트 데이터 로드 중...")
        
        data_files = {
            'notice': 'nexon_api_notice_data.json',
            'event': 'nexon_api_notice-event_data.json'
        }
        
        for key, filename in data_files.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.api_data[key] = json.load(f)
                print(f"✅ {filename} 로드 완료")
            else:
                print(f"⚠️  {filename} 파일이 없습니다")
    
    def analyze_data_structure(self, data, name=""):
        """데이터 구조 분석"""
        analysis = {
            'type': type(data).__name__,
            'description': f"{name} 데이터 구조"
        }
        
        if isinstance(data, dict):
            analysis['properties'] = {}
            for key, value in data.items():
                analysis['properties'][key] = self.analyze_data_structure(value, key)
                
        elif isinstance(data, list):
            analysis['items_count'] = len(data)
            if data:  # 리스트가 비어있지 않으면
                analysis['item_structure'] = self.analyze_data_structure(data[0], f"{name}_item")
                
        elif isinstance(data, str):
            analysis['example'] = data[:100] + "..." if len(data) > 100 else data
            
        else:
            analysis['example'] = data
            
        return analysis
    
    def generate_markdown_docs(self):
        """Markdown 문서 생성"""
        print("📝 Markdown 문서 생성 중...")
        
        doc_content = f"""# MAI 챗봇 API 자동 생성 문서 🤖

> 이 문서는 실제 API 응답 데이터를 기반으로 자동 생성되었습니다.
> 
> **생성 시간**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 데이터 분석 결과

"""
        
        for endpoint, data in self.api_data.items():
            doc_content += f"### {endpoint.upper()} 엔드포인트\n\n"
            
            if data:
                # 기본 정보
                doc_content += f"- **데이터 타입**: `{type(data).__name__}`\n"
                
                if isinstance(data, dict):
                    doc_content += f"- **최상위 키**: `{list(data.keys())}`\n\n"
                    
                    # 각 키별 상세 분석
                    for key, value in data.items():
                        doc_content += f"#### {key} 필드\n\n"
                        
                        if isinstance(value, list):
                            doc_content += f"- **타입**: 배열 (항목 {len(value)}개)\n"
                            
                            if value:  # 배열이 비어있지 않으면
                                first_item = value[0]
                                if isinstance(first_item, dict):
                                    doc_content += f"- **배열 항목 구조**:\n"
                                    for item_key, item_value in first_item.items():
                                        doc_content += f"  - `{item_key}`: {type(item_value).__name__}"
                                        if isinstance(item_value, str) and len(item_value) < 100:
                                            doc_content += f" (예시: \"{item_value}\")"
                                        doc_content += "\n"
                                        
                        else:
                            doc_content += f"- **타입**: {type(value).__name__}\n"
                            if isinstance(value, str) and len(value) < 100:
                                doc_content += f"- **예시**: \"{value}\"\n"
                        
                        doc_content += "\n"
                
                # 실제 응답 예시
                doc_content += f"#### 실제 응답 예시\n\n"
                doc_content += "```json\n"
                
                # 응답 데이터를 보기 좋게 제한
                if isinstance(data, dict):
                    limited_data = {}
                    for key, value in data.items():
                        if isinstance(value, list) and value:
                            # 배열인 경우 첫 2개 항목만 보여주기
                            limited_data[key] = value[:2] + ([{"...more_items": "..."}] if len(value) > 2 else [])
                        else:
                            limited_data[key] = value
                    doc_content += json.dumps(limited_data, indent=2, ensure_ascii=False)
                else:
                    doc_content += json.dumps(data, indent=2, ensure_ascii=False)
                
                doc_content += "\n```\n\n"
                
            doc_content += "---\n\n"
        
        # 사용법 추가
        doc_content += """## 🚀 API 사용법

### cURL로 테스트
```bash
# 공지사항 조회
curl -X GET "http://localhost:8000/nexon_api/notice/"

# 이벤트 조회  
curl -X GET "http://localhost:8000/nexon_api/notice-event/"
```

### Python으로 테스트
```python
import requests

# 공지사항 조회
response = requests.get("http://localhost:8000/nexon_api/notice/")
data = response.json()
print(data)
```

### 자동 테스트 실행
```bash
python tests/api/test_nexon_api.py
```

---

**📅 마지막 업데이트**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

> 💡 **팁**: 이 문서는 `python docs/api/auto_generate_docs.py` 명령어로 언제든 재생성할 수 있습니다!
"""
        
        # 파일 저장
        output_file = self.output_dir / "API_AUTO_GENERATED.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"✅ Markdown 문서 생성 완료: {output_file}")
        return str(output_file)
    
    def generate_json_schema(self):
        """JSON Schema 생성"""
        print("📋 JSON Schema 생성 중...")
        
        schemas = {}
        
        for endpoint, data in self.api_data.items():
            if data and isinstance(data, dict):
                schema = {
                    "type": "object",
                    "properties": {},
                    "example": data
                }
                
                for key, value in data.items():
                    if isinstance(value, list) and value:
                        schema["properties"][key] = {
                            "type": "array",
                            "items": self._generate_schema_for_item(value[0]) if value else {"type": "object"}
                        }
                    else:
                        schema["properties"][key] = self._generate_schema_for_item(value)
                
                schemas[f"{endpoint}_response"] = schema
        
        # Schema 파일 저장
        schema_file = self.output_dir / "api_schemas.json"
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schemas, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON Schema 생성 완료: {schema_file}")
        return str(schema_file)
    
    def _generate_schema_for_item(self, item):
        """개별 항목의 JSON Schema 생성"""
        if isinstance(item, dict):
            return {
                "type": "object",
                "properties": {
                    key: self._generate_schema_for_item(value) 
                    for key, value in item.items()
                }
            }
        elif isinstance(item, list):
            return {
                "type": "array",
                "items": self._generate_schema_for_item(item[0]) if item else {"type": "string"}
            }
        elif isinstance(item, str):
            return {"type": "string", "example": item}
        elif isinstance(item, int):
            return {"type": "integer", "example": item}
        elif isinstance(item, float):
            return {"type": "number", "example": item}
        elif isinstance(item, bool):
            return {"type": "boolean", "example": item}
        else:
            return {"type": "string"}
    
    def generate_all_docs(self):
        """모든 문서 형태 생성"""
        print("🚀 API 문서 자동 생성 시작!")
        print("=" * 50)
        
        # 데이터 로드
        self.load_test_data()
        
        if not self.api_data:
            print("❌ 로드할 테스트 데이터가 없습니다.")
            print("먼저 API 테스트를 실행해주세요: python tests/api/test_nexon_api.py")
            return
        
        # 문서들 생성
        generated_files = []
        
        try:
            # Markdown 문서
            md_file = self.generate_markdown_docs()
            generated_files.append(md_file)
            
            # JSON Schema
            schema_file = self.generate_json_schema()
            generated_files.append(schema_file)
            
        except Exception as e:
            print(f"❌ 문서 생성 중 오류: {e}")
            return
        
        # 결과 출력
        print("\n" + "=" * 50)
        print("✨ 문서 생성 완료!")
        print("\n📁 생성된 파일들:")
        for file_path in generated_files:
            print(f"   📄 {file_path}")
        
        print(f"\n🔗 생성된 문서들:")
        print(f"   📖 Markdown: docs/api/API_AUTO_GENERATED.md")
        print(f"   🔧 Schema: docs/api/api_schemas.json")

def main():
    """메인 실행 함수"""
    generator = APIDocGenerator()
    generator.generate_all_docs()

if __name__ == "__main__":
    main()
