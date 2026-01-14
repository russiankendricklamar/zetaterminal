"""
API endpoints for database operations.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from src.database.repositories import (
    BondValuationRepository,
    PortfolioRepository,
    CalculationHistoryRepository,
    MarketDataRepository,
    FileRepository
)
from src.database.models import (
    BondValuationRecord,
    PortfolioRecord,
    CalculationHistory,
    MarketDataDaily,
    FileRecord
)
from src.database.storage import StorageService

router = APIRouter()


# Dependency injection for repositories
def get_bond_repo() -> BondValuationRepository:
    return BondValuationRepository()


def get_portfolio_repo() -> PortfolioRepository:
    return PortfolioRepository()


def get_history_repo() -> CalculationHistoryRepository:
    return CalculationHistoryRepository()


# Bond Valuation endpoints
@router.post("/bond-valuations", response_model=dict)
async def create_bond_valuation(
    record: BondValuationRecord,
    repo: BondValuationRepository = Depends(get_bond_repo)
):
    """Create a new bond valuation record."""
    try:
        result = repo.create(record)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bond-valuations/{record_id}", response_model=dict)
async def get_bond_valuation(
    record_id: int,
    repo: BondValuationRepository = Depends(get_bond_repo)
):
    """Get bond valuation by ID."""
    result = repo.get_by_id(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"success": True, "data": result}


@router.get("/bond-valuations", response_model=dict)
async def get_bond_valuations(
    secid: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    repo: BondValuationRepository = Depends(get_bond_repo)
):
    """Get bond valuations with optional filters."""
    try:
        if secid:
            results = repo.get_by_secid(secid, limit)
        elif start_date and end_date:
            results = repo.get_by_date_range(start_date, end_date, limit)
        else:
            # Get all recent records
            results = repo.get_by_date_range(
                (datetime.now().replace(day=1)).strftime("%Y-%m-%d"),
                datetime.now().strftime("%Y-%m-%d"),
                limit
            )
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bond-valuations/{record_id}", response_model=dict)
async def update_bond_valuation(
    record_id: int,
    record: BondValuationRecord,
    repo: BondValuationRepository = Depends(get_bond_repo)
):
    """Update bond valuation record."""
    result = repo.update(record_id, record)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"success": True, "data": result}


@router.delete("/bond-valuations/{record_id}", response_model=dict)
async def delete_bond_valuation(
    record_id: int,
    repo: BondValuationRepository = Depends(get_bond_repo)
):
    """Delete bond valuation record."""
    success = repo.delete(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"success": True, "message": "Record deleted"}


# Portfolio endpoints
@router.post("/portfolios", response_model=dict)
async def create_portfolio(
    record: PortfolioRecord,
    repo: PortfolioRepository = Depends(get_portfolio_repo)
):
    """Create a new portfolio record."""
    try:
        result = repo.create(record)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolios", response_model=dict)
async def get_portfolios(
    limit: int = 100,
    repo: PortfolioRepository = Depends(get_portfolio_repo)
):
    """Get all portfolios."""
    results = repo.get_all(limit)
    return {"success": True, "data": results, "count": len(results)}


@router.get("/portfolios/{portfolio_id}", response_model=dict)
async def get_portfolio(
    portfolio_id: int,
    repo: PortfolioRepository = Depends(get_portfolio_repo)
):
    """Get portfolio by ID."""
    result = repo.get_by_id(portfolio_id)
    if not result:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"success": True, "data": result}


# Calculation History endpoints
@router.post("/calculation-history", response_model=dict)
async def create_calculation_history(
    record: CalculationHistory,
    repo: CalculationHistoryRepository = Depends(get_history_repo)
):
    """Create a new calculation history record."""
    try:
        result = repo.create(record)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calculation-history", response_model=dict)
async def get_calculation_history(
    calculation_type: Optional[str] = None,
    limit: int = 50,
    repo: CalculationHistoryRepository = Depends(get_history_repo)
):
    """Get calculation history."""
    results = repo.get_recent(calculation_type, limit)
    return {"success": True, "data": results, "count": len(results)}


# Market Data endpoints
def get_market_repo() -> MarketDataRepository:
    return MarketDataRepository()


@router.get("/market-data", response_model=dict)
async def get_market_data(
    ticker: Optional[str] = None,
    data_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    repo: MarketDataRepository = Depends(get_market_repo)
):
    """Get market data."""
    if ticker:
        results = repo.get_by_ticker(ticker, data_type, start_date, end_date, limit)
    else:
        results = []
    return {"success": True, "data": results, "count": len(results)}


@router.post("/market-data/daily", response_model=dict)
async def create_market_data(
    record: MarketDataDaily,
    repo: MarketDataRepository = Depends(get_market_repo)
):
    """Create or update daily market data."""
    try:
        result = repo.create_or_update(record)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# File endpoints
def get_file_repo() -> FileRepository:
    return FileRepository()


@router.get("/files", response_model=dict)
async def get_files(
    file_type: Optional[str] = None,
    limit: int = 100,
    repo: FileRepository = Depends(get_file_repo)
):
    """Get files list."""
    if file_type:
        results = repo.get_by_type(file_type, limit)
    else:
        results = repo.get_all(limit)
    return {"success": True, "data": results, "count": len(results)}


@router.get("/files/{file_id}", response_model=dict)
async def get_file(
    file_id: int,
    repo: FileRepository = Depends(get_file_repo)
):
    """Get file metadata by ID."""
    result = repo.get_by_id(file_id)
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    return {"success": True, "data": result}


# Parquet Export endpoints
from src.database.parquet_export import ParquetExporter


@router.post("/export/market-data/parquet", response_model=dict)
async def export_market_data_parquet(
    ticker: Optional[str] = None,
    data_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    file_name: Optional[str] = None
):
    """Export market data to Parquet format."""
    try:
        exporter = ParquetExporter()
        result = exporter.export_market_data_to_parquet(
            ticker=ticker,
            data_type=data_type,
            start_date=start_date,
            end_date=end_date,
            file_name=file_name
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/table/{table_name}/parquet", response_model=dict)
async def export_table_parquet(
    table_name: str,
    file_name: Optional[str] = None
):
    """Export table to Parquet format."""
    try:
        exporter = ParquetExporter()
        result = exporter.export_table_to_parquet(
            table_name=table_name,
            file_name=file_name
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Registry export endpoints
class RegistryParquetRequest(BaseModel):
    registry_type: str
    data: List[dict]
    file_name: Optional[str] = None

@router.post("/export/registry/parquet", response_model=dict)
async def export_registry_parquet(
    request: RegistryParquetRequest
):
    """
    Export registry data to Parquet format and store in Supabase Storage.
    
    Args:
        request: Request body with registry_type, data, and optional file_name
    """
    registry_type = request.registry_type
    data = request.data
    file_name = request.file_name
    try:
        import pandas as pd
        from io import BytesIO
        from datetime import datetime
        
        if not data:
            raise ValueError("Registry data is empty")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Generate file name
        if not file_name:
            date_str = datetime.now().strftime("%Y%m%d")
            file_name = f"registry_{registry_type}_{date_str}.parquet"
        
        # Generate file path
        storage = StorageService()
        file_path = storage.generate_file_path("registers", file_name, "parquet")
        
        # Convert DataFrame to Parquet bytes
        buffer = BytesIO()
        df.to_parquet(
            buffer,
            engine='pyarrow',
            compression='snappy',
            index=False
        )
        buffer.seek(0)
        
        # Upload to Storage
        file_info = storage.upload_file(
            file_path=file_path,
            file_data=buffer,
            file_type="register",
            description=f"Registry export: {registry_type} ({len(data)} records)"
        )
        
        # Save metadata to database
        file_repo = FileRepository()
        file_record = FileRecord(
            file_name=file_name,
            file_path=file_path,
            file_type="register",
            file_size=file_info["size"],
            mime_type="application/octet-stream",
            description=f"Registry export: {registry_type} ({len(data)} records)",
            metadata={
                "registry_type": registry_type,
                "records_count": len(data),
                "format": "parquet",
                "compression": "snappy"
            }
        )
        file_repo.create(file_record)
        
        return {
            "success": True,
            "data": {
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_info["size"],
                "records_count": len(data),
                "url": file_info.get("url", "")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
