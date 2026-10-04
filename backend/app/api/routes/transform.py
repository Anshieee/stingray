from fastapi import APIRouter, HTTPException, status

from app.models.transform import TransformRequest, TransformResponse
from app.services.transform import UnsupportedTransformRequest, transform_request

router = APIRouter(tags=["transform"])


@router.post(
    "/transform",
    response_model=TransformResponse,
    status_code=status.HTTP_200_OK,
)
def transform(request: TransformRequest) -> TransformResponse:
    """Run the Phase 1 deterministic executive-summary integration stub."""
    try:
        return transform_request(request)
    except UnsupportedTransformRequest as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
