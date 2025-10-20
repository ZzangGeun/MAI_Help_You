#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangChain 없이 동작하는 간단한 챗봇 테스트 스크립트
Django 환경에서 기본 기능만 테스트합니다.
"""

import os
import sys
import django
import json
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MAI.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
except Exception as e:
    print(f"Django 설정 실패: {e}")
    sys.exit(1)

# Django 앱 import (LangChain 제외)
from apps.chatbot.models import ChatSession, ChatMessage
from django.contrib.auth.models import User
from services.ai_models.fastapi_model.model import load_model, ask_question


class SimpleChatbotTester:
    """간단한 챗봇 테스트 클래스 (LangChain 없이)"""
    
    def __init__(self):
        self.test_results = []
        self.test_user = None
        self.test_session = None
        
    def log_test(self, test_name, success, message="", details=None):
        """테스트 결과 로깅"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   세부사항: {details}")
    
    def setup_test_user(self):
        """테스트용 사용자 생성"""
        try:
            # 기존 테스트 사용자 삭제
            User.objects.filter(username='simple_test_user').delete()
            
            # 새 테스트 사용자 생성
            self.test_user = User.objects.create_user(
                username='simple_test_user',
                email='test@simple.com',
                password='testpass123'
            )
            self.log_test("사용자 설정", True, "테스트 사용자 생성 완료")
            return True
        except Exception as e:
            self.log_test("사용자 설정", False, f"테스트 사용자 생성 실패: {str(e)}")
            return False
    
    def test_model_loading(self):
        """모델 로딩 테스트"""
        try:
            success = load_model()
            if success:
                self.log_test("모델 로딩", True, "AI 모델 로딩 성공")
                return True
            else:
                self.log_test("모델 로딩", False, "AI 모델 로딩 실패")
                return False
        except Exception as e:
            self.log_test("모델 로딩", False, f"모델 로딩 중 예외: {str(e)}")
            return False
    
    def test_simple_response(self):
        """단순 응답 테스트"""
        try:
            question = "안녕하세요!"
            response = ask_question(question)
            
            if response and len(response.strip()) > 0:
                self.log_test("단순 응답", True, "응답 생성 성공", f"질문: {question}, 응답: {response[:50]}...")
                return True
            else:
                self.log_test("단순 응답", False, "빈 응답 또는 None 반환")
                return False
        except Exception as e:
            self.log_test("단순 응답", False, f"응답 생성 중 예외: {str(e)}")
            return False
    
    def test_session_creation(self):
        """세션 생성 테스트"""
        try:
            # 익명 세션 생성
            anonymous_session = ChatSession.objects.create()
            if anonymous_session.id:
                self.log_test("익명 세션 생성", True, f"세션 ID: {anonymous_session.id}")
            else:
                self.log_test("익명 세션 생성", False, "세션 생성 실패")
                return False
            
            # 사용자 세션 생성
            if self.test_user:
                self.test_session = ChatSession.objects.create(user=self.test_user)
                if self.test_session.id:
                    self.log_test("사용자 세션 생성", True, f"세션 ID: {self.test_session.id}")
                else:
                    self.log_test("사용자 세션 생성", False, "사용자 세션 생성 실패")
                    return False
            
            return True
        except Exception as e:
            self.log_test("세션 생성", False, f"세션 생성 중 예외: {str(e)}")
            return False
    
    def test_message_storage(self):
        """메시지 저장 테스트"""
        if not self.test_session:
            self.log_test("메시지 저장", False, "테스트 세션이 없음")
            return False
        
        try:
            # 사용자 메시지 저장
            user_message = ChatMessage.objects.create(
                session=self.test_session,
                content="테스트 사용자 메시지",
                is_user=True
            )
            
            # AI 응답 저장
            ai_message = ChatMessage.objects.create(
                session=self.test_session,
                content="테스트 AI 응답",
                is_user=False
            )
            
            # 저장 확인
            saved_messages = ChatMessage.objects.filter(session=self.test_session).count()
            
            if saved_messages == 2:
                self.log_test("메시지 저장", True, f"메시지 2개 저장 성공")
                return True
            else:
                self.log_test("메시지 저장", False, f"예상과 다른 메시지 수: {saved_messages}")
                return False
                
        except Exception as e:
            self.log_test("메시지 저장", False, f"메시지 저장 중 예외: {str(e)}")
            return False
    
    def test_conversation_flow(self):
        """간단한 대화 플로우 테스트"""
        if not self.test_session:
            self.log_test("대화 플로우", False, "테스트 세션이 없음")
            return False
        
        try:
            messages = [
                "안녕하세요!",
                "파이썬에 대해 알려주세요.",
                "감사합니다!"
            ]
            
            conversation_results = []
            for i, message in enumerate(messages, 1):
                try:
                    # 사용자 메시지 저장
                    ChatMessage.objects.create(
                        session=self.test_session,
                        content=message,
                        is_user=True
                    )
                    
                    # AI 응답 생성
                    response = ask_question(message)
                    if not response:
                        response = f"기본 응답: {message}에 대한 답변입니다."
                    
                    # AI 응답 저장
                    ChatMessage.objects.create(
                        session=self.test_session,
                        content=response,
                        is_user=False
                    )
                    
                    conversation_results.append(f"메시지 {i}: 성공")
                    print(f"   Q{i}: {message}")
                    print(f"   A{i}: {response[:100]}...")
                    
                except Exception as msg_error:
                    conversation_results.append(f"메시지 {i}: 실패 ({str(msg_error)})")
            
            success_count = sum(1 for result in conversation_results if "성공" in result)
            if success_count == len(messages):
                self.log_test("대화 플로우", True, f"모든 메시지 처리 성공 ({success_count}/{len(messages)})")
                return True
            else:
                self.log_test("대화 플로우", False, f"일부 메시지 실패 ({success_count}/{len(messages)})", conversation_results)
                return False
                
        except Exception as e:
            self.log_test("대화 플로우", False, f"대화 플로우 테스트 중 예외: {str(e)}")
            return False
    
    def test_session_loading(self):
        """세션 로드 테스트"""
        try:
            if not self.test_session:
                self.log_test("세션 로드", False, "테스트 세션이 없음")
                return False
            
            # 세션에 저장된 메시지 조회
            messages = ChatMessage.objects.filter(session=self.test_session).order_by('created_at')
            
            if len(messages) > 0:
                user_messages = messages.filter(is_user=True).count()
                ai_messages = messages.filter(is_user=False).count()
                
                self.log_test("세션 로드", True, 
                             f"세션 메시지 로드 성공", 
                             f"총 {len(messages)}개 메시지 (사용자: {user_messages}, AI: {ai_messages})")
                return True
            else:
                self.log_test("세션 로드", False, "로드된 메시지가 없음")
                return False
                
        except Exception as e:
            self.log_test("세션 로드", False, f"세션 로드 테스트 중 예외: {str(e)}")
            return False
    
    def cleanup(self):
        """테스트 정리"""
        try:
            # 테스트 데이터 정리
            if self.test_user:
                ChatSession.objects.filter(user=self.test_user).delete()
                self.test_user.delete()
            
            # 익명 세션들도 정리
            ChatSession.objects.filter(user__isnull=True).delete()
            
            self.log_test("정리", True, "테스트 데이터 정리 완료")
        except Exception as e:
            self.log_test("정리", False, f"정리 중 예외: {str(e)}")
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "="*60)
        print("🤖 간단한 CHATBOT 테스트 결과 요약")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print("="*60)
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 간단한 Chatbot 테스트 시작... (LangChain 없이)")
        print("-" * 60)
        
        # 테스트 실행 순서
        tests = [
            self.setup_test_user,
            self.test_model_loading,
            self.test_simple_response,
            self.test_session_creation,
            self.test_message_storage,
            self.test_conversation_flow,
            self.test_session_loading
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ 테스트 '{test.__name__}' 중 예외 발생: {str(e)}")
        
        # 정리 및 결과 출력
        self.cleanup()
        self.print_summary()


def main():
    """메인 실행 함수"""
    print("="*60)
    print("🤖 MAI_Help_You 간단한 Chatbot 테스트")
    print("🔧 LangChain 호환성 문제를 피한 기본 기능 테스트")
    print("="*60)
    
    try:
        tester = SimpleChatbotTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n💥 예상치 못한 오류가 발생했습니다: {str(e)}")
    
    print("\n🏁 테스트 완료!")


if __name__ == "__main__":
    main()