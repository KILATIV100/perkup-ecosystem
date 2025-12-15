"""Event service - business logic for event operations"""

from datetime import datetime
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventParticipant
from app.models.user import User


class EventError(Exception):
    """Custom exception for event errors"""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class EventService:
    """Service for event operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_events(
        self,
        status: str | None = None,
        event_type: str | None = None,
        featured_only: bool = False
    ) -> list[Event]:
        """Get events with filters"""
        query = select(Event)
        now = datetime.utcnow()

        if status == "active":
            query = query.where(
                Event.status == "active",
                Event.starts_at <= now,
                Event.ends_at >= now
            )
        elif status == "upcoming":
            query = query.where(
                Event.status == "active",
                Event.starts_at > now
            )
        elif status == "past":
            query = query.where(Event.ends_at < now)

        if event_type:
            query = query.where(Event.event_type == event_type)

        if featured_only:
            query = query.where(Event.is_featured == True)

        query = query.order_by(Event.starts_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_event_by_slug(self, slug: str) -> Event | None:
        """Get event by slug"""
        result = await self.db.execute(select(Event).where(Event.slug == slug))
        return result.scalar_one_or_none()

    async def get_event_by_id(self, event_id: UUID) -> Event | None:
        """Get event by ID"""
        result = await self.db.execute(select(Event).where(Event.id == event_id))
        return result.scalar_one_or_none()

    async def get_participation(
        self,
        event_id: UUID,
        user_id: int
    ) -> EventParticipant | None:
        """Get user's participation in an event"""
        result = await self.db.execute(
            select(EventParticipant).where(
                EventParticipant.event_id == event_id,
                EventParticipant.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def join_event(self, event: Event, user: User) -> EventParticipant:
        """Join an event"""
        # Check if event is active or upcoming
        now = datetime.utcnow()
        if event.status != "active":
            raise EventError("event_not_active", "Event is not active")

        if event.ends_at < now:
            raise EventError("event_ended", "Event has ended")

        # Check if user already joined
        existing = await self.get_participation(event.id, user.id)
        if existing:
            raise EventError("already_joined", "You have already joined this event")

        # Check max participants
        if event.max_participants and event.current_participants >= event.max_participants:
            raise EventError("event_full", "Event has reached maximum participants")

        # Check requirements
        if not await self._check_requirements(event, user):
            raise EventError(
                "requirements_not_met",
                "You don't meet the requirements to join this event"
            )

        # Create participation
        participant = EventParticipant(
            event_id=event.id,
            user_id=user.id,
        )
        self.db.add(participant)

        # Update event participant count
        event.current_participants += 1

        await self.db.flush()
        await self.db.refresh(participant)

        return participant

    async def _check_requirements(self, event: Event, user: User) -> bool:
        """Check if user meets event requirements"""
        requirements = event.requirements or {}

        # Check minimum level
        min_level = requirements.get("min_level")
        if min_level and user.level < min_level:
            return False

        # Check minimum checkins
        min_checkins = requirements.get("min_checkins")
        if min_checkins and user.total_checkins < min_checkins:
            return False

        # Add more requirement checks as needed

        return True

    async def update_progress(
        self,
        participant: EventParticipant,
        progress_update: dict
    ) -> EventParticipant:
        """Update participant's progress in an event"""
        # Merge progress
        current_progress = participant.progress or {}
        current_progress.update(progress_update)
        participant.progress = current_progress

        # Calculate progress percentage
        event = await self.get_event_by_id(participant.event_id)
        participant.progress_percentage = self._calculate_progress_percentage(
            event, current_progress
        )

        # Check if completed
        if participant.progress_percentage >= 100:
            participant.status = "completed"
            participant.completed_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(participant)

        return participant

    def _calculate_progress_percentage(self, event: Event, progress: dict) -> int:
        """Calculate progress percentage based on event requirements"""
        requirements = event.requirements or {}

        if not requirements:
            return 100  # No requirements means instant completion

        # Example: challenge with checkin requirements
        checkin_reqs = requirements.get("checkins", [])
        if checkin_reqs:
            completed = 0
            for req in checkin_reqs:
                location_progress = progress.get(f"location_{req['location_id']}", 0)
                if location_progress >= req.get("count", 1):
                    completed += 1
            return int((completed / len(checkin_reqs)) * 100)

        return 0

    async def claim_rewards(self, participant: EventParticipant) -> dict:
        """Claim rewards for completed event"""
        if participant.status != "completed":
            raise EventError("not_completed", "Event not completed yet")

        if participant.rewards_claimed:
            raise EventError("already_claimed", "Rewards already claimed")

        event = await self.get_event_by_id(participant.event_id)
        rewards = event.rewards or {}

        participant.rewards_claimed = True
        participant.rewards_claimed_at = datetime.utcnow()
        participant.status = "rewarded"

        await self.db.flush()

        return rewards
