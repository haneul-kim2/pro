# C:\pro\app\routers\meso_sales.py (수정 후 제안)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models # ✨ 상위 폴더 참조로 변경 ✨
from ..database import get_db # ✨ database 모듈에서 get_db 직접 import ✨

# ================== ✨ 라우터 객체 생성 (prefix 없이) ✨ ==================
router = APIRouter(
    # prefix는 main.py에서 /api/meso-sales 로 이미 적용됨
    tags=["Meso Sales API"]
)
# =======================================================================

@router.post("/", response_model=schemas.MesoSale, status_code=status.HTTP_201_CREATED)
async def create_new_meso_sale(
    meso_sale_data: schemas.MesoSaleCreate,
    db: Session = Depends(get_db)
):
    try:
        # crud.create_meso_sale 함수 사용 (crud.py 함수명 확인 필요)
        created_sale = crud.create_meso_sale(db=db, sale=meso_sale_data) # 파라미터명 sale로 변경
        return created_sale
    except Exception as e:
        print(f"Error creating meso sale: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메소 판매 기록 생성 중 내부 서버 오류 발생")
# === ✨ 새로운 API 라우트 추가 시작: 삭제 기능 ✨ ===

@router.delete("/{sale_id}", response_model=schemas.DeleteResponse, status_code=status.HTTP_200_OK)
async def delete_single_meso_sale(sale_id: int, db: Session = Depends(get_db)):
    success = crud.delete_meso_sale(db=db, log_id=sale_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 ID의 메소 판매 기록을 찾을 수 없습니다.")
    return schemas.DeleteResponse(message="메소 판매 기록이 성공적으로 삭제되었습니다.", deleted_id=sale_id)

@router.delete("/all/", response_model=schemas.DeleteResponse, status_code=status.HTTP_200_OK)
async def delete_all_meso_sale_records(db: Session = Depends(get_db)):
    num_deleted = crud.delete_all_meso_sales(db=db)
    return schemas.DeleteResponse(message=f"총 {num_deleted}개의 메소 판매 기록이 삭제되었습니다.", deleted_count=num_deleted)

# === ✨ 새로운 API 라우트 추가 끝 ✨ ===

@router.get("/", response_model=List[schemas.MesoSale])
async def read_all_meso_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # crud.get_meso_sales 함수 사용 (crud.py 함수명 확인 필요)
    sales = crud.get_meso_sales(db=db, skip=skip, limit=limit)
    return sales

@router.get("/{sale_id}", response_model=schemas.MesoSale)
async def read_single_meso_sale(sale_id: int, db: Session = Depends(get_db)):
    # crud.get_meso_sale 함수 사용 (crud.py 함수명 확인 필요)
    db_sale = crud.get_meso_sale(db=db, log_id=sale_id) # crud 함수 파라미터명 확인
    if db_sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 ID의 메소 판매 기록을 찾을 수 없습니다.")
    return db_sale