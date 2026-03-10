"""
Repository pattern for database operations using SQLAlchemy.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from .sa_models import (
    BondValuation,
    Portfolio,
    CalculationHistory,
    MarketDataDaily,
    FileRecord,
)
from .models import (
    BondValuationRecord,
    PortfolioRecord,
    CalculationHistory as CalculationHistorySchema,
    MarketDataDaily as MarketDataDailySchema,
    FileRecord as FileRecordSchema,
)


def _row_to_dict(row: Any) -> Dict[str, Any]:
    """Convert SQLAlchemy model instance to dict."""
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


class BondValuationRepository:
    """Repository for bond valuation records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, record: BondValuationRecord) -> Dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at", "updated_at"})
        row = BondValuation(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        row = await self.session.get(BondValuation, record_id)
        return _row_to_dict(row) if row else None

    async def get_by_secid(self, secid: str, limit: int = 10) -> List[Dict[str, Any]]:
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
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(BondValuation)
            .where(BondValuation.valuation_date >= start_date)
            .where(BondValuation.valuation_date <= end_date)
            .order_by(BondValuation.valuation_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]

    async def update(self, record_id: int, record: BondValuationRecord) -> Optional[Dict[str, Any]]:
        row = await self.session.get(BondValuation, record_id)
        if not row:
            return None
        data = record.model_dump(exclude={"id", "created_at"}, exclude_none=True)
        for key, value in data.items():
            setattr(row, key, value)
        row.updated_at = datetime.now(timezone.utc)
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

    async def create(self, record: PortfolioRecord) -> Dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at", "updated_at"})
        row = Portfolio(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        stmt = (
            select(Portfolio)
            .order_by(Portfolio.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]

    async def get_by_id(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        row = await self.session.get(Portfolio, portfolio_id)
        return _row_to_dict(row) if row else None


class CalculationHistoryRepository:
    """Repository for calculation history."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, record: CalculationHistorySchema) -> Dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at"})
        row = CalculationHistory(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_recent(
        self, calculation_type: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
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

    async def create_or_update(self, record: MarketDataDailySchema) -> Dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at"}, exclude_none=True)
        # Simple upsert: try to find existing, then update or create
        stmt = (
            select(MarketDataDaily)
            .where(MarketDataDaily.ticker == data["ticker"])
            .where(MarketDataDaily.data_type == data["data_type"])
            .where(MarketDataDaily.date == data["date"])
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
            await self.session.commit()
            await self.session.refresh(existing)
            return _row_to_dict(existing)

        row = MarketDataDaily(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_by_ticker(
        self,
        ticker: str,
        data_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
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
        self, ticker: str, data_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
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

    async def create(self, record: FileRecordSchema) -> Dict[str, Any]:
        data = record.model_dump(exclude={"id", "created_at", "updated_at"})
        row = FileRecord(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return _row_to_dict(row)

    async def get_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        row = await self.session.get(FileRecord, file_id)
        return _row_to_dict(row) if row else None

    async def get_by_type(self, file_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        stmt = (
            select(FileRecord)
            .where(FileRecord.file_type == file_type)
            .order_by(FileRecord.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [_row_to_dict(r) for r in result.scalars().all()]

    async def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
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
