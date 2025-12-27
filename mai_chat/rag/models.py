# -*- coding: utf-8 -*-
"""
RAG Django 모델

문서와 청크를 저장하는 Django 모델입니다.
벡터 임베딩은 pgvector VectorField로 직접 저장됩니다.
"""

import uuid
from django.db import models
from django.utils import timezone
from pgvector.django import VectorField


class Document(models.Model):
    """
    원본 문서 메타데이터
    
    메이플스토리 관련 가이드, 공지사항, 아이템 정보 등의 원본 문서를 저장합니다.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="문서 ID"
    )
    title = models.CharField(
        max_length=500,
        verbose_name="문서 제목"
    )
    source = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="출처 URL 또는 파일명"
    )
    content_type = models.CharField(
        max_length=50,
        choices=[
            ('guide', '가이드'),
            ('notice', '공지사항'),
            ('item', '아이템 정보'),
            ('quest', '퀘스트 정보'),
            ('skill', '스킬 정보'),
            ('other', '기타')
        ],
        default='other',
        verbose_name="문서 타입"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="추가 메타데이터"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성 시각"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정 시각"
    )
    
    class Meta:
        db_table = "mai_rag_document"
        verbose_name = "RAG 문서"
        verbose_name_plural = "RAG 문서"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type"]),
            models.Index(fields=["-created_at"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.title} ({self.content_type})"


class DocumentChunk(models.Model):
    """
    문서 청크
    
    원본 문서를 검색 최적화를 위해 작은 단위로 분할한 청크입니다.
    각 청크는 독립적으로 임베딩되고 검색됩니다.
    벡터 임베딩은 pgvector VectorField에 저장됩니다.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="청크 ID"
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks",
        verbose_name="원본 문서"
    )
    content = models.TextField(
        verbose_name="청크 내용"
    )
    chunk_index = models.IntegerField(
        verbose_name="청크 순서",
        help_text="원본 문서 내에서의 순서"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="청크 메타데이터",
    )
    embedding = VectorField(dimensions=768, null=True, blank=True, verbose_name="청크 임베딩")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성 시각"
    )
    
    class Meta:
        db_table = "mai_rag_chunk"
        verbose_name = "문서 청크"
        verbose_name_plural = "문서 청크"
        ordering = ["document", "chunk_index"]
        unique_together = [["document", "chunk_index"]]
        indexes = [
            models.Index(fields=["document", "chunk_index"]),
        ]
    
    def __str__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.document.title} - Chunk {self.chunk_index}: {preview}"

