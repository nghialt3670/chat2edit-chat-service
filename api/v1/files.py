import traceback

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from database.services.file_service import FileService
from database.services.user_service import UserService
from dependencies.authorization import clerk_validate_user
from dependencies.database import get_file_service, get_user_service

router = APIRouter(prefix="/api/v1")


@router.get("/files/{file_id}", response_class=StreamingResponse)
async def get_file(
    file_id: str,
    user_service: UserService = Depends(get_user_service),
    file_service: FileService = Depends(get_file_service),
    clerk_user_id=Depends(clerk_validate_user),
):
    try:
        file_object = file_service.get(file_id)

        if file_object is None:
            raise HTTPException(404)

        user = user_service.find_by_clerk_user_id(clerk_user_id)
        if file_object.user_id != user.id:
            raise HTTPException(401)

        headers = {
            "Content-Disposition": f'attachment; filename="{file_object.filename}"'
        }
        return StreamingResponse(file_object, headers=headers)

    except HTTPException as e:
        raise e

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(500)
