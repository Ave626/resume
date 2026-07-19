import pytest

@pytest.mark.asyncio
async def test_delete_module_cascade_removes_sections_and_lectures(
    client, seeded_admin_user
) -> None:
    login_response = await client.post(
        '/api/auth/login',
        json={
            'email': 'admin@example.com',
            'password': 'strongpassword123',
        },
    )
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    course_resp = await client.post(
        '/api/admin/courses',
        headers=headers,
        json={'title': 'Course', 'description': 'Description'},
    )
    course_id = course_resp.json()['id']

    module_resp = await client.post(
        f'/api/admin/courses/{course_id}/modules',
        headers=headers,
        json={'title': 'Module', 'description': 'Description', 'position': 1},
    )
    module_id = module_resp.json()['id']

    section_resp = await client.post(
        f'/api/admin/modules/{module_id}/sections',
        headers=headers,
        json={'title': 'Section', 'description': 'Description', 'position': 1},
    )
    section_id = section_resp.json()['id']

    lecture_resp = await client.post(
        f'/api/admin/sections/{section_id}/lectures',
        headers=headers,
        json={'title': 'Lecture', 'content': 'Content', 'position': 1},
    )
    lecture_id = lecture_resp.json()['id']

    delete_resp = await client.delete(
        f'/api/admin/modules/{module_id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert delete_resp.status_code == 204

    course_resp = await client.get(f'/api/courses/{course_id}')
    assert course_resp.status_code == 200

    structure_resp = await client.get(f'/api/courses/{course_id}/structure')
    assert structure_resp.status_code == 200
    assert len(structure_resp.json()['modules']) == 0
    
    lecture_resp = await client.get(f'/api/lectures/{lecture_id}')
    assert lecture_resp.status_code == 404
    assert lecture_resp.json()['error'] == 'lecture_not_found'