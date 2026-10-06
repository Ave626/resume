from uuid import UUID

import pytest

from app.infrastructure.database.repositories import (
    SqlAlchemyCourseCatalogMetricsRepository,
)


@pytest.mark.asyncio
async def test_catalog_metrics_are_aggregated_in_database(
    session_factory,
    seeded_course_tree,
):
    course_id = UUID(seeded_course_tree.course_id)
    async with session_factory() as session:
        repository = SqlAlchemyCourseCatalogMetricsRepository(session)
        metrics_by_course = await repository.get_by_course_ids([course_id])
        metrics = metrics_by_course[course_id]

        assert metrics.counters.module_count == 1
        assert metrics.counters.section_count == 1
        assert metrics.counters.lecture_count == 1
        assert metrics.counters.question_count == 0
        assert metrics.counters.task_count == 0
        assert metrics.counters.code_task_count == 0
        assert metrics.rating.average_rating == 0.0
        assert metrics.rating.reviews_count == 0


@pytest.mark.asyncio
async def test_catalog_metrics_return_empty_mapping_for_empty_ids(
    session_factory,
):
    async with session_factory() as session:
        repository = SqlAlchemyCourseCatalogMetricsRepository(session)
        result = await repository.get_by_course_ids([])
        assert result == {}
