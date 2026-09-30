import pytest


@pytest.mark.asyncio
async def test_student_can_create_lecture_comment(
    client,
    student_auth_headers,
    seeded_comments_tree,
):
    response = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Great explanation of Clean Architecture."},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["target_type"] == "lecture"
    assert payload["target_id"] == seeded_comments_tree.lecture_id
    assert payload["text"] == "Great explanation of Clean Architecture."
    assert "id" in payload
    assert "created_at" in payload
    assert payload["updated_at"] is None


@pytest.mark.asyncio
async def test_student_can_get_lecture_comments(
    client,
    student_auth_headers,
    seeded_comments_tree,
):
    first_res = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "First comment"},
    )
    second_res = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Second comment"},
    )

    response = await client.get(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["id"] == first_res.json()["id"]
    assert payload[0]["text"] == "First comment"
    assert payload[1]["id"] == second_res.json()["id"]
    assert payload[1]["text"] == "Second comment"


@pytest.mark.asyncio
async def test_unauthenticated_user_cannot_create_comment(
    client,
    seeded_comments_tree,
):
    response = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        json={"text": "Unauthorized attempt"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_student_cannot_comment_inaccessible_lecture(
    client,
    student_auth_headers,
    seeded_comments_tree,
):
    response = await client.post(
        f"/api/lectures/{seeded_comments_tree.draft_lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Trying to comment on draft lecture"},
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_author_cannot_create_comment_as_student(
    client,
    author_auth_headers,
    seeded_comments_tree,
):
    response = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=author_auth_headers,
        json={"text": "Author trying to leave a student comment"},
    )

    assert response.status_code == 403
    assert response.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_comment_author_can_update_own_comment(
    client,
    student_auth_headers,
    seeded_comments_tree,
):
    create_res = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Initial comment"},
    )
    comment_id = create_res.json()["id"]

    patch_res = await client.patch(
        f"/api/comments/{comment_id}",
        headers=student_auth_headers,
        json={"text": "Edited comment"},
    )

    assert patch_res.status_code == 200
    payload = patch_res.json()
    assert payload["id"] == comment_id
    assert payload["text"] == "Edited comment"
    assert payload["updated_at"] is not None


@pytest.mark.asyncio
async def test_other_student_cannot_update_comment(
    client,
    student_auth_headers,
    seeded_comments_tree,
):
    create_res = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Initial comment"},
    )
    comment_id = create_res.json()["id"]

    await client.post(
        "/api/auth/register",
        json={
            "email": "second_student@example.com",
            "password": "password123",
            "role": "student",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={
            "email": "second_student@example.com",
            "password": "password123",
        },
    )
    second_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    patch_res = await client.patch(
        f"/api/comments/{comment_id}",
        headers=second_headers,
        json={"text": "Hacker update"},
    )

    assert patch_res.status_code == 403
    assert patch_res.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_comment_author_can_delete_own_comment(
    client,
    student_auth_headers,
    seeded_comments_tree,
):
    create_res = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Comment to be deleted"},
    )
    comment_id = create_res.json()["id"]

    del_res = await client.delete(
        f"/api/comments/{comment_id}",
        headers=student_auth_headers,
    )

    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_course_author_can_delete_comment_under_their_course(
    client,
    student_auth_headers,
    author_auth_headers,
    seeded_comments_tree,
):
    create_res = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Student comment to moderate"},
    )
    comment_id = create_res.json()["id"]

    del_res = await client.delete(
        f"/api/comments/{comment_id}",
        headers=author_auth_headers,
    )

    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_foreign_author_cannot_delete_comment(
    client,
    student_auth_headers,
    seeded_comments_tree,
):
    create_res = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Student comment"},
    )
    comment_id = create_res.json()["id"]

    await client.post(
        "/api/auth/register",
        json={
            "email": "foreign_author@example.com",
            "password": "password123",
            "role": "author",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={
            "email": "foreign_author@example.com",
            "password": "password123",
        },
    )
    foreign_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    del_res = await client.delete(
        f"/api/comments/{comment_id}",
        headers=foreign_headers,
    )

    assert del_res.status_code == 403
    assert del_res.json()["error"] == "permission_denied"


@pytest.mark.asyncio
async def test_admin_can_delete_any_comment(
    client,
    student_auth_headers,
    admin_auth_headers,
    seeded_comments_tree,
):
    create_res = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Student comment for admin deletion"},
    )
    comment_id = create_res.json()["id"]

    del_res = await client.delete(
        f"/api/comments/{comment_id}",
        headers=admin_auth_headers,
    )

    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_deleted_comment_disappears_from_list(
    client,
    student_auth_headers,
    seeded_comments_tree,
):
    create_res = await client.post(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
        json={"text": "Will be deleted"},
    )
    comment_id = create_res.json()["id"]

    await client.delete(
        f"/api/comments/{comment_id}",
        headers=student_auth_headers,
    )

    get_res = await client.get(
        f"/api/lectures/{seeded_comments_tree.lecture_id}/comments",
        headers=student_auth_headers,
    )

    assert get_res.status_code == 200
    assert len(get_res.json()) == 0


@pytest.mark.asyncio
async def test_universal_comments_endpoints(
    client,
    student_auth_headers,
    seeded_comments_tree,
):
    post_res = await client.post(
        "/api/comments",
        headers=student_auth_headers,
        json={
            "target_type": "lecture",
            "target_id": seeded_comments_tree.lecture_id,
            "text": "Created via universal endpoint",
        },
    )

    assert post_res.status_code == 201
    payload = post_res.json()
    assert payload["target_type"] == "lecture"
    assert payload["text"] == "Created via universal endpoint"

    get_res = await client.get(
        f"/api/comments?target_type=lecture&target_id={seeded_comments_tree.lecture_id}",
        headers=student_auth_headers,
    )

    assert get_res.status_code == 200
    comments = get_res.json()
    assert len(comments) == 1
    assert comments[0]["text"] == "Created via universal endpoint"
