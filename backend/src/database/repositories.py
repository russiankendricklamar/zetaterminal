"""
Repository pattern for database operations using SQLAlchemy.
"""
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    BondValuationRecord,
    PortfolioRecord,
)
from .models import (
    CalculationHistory as CalculationHistorySchema,
)
from .models import (
    FileRecord as FileRecordSchema,
)
from .models import (
    MarketDataDaily as MarketDataDailySchema,
)
from .sa_models import (
    BondValuation,
    CalculationHistory,
    FileRecord,
    MarketDataDaily,
    Portfolio,
)


def _row_to_dict(row: Any) -> dict[str, Any]:
    """Convert SQLAlchemy model instance to dict."""
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


class BondValuationRepository:
    """Repository for bond valuation records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, record: BondValuationRecord) -> dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at", "updated_at"})
        row = BondValuation(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_by_id(self, record_id: int) -> dict[str, Any] | None:
        row = await self.session.get(BondValuation, record_id)
        return _row_to_dict(row) if row else None

    async def get_by_secid(self, secid: str, limit: int = 10) -> list[dict[str, Any]]:
        stmt = (
            select(BondValuation)
            .where(BondValuation.secid == secid)
            .order_by(BondValuation.valuation_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]

    async def get_by_date_range(
        self, start_date: str, end_date: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        stmt = (
            select(BondValuation)
            .where(BondValuation.valuation_date >= start_date)
            .where(BondValuation.valuation_date <= end_date)
            .order_by(BondValuation.valuation_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]

    async def update(self, record_id: int, record: BondValuationRecord) -> dict[str, Any] | None:
        row = await self.session.get(BondValuation, record_id)
        if not row:
            return None
        data = record.model_dump(exclude={"id", "created_at"}, exclude_none=True)
        for key, value in data.items():
            setattr(row, key, value)
        row.updated_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def delete(self, record_id: int) -> bool:
        row = await self.session.get(BondValuation, record_id)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.commit()
        return True


class PortfolioRepository:
    """Repository for portfolio records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, record: PortfolioRecord) -> dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at", "updated_at"})
        row = Portfolio(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_all(self, limit: int = 100) -> list[dict[str, Any]]:
        stmt = (
            select(Portfolio)
            .order_by(Portfolio.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]

    async def get_by_id(self, portfolio_id: int) -> dict[str, Any] | None:
        row = await self.session.get(Portfolio, portfolio_id)
        return _row_to_dict(row) if row else None


class CalculationHistoryRepository:
    """Repository for calculation history."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, record: CalculationHistorySchema) -> dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at"})
        row = CalculationHistory(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_recent(
        self, calculation_type: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        stmt = select(CalculationHistory)
        if calculation_type:
            stmt = stmt.where(CalculationHistory.calculation_type == calculation_type)
        stmt = stmt.order_by(CalculationHistory.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]


class MarketDataRepository:
    """Repository for market data."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_or_update(self, record: MarketDataDailySchema) -> dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at"}, exclude_none=True)
        # Atomic upsert via INSERT ... ON CONFLICT DO UPDATE
        stmt = pg_insert(MarketDataDaily).values(**data)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_market_data_ticker_type_date",
            set_={k: stmt.excluded[k] for k in data if k not in ("ticker", "data_type", "date")},
        ).returning(MarketDataDaily)
        result = await self.session.execute(stmt)
        row = result.scalar_one()
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_by_ticker(
        self,
        ticker: str,
        data_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        stmt = select(MarketDataDaily).where(MarketDataDaily.ticker == ticker)
        if data_type:
            stmt = stmt.where(MarketDataDaily.data_type == data_type)
        if start_date:
            stmt = stmt.where(MarketDataDaily.date >= start_date)
        if end_date:
            stmt = stmt.where(MarketDataDaily.date <= end_date)
        stmt = stmt.order_by(MarketDataDaily.date.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]

    async def get_latest(
        self, ticker: str, data_type: str | None = None
    ) -> dict[str, Any] | None:
        stmt = select(MarketDataDaily).where(MarketDataDaily.ticker == ticker)
        if data_type:
            stmt = stmt.where(MarketDataDaily.data_type == data_type)
        stmt = stmt.order_by(MarketDataDaily.date.desc()).limit(1)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return _row_to_dict(row) if row else None


class FileRepository:
    """Repository for file metadata."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, record: FileRecordSchema) -> dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at", "updated_at"})
        row = FileRecord(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_by_id(self, file_id: int) -> dict[str, Any] | None:
        row = await self.session.get(FileRecord, file_id)
        return _row_to_dict(row) if row else None

    async def get_by_type(self, file_type: str, limit: int = 100) -> list[dict[str, Any]]:
        stmt = (
            select(FileRecord)
            .where(FileRecord.file_type == file_type)
            .order_by(FileRecord.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]

    async def get_all(self, limit: int = 100) -> list[dict[str, Any]]:
        stmt = select(FileRecord).order_by(FileRecord.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]

    async def delete(self, file_id: int) -> bool:
        row = await self.session.get(FileRecord, file_id)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.commit()
        return True
