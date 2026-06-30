# app/services/dashboard_service.py

from app.models.interview import (
    Interview,
    InterviewStatus
)
from app.models.candidate import Candidate
from app.models.job_requisition import JobRequisition

from app.core.utils.pagination import build_paginated_response

async def get_dashboard_stats():

    total_interviews = (
        await Interview.find().count()
    )

    completed_interviews = (
        await Interview.find(
            {
                "status":
                    InterviewStatus.COMPLETED
            }
        ).count()
    )

    upcoming_interviews = (
        await Interview.find(
            {
                "status":
                    InterviewStatus.SCHEDULED
            }
        ).count()
    )

    total_candidates = (
        await Candidate.find().count()
    )

    return {
        "totalInterviews":
            total_interviews,

        "completedInterviews":
            completed_interviews,

        "upcomingInterviews":
            upcoming_interviews,

        "totalCandidates":
            total_candidates
    }

from datetime import datetime, timezone


async def get_upcoming_interviews():

    interviews = (
        await Interview.find(
            {
                "status":
                    InterviewStatus.SCHEDULED
            }
        )
        .sort(
            -Interview.scheduledAt
        )
        .limit(5)
        .to_list()
    )

    result = []

    for interview in interviews:

        candidate = await Candidate.get(
            interview.candidateId
        )

        requisition = (
            await JobRequisition.get(
                interview.jobRequisitionId
            )
        )

        result.append(
            {
                "interviewId":
                    str(interview.id),

                "candidateName":
                    candidate.name
                    if candidate
                    else "",

                "jobRole":
                    requisition.designation
                    if requisition
                    else "",

                "scheduledAt":
                    interview.scheduledAt,

                "interviewers": [],

                "type":
                    "Technical",

                "status":
                    interview.status
            }
        )

    return result

async def get_recent_interviews():

    interviews = (
        await Interview.find(
            {
                "status":
                    InterviewStatus.COMPLETED
            }
        )
        .sort(
            -Interview.completedAt
        )
        .limit(5)
        .to_list()
    )

    result = []

    for interview in interviews:

        candidate = await Candidate.get(
            interview.candidateId
        )

        requisition = (
            await JobRequisition.get(
                interview.jobRequisitionId
            )
        )

        duration = 0

        if (
            interview.startedAt
            and
            interview.completedAt
        ):
            duration = int(
                (
                    interview.completedAt
                    -
                    interview.startedAt
                ).total_seconds()
                / 60
            )

        result.append(
            {
                "interviewId":
                    str(interview.id),

                "candidateName":
                    candidate.name
                    if candidate
                    else "",

                "jobRole":
                    requisition.designation
                    if requisition
                    else "",

                "interviewDate":
                    interview.completedAt,

                "duration":
                    duration,

                "status":
                    interview.status,

                "overallScore":
                    interview.technicalScore
                    or 0
            }
        )

    return result

async def get_dashboard_service(
    current_user
):

    stats = await get_dashboard_stats()

    upcoming_interviews = (
        await get_upcoming_interviews()
    )

    recent_interviews = (
        await get_recent_interviews()
    )

    return {
        "stats": stats,
        "upcomingInterviews":
            upcoming_interviews,
        "recentInterviews":
            recent_interviews
    }

async def get_upcoming_interviews_service(
    pagination,
    current_user
):

    filters = {
        "status": InterviewStatus.SCHEDULED
    }

    total_records = await Interview.find(
        filters
    ).count()

    query = Interview.find(
        filters
    ).sort(
        Interview.scheduledAt
    )

    if pagination.page and pagination.page_size:
        query = (
            query
            .skip(pagination.skip)
            .limit(pagination.limit)
        )

    interviews = await query.to_list()

    candidate_ids = list({
        interview.candidateId
        for interview in interviews
    })

    requisition_ids = list({
        interview.jobRequisitionId
        for interview in interviews
    })

    candidates = await Candidate.find(
        {
            "_id": {
                "$in": candidate_ids
            }
        }
    ).to_list()

    requisitions = await JobRequisition.find(
        {
            "_id": {
                "$in": requisition_ids
            }
        }
    ).to_list()

    candidate_map = {
        str(candidate.id): candidate
        for candidate in candidates
    }

    requisition_map = {
        str(req.id): req
        for req in requisitions
    }

    records = []

    for interview in interviews:

        candidate = candidate_map.get(
            str(interview.candidateId)
        )

        requisition = requisition_map.get(
            str(interview.jobRequisitionId)
        )

        records.append(
            {
                "interviewId": str(interview.id),
                "candidateName": (
                    candidate.name
                    if candidate else ""
                ),
                "jobRole": (
                    requisition.designation
                    if requisition else ""
                ),
                "scheduledAt": interview.scheduledAt,
                "interviewers": [],
                "type": "Technical",
                "status": interview.status
            }
        )

    return build_paginated_response(
        records=records,
        page=pagination.page or 1,
        page_size=(
            pagination.page_size
            or total_records
            or 1
        ),
        total_records=total_records
    )

async def get_recent_interviews_service(
    pagination,
    current_user
):

    filters = {
        "status": InterviewStatus.COMPLETED
    }

    total_records = await Interview.find(
        filters
    ).count()

    query = (
        Interview.find(filters)
        .sort(-Interview.completedAt)
    )

    if pagination.page and pagination.page_size:
        query = (
            query
            .skip(pagination.skip)
            .limit(pagination.limit)
        )

    interviews = await query.to_list()

    candidate_ids = list({
        interview.candidateId
        for interview in interviews
    })

    requisition_ids = list({
        interview.jobRequisitionId
        for interview in interviews
    })

    candidates = await Candidate.find(
        {
            "_id": {
                "$in": candidate_ids
            }
        }
    ).to_list()

    requisitions = await JobRequisition.find(
        {
            "_id": {
                "$in": requisition_ids
            }
        }
    ).to_list()

    candidate_map = {
        str(candidate.id): candidate
        for candidate in candidates
    }

    requisition_map = {
        str(req.id): req
        for req in requisitions
    }

    records = []

    for interview in interviews:

        candidate = candidate_map.get(
            str(interview.candidateId)
        )

        requisition = requisition_map.get(
            str(interview.jobRequisitionId)
        )

        duration = 0

        if (
            interview.startedAt
            and interview.completedAt
        ):
            duration = int(
                (
                    interview.completedAt
                    - interview.startedAt
                ).total_seconds()
                / 60
            )

        records.append(
            {
                "interviewId": str(interview.id),
                "candidateName": (
                    candidate.name
                    if candidate else ""
                ),
                "jobRole": (
                    requisition.designation
                    if requisition else ""
                ),
                "interviewDate": interview.completedAt,
                "duration": duration,
                "status": interview.status,
                "overallScore": (
                    interview.technicalScore
                    or 0
                )
            }
        )

    return build_paginated_response(
        records=records,
        page=pagination.page or 1,
        page_size=(
            pagination.page_size
            or total_records
            or 1
        ),
        total_records=total_records
    )