from fastapi import APIRouter, HTTPException
from app.models.travel import ServiceSearch
from app.services.search_service import EnhancedSearchTools

router = APIRouter()
search_tools = EnhancedSearchTools()

@router.post("/flights/search")
async def search_flights(search_data: ServiceSearch):
    try:
        results = search_tools.search_flights(
            search_data.departure,
            search_data.destination,
            search_data.date
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")

@router.post("/hotels/search")
async def search_hotels(search_data: ServiceSearch):
    try:
        results = search_tools.search_hotels(
            search_data.destination,
            search_data.area,
            search_data.checkin,
            search_data.checkout
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotel search failed: {str(e)}")

@router.post("/transport/search")
async def search_transportation(search_data: ServiceSearch):
    try:
        # Search all transport types
        results = {}
        
        # Search trains
        train_results = search_tools.search_trains(
            search_data.departure,
            search_data.destination,
            search_data.date
        )
        results['trains'] = train_results
        
        # Search buses
        bus_results = search_tools.search_buses(
            search_data.departure,
            search_data.destination,
            search_data.date
        )
        results['buses'] = bus_results
        
        # Search cabs
        cab_results = search_tools.search_intercity_cab(
            search_data.departure,
            search_data.destination,
            search_data.date
        )
        results['cabs'] = cab_results
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transport search failed: {str(e)}")