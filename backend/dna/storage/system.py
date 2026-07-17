import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid

from dna.storage.db import (
    get_db_session, RepositoryModel, SettingModel, NotificationModel,
    ReviewModel, RefactoringPipelineModel, OrganizationTeamModel
)

class SystemDB:
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self._session = None

    def open(self):
        self._session = get_db_session()
        return self

    def close(self):
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and self._session:
            self._session.rollback()
        self.close()

    # Repositories
    def add_repository(self, path: str, name: str, total_files: int, source_files: int, commits: int, risk_score: float):
        now = datetime.now(timezone.utc).isoformat()
        # Find if repository exists
        repo = self._session.query(RepositoryModel).filter_by(path=path).first()
        if not repo:
            repo = RepositoryModel(uid=str(uuid.uuid4()), path=path)
        
        repo.name = name
        repo.analyzed_at = now
        repo.total_files = total_files
        repo.source_files = source_files
        repo.commits = commits
        repo.risk_score = risk_score
        
        self._session.add(repo)
        self._session.commit()

    def get_repositories(self) -> List[Dict[str, Any]]:
        repos = self._session.query(RepositoryModel).order_by(RepositoryModel.analyzed_at.desc()).all()
        return [
            {
                "path": r.path,
                "name": r.name,
                "analyzed_at": r.analyzed_at,
                "total_files": r.total_files,
                "source_files": r.source_files,
                "commits": r.commits,
                "risk_score": r.risk_score
            }
            for r in repos
        ]

    # Settings
    def set_setting(self, key: str, value: str):
        setting = self._session.query(SettingModel).filter_by(key=key).first()
        if not setting:
            setting = SettingModel(key=key)
        setting.value = value
        self._session.add(setting)
        self._session.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        setting = self._session.query(SettingModel).filter_by(key=key).first()
        return setting.value if setting else default

    def get_all_settings(self) -> Dict[str, str]:
        settings = self._session.query(SettingModel).all()
        return {s.key: s.value for s in settings}

    # Notifications
    def add_notification(self, title: str, message: str, type_: str = "info") -> str:
        nid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        notif = NotificationModel(
            id=nid,
            title=title,
            message=message,
            type=type_,
            read=False,
            timestamp=now
        )
        self._session.add(notif)
        self._session.commit()
        return nid

    def get_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        query = self._session.query(NotificationModel)
        if unread_only:
            query = query.filter_by(read=False)
        notifications = query.order_by(NotificationModel.timestamp.desc()).all()
        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "read": n.read,
                "timestamp": n.timestamp
            }
            for n in notifications
        ]

    def mark_notification_read(self, nid: str):
        notif = self._session.query(NotificationModel).filter_by(id=nid).first()
        if notif:
            notif.read = True
            self._session.commit()

    def mark_all_notifications_read(self):
        self._session.query(NotificationModel).update({NotificationModel.read: True})
        self._session.commit()

    def delete_notification(self, nid: str):
        notif = self._session.query(NotificationModel).filter_by(id=nid).first()
        if notif:
            self._session.delete(notif)
            self._session.commit()

    # Reviews
    def create_review(self, title: str, description: str, repo_path: str, assignees: list, files: list) -> str:
        rid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        review = ReviewModel(
            id=rid,
            title=title,
            description=description,
            repo_path=repo_path,
            status="open",
            assignees_json=json.dumps(assignees),
            files_json=json.dumps(files),
            comments_json="[]",
            created_at=now
        )
        self._session.add(review)
        self._session.commit()
        return rid

    def get_reviews(self) -> List[Dict[str, Any]]:
        reviews = self._session.query(ReviewModel).order_by(ReviewModel.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "repo_path": r.repo_path,
                "status": r.status,
                "assignees": json.loads(r.assignees_json),
                "files": json.loads(r.files_json),
                "comments": json.loads(r.comments_json),
                "created_at": r.created_at
            }
            for r in reviews
        ]

    def get_review(self, rid: str) -> Optional[Dict[str, Any]]:
        r = self._session.query(ReviewModel).filter_by(id=rid).first()
        if not r:
            return None
        return {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "repo_path": r.repo_path,
            "status": r.status,
            "assignees": json.loads(r.assignees_json),
            "files": json.loads(r.files_json),
            "comments": json.loads(r.comments_json),
            "created_at": r.created_at
        }

    def update_review_status(self, rid: str, status: str):
        review = self._session.query(ReviewModel).filter_by(id=rid).first()
        if review:
            review.status = status
            self._session.commit()

    def add_review_comment(self, rid: str, comment: dict) -> bool:
        review = self._session.query(ReviewModel).filter_by(id=rid).first()
        if not review:
            return False
        
        comments = json.loads(review.comments_json)
        comments.append({
            "id": len(comments) + 1,
            "author": comment.get("author", "User"),
            "text": comment.get("text", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "file_path": comment.get("file_path"),
            "line": comment.get("line")
        })
        review.comments_json = json.dumps(comments)
        self._session.commit()
        return True

    # Refactoring Pipelines
    def create_pipeline(self, name: str, description: str, tasks: list, impact_report: dict) -> str:
        pid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        pipeline = RefactoringPipelineModel(
            id=pid,
            name=name,
            description=description,
            status="pending",
            tasks_json=json.dumps(tasks),
            impact_report_json=json.dumps(impact_report),
            execution_history_json="[]",
            created_at=now
        )
        self._session.add(pipeline)
        self._session.commit()
        return pid

    def get_pipelines(self) -> List[Dict[str, Any]]:
        pipelines = self._session.query(RefactoringPipelineModel).order_by(RefactoringPipelineModel.created_at.desc()).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "status": p.status,
                "tasks": json.loads(p.tasks_json),
                "impact_report": json.loads(p.impact_report_json),
                "execution_history": json.loads(p.execution_history_json),
                "created_at": p.created_at
            }
            for p in pipelines
        ]

    def get_pipeline(self, pid: str) -> Optional[Dict[str, Any]]:
        p = self._session.query(RefactoringPipelineModel).filter_by(id=pid).first()
        if not p:
            return None
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "status": p.status,
            "tasks": json.loads(p.tasks_json),
            "impact_report": json.loads(p.impact_report_json),
            "execution_history": json.loads(p.execution_history_json),
            "created_at": p.created_at
        }

    def update_pipeline_status(self, pid: str, status: str):
        p = self._session.query(RefactoringPipelineModel).filter_by(id=pid).first()
        if p:
            p.status = status
            self._session.commit()

    def run_pipeline_step(self, pid: str, step_index: int, status: str, log_message: str) -> bool:
        p = self._session.query(RefactoringPipelineModel).filter_by(id=pid).first()
        if not p:
            return False
        
        tasks = json.loads(p.tasks_json)
        if 0 <= step_index < len(tasks):
            tasks[step_index]["status"] = status
            tasks[step_index]["log"] = log_message
        
        history = json.loads(p.execution_history_json)
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": f"Step {step_index} ('{tasks[step_index]['name'] if step_index < len(tasks) else ''}') updated to {status}",
            "log": log_message
        })
        
        # Calculate overall status
        all_done = all(t.get("status") == "success" for t in tasks)
        any_failed = any(t.get("status") == "failed" for t in tasks)
        
        overall_status = "running"
        if all_done:
            overall_status = "success"
        elif any_failed:
            overall_status = "failed"
            
        p.tasks_json = json.dumps(tasks)
        p.status = overall_status
        p.execution_history_json = json.dumps(history)
        self._session.commit()
        return True

    # Teams / Organization
    def get_teams(self) -> List[Dict[str, Any]]:
        teams = self._session.query(OrganizationTeamModel).all()
        if not teams:
            self.seed_default_teams()
            teams = self._session.query(OrganizationTeamModel).all()
        return [
            {
                "id": t.id,
                "name": t.name,
                "role": t.role,
                "members": json.loads(t.members_json)
            }
            for t in teams
        ]

    def seed_default_teams(self):
        teams = [
            OrganizationTeamModel(
                id="team-1",
                name="Platform Engineering",
                role="Architectural Governance",
                members_json=json.dumps([
                    {"name": "Alice Johnson", "role": "Lead Architect", "email": "alice@company.com"},
                    {"name": "Bob Smith", "role": "Senior Dev", "email": "bob@company.com"}
                ])
            ),
            OrganizationTeamModel(
                id="team-2",
                name="Security & Quality",
                role="Risk Management & Compliance",
                members_json=json.dumps([
                    {"name": "Charlie Brown", "role": "Security Specialist", "email": "charlie@company.com"},
                    {"name": "David Miller", "role": "QA Lead", "email": "david@company.com"}
                ])
            )
        ]
        for t in teams:
            self._session.merge(t)
        self._session.commit()

    def update_team(self, team_id: str, name: str, role: str, members: list):
        team = self._session.query(OrganizationTeamModel).filter_by(id=team_id).first()
        if not team:
            team = OrganizationTeamModel(id=team_id)
        team.name = name
        team.role = role
        team.members_json = json.dumps(members)
        self._session.merge(team)
        self._session.commit()

    def delete_team(self, team_id: str):
        team = self._session.query(OrganizationTeamModel).filter_by(id=team_id).first()
        if team:
            self._session.delete(team)
            self._session.commit()
