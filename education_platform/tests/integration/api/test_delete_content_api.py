from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_delete_course_returns_204(
    client, seeded_course_tree, admin_auth_headers
) -> None:
    response = await client.delete(
        f"/api/admin/courses/{seeded_course_tree.course_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_course_returns_404_when_missing(
    client, admin_auth_headers
) -> None:
    response = await client.delete(
        f"/api/admin/courses/{uuid4()}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] == "course_not_found"


@pytest.mark.asyncio
async def test_delete_course_returns_401_without_auth(
    client, seeded_course_tree
) -> None:
    response = await client.delete(
        f"/api/admin/courses/{seeded_course_tree.course_id}",
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload["error"] == "authentication_error"


@pytest.mark.asyncio
async def test_delete_course_returns_403_for_student(
    client, seeded_course_tree, student_auth_headers
) -> None:
    response = await client.delete(
        f"/api/admin/courses/{seeded_course_tree.course_id}",
        headers=student_auth_headers,
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_delete_module_returns_204(
    client, seeded_course_tree, admin_auth_headers
) -> None:
    response = await client.delete(
        f"/api/admin/modules/{seeded_course_tree.module_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_module_returns_404_when_missing(
    client, admin_auth_headers
) -> None:
    response = await client.delete(
        f"/api/admin/modules/{uuid4()}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] == "module_not_found"


@pytest.mark.asyncio
async def test_delete_section_returns_204(
    client, seeded_course_tree, admin_auth_headers
) -> None:
    response = await client.delete(
        f"/api/admin/sections/{seeded_course_tree.section_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_section_returns_404_when_missing(
    client, admin_auth_headers
) -> None:
    response = await client.delete(
        f"/api/admin/sections/{uuid4()}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] == "section_not_found"


@pytest.mark.asyncio
async def test_delete_lecture_returns_204(
    client, seeded_course_tree, admin_auth_headers
) -> None:
    response = await client.delete(
        f"/api/admin/lectures/{seeded_course_tree.lecture_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_lecture_returns_404_when_missing(
    client, admin_auth_headers
) -> None:
    response = await client.delete(
        f"/api/admin/lectures/{uuid4()}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] == "lecture_not_found"


@pytest.mark.asyncio
async def test_after_deleting_course_public_api_returns_404(
    client, seeded_course_tree, admin_auth_headers
) -> None:
    await client.delete(
        f"/api/admin/courses/{seeded_course_tree.course_id}",
        headers=admin_auth_headers,
    )

    response = await client.get(f"/api/courses/{seeded_course_tree.course_id}")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] == "course_not_found"


@pytest.mark.asyncio
async def test_after_deleting_course_it_disappears_from_list(
    client, seeded_course_tree, admin_auth_headers
) -> None:
    await client.delete(
        f"/api/admin/courses/{seeded_course_tree.course_id}",
        headers=admin_auth_headers,
    )

    response = await client.get("/api/courses")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_after_deleting_module_structure_is_updated(
    client, seeded_course_tree, admin_auth_headers
) -> None:
    await client.delete(
        f"/api/admin/modules/{seeded_course_tree.module_id}",
        headers=admin_auth_headers,
    )

    response = await client.get(
        f"/api/courses/{seeded_course_tree.course_id}/structure"
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["modules"]) == 0


@pytest.mark.asyncio
async def test_after_deleting_lecture_public_api_returns_404(
    client, seeded_course_tree, admin_auth_headers
) -> None:
    await client.delete(
        f"/api/admin/lectures/{seeded_course_tree.lecture_id}",
        headers=admin_auth_headers,
    )

    response = await client.get(f"/api/lectures/{seeded_course_tree.lecture_id}")
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] == "lecture_not_found"
