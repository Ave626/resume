import pytest
from uuid import uuid4
from app.application.interfaces.services.file_storage import FileStorage
import app.presentation.api.dependencies as api_dependencies


class FakeFileStorage(FileStorage):
    def __init__(self) -> None:
        self.uploaded_files: dict[str, bytes] = {}

    async def upload(self, file_name: str, content: bytes, content_type: str) -> str:
        self.uploaded_files[file_name] = content
        return f"http://test-cdn.local/{file_name}"


@pytest.fixture
def fake_storage():
    return FakeFileStorage()


@pytest.fixture(autouse=True)
def override_file_storage(app, fake_storage):
    app.dependency_overrides[api_dependencies.get_file_storage] = lambda: fake_storage
    yield
    app.dependency_overrides.pop(api_dependencies.get_file_storage, None)


@pytest.mark.asyncio
async def test_author_can_upload_course_cover(
    client,
    author_auth_headers,
    fake_storage,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Course for Cover Upload",
            "description": "Testing cover upload flow.",
        },
    )
    assert create_response.status_code == 201
    course_id = create_response.json()["id"]

    file_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files={"file": ("cover.png", file_bytes, "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == course_id
    assert payload["cover_image_url"] is not None
    assert payload["cover_image_url"].startswith("http://test-cdn.local/covers/")
    assert payload["cover_image_url"].endswith(".png")
    assert len(fake_storage.uploaded_files) == 1


@pytest.mark.asyncio
async def test_admin_can_upload_course_cover(
    client,
    author_auth_headers,
    admin_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Author Course",
            "description": "Admin will upload cover.",
        },
    )
    course_id = create_response.json()["id"]

    file_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 32
    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=admin_auth_headers,
        files={"file": ("cover.jpg", file_bytes, "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["cover_image_url"].endswith(".jpg")


@pytest.mark.asyncio
async def test_other_author_cannot_upload_course_cover(
    client,
    author_auth_headers,
    seeded_other_author_user,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Author Course",
            "description": "Other author should be rejected.",
        },
    )
    course_id = create_response.json()["id"]

    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "other-author@example.com",
            "password": "strongpassword123",
        },
    )
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    file_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=other_headers,
        files={"file": ("cover.png", file_bytes, "image/png")},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_cannot_upload_course_cover(client):
    response = await client.post(
        f"/api/admin/courses/{uuid4()}/cover",
        files={"file": ("cover.png", b"image-data", "image/png")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_cover_course_not_found(
    client,
    author_auth_headers,
):
    missing_id = uuid4()
    file_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    response = await client.post(
        f"/api/admin/courses/{missing_id}/cover",
        headers=author_auth_headers,
        files={"file": ("cover.png", file_bytes, "image/png")},
    )
    assert response.status_code == 404
    assert response.json()["error"] == "course_not_found"


@pytest.mark.asyncio
async def test_upload_cover_rejects_unsupported_extension(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Course Test",
            "description": "Validation test.",
        },
    )
    course_id = create_response.json()["id"]

    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files={"file": ("danger.exe", b"malicious content", "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_course_cover_file"


@pytest.mark.asyncio
async def test_upload_cover_rejects_unsupported_content_type(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Course Test",
            "description": "Validation test.",
        },
    )
    course_id = create_response.json()["id"]

    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files={"file": ("cover.png", b"pdf content", "application/pdf")},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_course_cover_file"


@pytest.mark.asyncio
async def test_upload_cover_rejects_empty_file(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Course Test",
            "description": "Validation test.",
        },
    )
    course_id = create_response.json()["id"]

    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files={"file": ("cover.png", b"", "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_course_cover_file"


@pytest.mark.asyncio
async def test_upload_cover_rejects_oversized_file(
    client,
    author_auth_headers,
):
    create_response = await client.post(
        "/api/admin/courses",
        headers=author_auth_headers,
        json={
            "title": "Course Test",
            "description": "Validation test.",
        },
    )
    course_id = create_response.json()["id"]

    oversized = b"a" * (5 * 1024 * 1024 + 1)
    response = await client.post(
        f"/api/admin/courses/{course_id}/cover",
        headers=author_auth_headers,
        files={"file": ("cover.png", oversized, "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_course_cover_file"
