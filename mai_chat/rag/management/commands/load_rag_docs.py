import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from django.core.management.base import BaseCommand
from django.conf import settings
from mai_chat.rag.models import Document
from mai_chat.rag.document_loader import load_document_from_text, load_document_from_json_file

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'RAG 문서 로드: rag_documents 폴더의 JSON 파일들을 벡터 DB에 저장합니다.'

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        rag_docs_dir = base_dir / 'rag_documents'

        if not rag_docs_dir.exists():
            self.stdout.write(self.style.ERROR(f"디렉토리를 찾을 수 없습니다: {rag_docs_dir}"))
            return

        self.stdout.write(self.style.SUCCESS(f"문서 로드 시작: {rag_docs_dir}"))

        # 1. Boss Metadata
        boss_file = rag_docs_dir / 'boss' / 'maplestory_boss_index_metadata.json'
        if boss_file.exists():
            self.process_boss_file(boss_file)
        else:
            self.stdout.write(self.style.WARNING(f"보스 파일 없음: {boss_file}"))

        # 2. Class Metadata
        class_file = rag_docs_dir / 'class' / 'maplestory_class_index_metadata.json'
        if class_file.exists():
            self.process_class_file(class_file)
        else:
            self.stdout.write(self.style.WARNING(f"직업 파일 없음: {class_file}"))

        # 3. Notices
        notice_file = rag_docs_dir / 'notices' / 'notice_data_rag.json'
        if notice_file.exists():
            self.process_notice_file(notice_file)
        else:
            self.stdout.write(self.style.WARNING(f"공지사항 파일 없음: {notice_file}"))

        self.stdout.write(self.style.SUCCESS("모든 작업 완료"))

    def process_boss_file(self, file_path: Path):
        self.stdout.write(f"보스 데이터 처리 중: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            bosses = data.get('boss_monsters', [])
            count = 0
            
            # 기존 보스 문서 삭제 (중복 방지)
            deleted, _ = Document.objects.filter(content_type='guide', source__startswith='boss_metadata').delete()
            if deleted:
                self.stdout.write(f"기존 보스 문서 삭제됨: {deleted}개")

            for boss in bosses:
                name = boss.get('name')
                if not name:
                    continue
                
                # 컨텐츠 텍스트 생성
                content_lines = [f"보스 몬스터: {name}"]
                difficulties = boss.get('difficulties', [])
                for diff in difficulties:
                    diff_name = diff.get('difficulty')
                    level = diff.get('level')
                    hp = diff.get('hp')
                    defense = diff.get('defense_rate')
                    force = diff.get('force', {})
                    force_type = force.get('type')
                    force_val = force.get('value')
                    
                    line = f"- 난이도: {diff_name}, 레벨: {level}, HP: {hp}, 방어율: {defense}%"
                    if force_type and force_type != 'None':
                        line += f", 필요 {force_type}: {force_val}"
                    content_lines.append(line)
                
                content = "\n".join(content_lines)
                
                load_document_from_text(
                    title=f"[보스] {name}",
                    content=content,
                    content_type='guide',
                    source='boss_metadata',
                    metadata={'category': 'boss', 'boss_name': name}
                )
                count += 1
            
            self.stdout.write(self.style.SUCCESS(f"보스 문서 {count}개 로드 완료"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"보스 데이터 처리 실패: {e}"))

    def process_class_file(self, file_path: Path):
        self.stdout.write(f"직업 데이터 처리 중: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                self.stdout.write(self.style.ERROR("직업 데이터가 리스트 형식이 아닙니다."))
                return

            count = 0
            
            # 기존 직업 문서 삭제
            deleted, _ = Document.objects.filter(content_type='guide', source__startswith='class_metadata').delete()
            if deleted:
                self.stdout.write(f"기존 직업 문서 삭제됨: {deleted}개")

            for job in data:
                name = job.get('name')
                if not name:
                    continue
                
                main_cat = job.get('main_category')
                job_class = job.get('job_class')
                stat = job.get('stat')
                
                content = f"직업: {name}\n계열: {main_cat}\n직업군: {job_class}\n주스탯: {stat}"
                
                load_document_from_text(
                    title=f"[직업] {name}",
                    content=content,
                    content_type='guide',
                    source='class_metadata',
                    metadata=job
                )
                count += 1
                
            self.stdout.write(self.style.SUCCESS(f"직업 문서 {count}개 로드 완료"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"직업 데이터 처리 실패: {e}"))

    def process_notice_file(self, file_path: Path):
        self.stdout.write(f"공지사항 데이터 처리 중: {file_path}")
        try:
            # 기존 공지사항 삭제
            deleted, _ = Document.objects.filter(content_type='notice').delete()
            if deleted:
                self.stdout.write(f"기존 공지사항 문서 삭제됨: {deleted}개")

            docs = load_document_from_json_file(str(file_path))
            self.stdout.write(self.style.SUCCESS(f"공지사항 문서 {len(docs)}개 로드 완료"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"공지사항 데이터 처리 실패: {e}"))
