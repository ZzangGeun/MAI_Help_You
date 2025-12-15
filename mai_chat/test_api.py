# -*- coding: utf-8 -*-
"""
MAI Chat API 테스트 스크립트

Django 서버가 실행 중일 때 이 스크립트를 실행하여 API를 테스트합니다.
"""

import requests
import json
from typing import Optional, Dict, Any


# API 기본 URL
BASE_URL = "http://localhost:8000/mai_chat"


class MaiChatAPITester:
    """MAI Chat API 테스트 클래스"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def print_separator(self, title: str = "") -> None:
        """구분선 출력"""
        print("\n" + "="*60)
        if title:
            print(f"  {title}")
            print("="*60)
    
    def print_response(self, response: requests.Response, show_json: bool = True) -> None:
        """응답 정보 출력"""
        print(f"상태 코드: {response.status_code}")
        if show_json:
            try:
                data = response.json()
                print(f"응답 데이터:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print(f"응답 텍스트: {response.text}")
    
    def test_create_session(self) -> bool:
        """세션 생성 테스트"""
        self.print_separator("1. 세션 생성 테스트")
        
        try:
            response = requests.post(f"{self.base_url}/api/chat/session/")
            self.print_response(response)
            
            if response.status_code == 201:
                data = response.json()
                self.session_id = data.get("session_id")
                print(f"\n✅ 세션 생성 성공! Session ID: {self.session_id}")
                return True
            else:
                print(f"\n❌ 세션 생성 실패")
                return False
        
        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")
            return False
    
    def test_chat(self, question: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """채팅 테스트"""
        self.print_separator(f"채팅 테스트: '{question}'")
        
        payload = {"question": question}
        if session_id:
            payload["session_id"] = session_id
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat/",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            self.print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ AI 응답: {data.get('response', '')[:100]}...")
                print(f"   응답 시간: {data.get('response_time', 0)}ms")
                
                # 세션 ID 저장
                if not self.session_id:
                    self.session_id = data.get("session_id")
                
                return data
            else:
                print(f"\n❌ 채팅 실패")
                return None
        
        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")
            return None
    
    def test_get_history(self, session_id: Optional[str] = None) -> bool:
        """히스토리 조회 테스트"""
        sid = session_id or self.session_id
        if not sid:
            print("❌ 세션 ID가 없습니다.")
            return False
        
        self.print_separator("히스토리 조회 테스트")
        
        try:
            response = requests.get(f"{self.base_url}/api/chat/history/{sid}/")
            self.print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ 히스토리 조회 성공! 메시지 수: {data.get('message_count', 0)}")
                return True
            else:
                print(f"\n❌ 히스토리 조회 실패")
                return False
        
        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")
            return False
    
    def test_delete_session(self, session_id: Optional[str] = None) -> bool:
        """세션 삭제 테스트"""
        sid = session_id or self.session_id
        if not sid:
            print("❌ 세션 ID가 없습니다.")
            return False
        
        self.print_separator("세션 삭제 테스트")
        
        try:
            response = requests.delete(f"{self.base_url}/api/chat/session/{sid}/")
            self.print_response(response)
            
            if response.status_code == 200:
                print(f"\n✅ 세션 삭제 성공!")
                self.session_id = None
                return True
            else:
                print(f"\n❌ 세션 삭제 실패")
                return False
        
        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")
            return False
    
    def run_full_test(self) -> None:
        """전체 테스트 실행"""
        print("\n" + "🚀 MAI Chat API 전체 테스트 시작".center(60, "="))
        
        # 1. 세션 생성
        if not self.test_create_session():
            print("\n❌ 세션 생성에 실패하여 테스트를 중단합니다.")
            return
        
        # 2. 첫 번째 채팅 (세션 ID 포함)
        self.test_chat(
            "메이플스토리에서 전사 직업은 뭐가 있어?",
            session_id=self.session_id
        )
        
        # 3. 두 번째 채팅 (대화 컨텍스트 유지 확인)
        self.test_chat(
            "그 중에서 가장 인기있는 직업은?",
            session_id=self.session_id
        )
        
        # 4. 히스토리 조회
        self.test_get_history()
        
        # 5. 세션 삭제
        self.test_delete_session()
        
        print("\n" + "✅ 전체 테스트 완료".center(60, "=") + "\n")


def test_without_session() -> None:
    """세션 ID 없이 채팅 테스트 (자동 세션 생성)"""
    print("\n" + "🧪 세션 없이 채팅 테스트".center(60, "="))
    
    tester = MaiChatAPITester()
    response = tester.test_chat("안녕? 메이플스토리가 뭐야?")
    
    if response:
        print(f"\n자동 생성된 세션 ID: {response.get('session_id')}")


def test_conversation_memory() -> None:
    """대화 메모리 테스트 (LangChain)"""
    print("\n" + "🧠 대화 메모리 테스트".center(60, "="))
    
    tester = MaiChatAPITester()
    
    # 세션 생성
    tester.test_create_session()
    
    # 연속된 대화로 메모리 테스트
    questions = [
        "메이플스토리에서 아란이 뭐야?",
        "아란의 주요 스킬은?",  # 이전 대화 컨텍스트 활용
        "그 직업의 장단점은?",  # 이전 대화 컨텍스트 활용
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n[질문 {i}] {question}")
        tester.test_chat(question, session_id=tester.session_id)
    
    # 히스토리 확인
    tester.test_get_history()


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("  MAI Chat API 테스트 도구".center(60))
    print("="*60)
    print("\n주의: Django 서버가 실행 중이어야 합니다!")
    print("명령: python manage.py runserver\n")
    
    # 사용자 선택
    print("테스트 옵션:")
    print("1. 전체 테스트 (권장)")
    print("2. 세션 없이 간단한 채팅")
    print("3. 대화 메모리 테스트")
    print("4. 커스텀 테스트")
    
    choice = input("\n선택 (1-4): ").strip()
    
    if choice == "1":
        tester = MaiChatAPITester()
        tester.run_full_test()
    
    elif choice == "2":
        test_without_session()
    
    elif choice == "3":
        test_conversation_memory()
    
    elif choice == "4":
        # 커스텀 테스트
        tester = MaiChatAPITester()
        tester.test_create_session()
        
        while True:
            question = input("\n질문 입력 (종료: q): ").strip()
            if question.lower() == 'q':
                break
            
            tester.test_chat(question, session_id=tester.session_id)
        
        tester.test_delete_session()
    
    else:
        print("❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    main()
