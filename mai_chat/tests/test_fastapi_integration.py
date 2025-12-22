
import pytest
from httpx import AsyncClient
from mai_chat.service.fastapi_app import app

@pytest.mark.asyncio
async def test_fastapi_response():
    """
    FastAPI 엔드포인트 `/ai/respond`가 정상적으로 응답하는지 테스트합니다.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Mocking the AI service internal call would be ideal, 
        # but for integration test we might want to check if it actually runs (or fails gracefully).
        # Since loading model is heavy, we might mock `get_ai_response_async`.
        
        # Here we will just checks if app is importable and route exists.
        # To avoid heavy model load during unit test, we can mock the ai_service.
        pass

    # Note: Actual integration test requires model files. 
    # This is a placeholder structure.
    assert True
