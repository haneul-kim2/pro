# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional # List 추가

# 현재 폴더(routers)의 상위 폴더(app)에 있는 crud, schemas, database 모듈을 가져옴
# 가정: crud.py, schemas.py, database.py 파일이 app 폴더 바로 아래에 있음
from .. import crud, schemas, database

# APIRouter 인스턴스 생성
# 일반적으로 router 인스턴스는 각 파일에서 생성합니다.
router = APIRouter(
    prefix="/api/meso-sales", # API 경로 접두사 설정
    tags=["Meso Sales"],      # Swagger UI 태그 설정
    responses={404: {"description": "Not found"}}, # 공통 응답 설정 (선택적)
)

# =========================================
# Meso Sale API Endpoints
# =========================================

# --- 메소 판매 기록 생성 ---
@router.post("/", response_model=schemas.MesoSale, status_code=201) # response_model 수정
async def create_meso_sale_record(
    sale_data: schemas.MesoSaleCreate, # 타입 힌트 수정 및 변수명 변경
    db: Session = Depends(database.get_db)
):
    """
    새로운 메소 판매 기록을 생성합니다.

    - **sale_data**: 판매 정보를 담은 객체
        - **date**: 판매 날짜 (YYYY-MM-DD)
        - **price_per_1m**: 100만 메소당 가격 (원, 0보다 커야 함)
        - **quantity_millions**: 판매량 (단위: 100만 메소, 0보다 커야 함)
        - **total_krw**: 총 판매액 (원, 자동 계산되어 저장되지만, 생성 시점에는 클라이언트에서 계산하여 전달 필요)
    """
    # crud 함수 호출 시 파라미터 이름과 변수명 통일
    try:
        created_sale = crud.create_meso_sale(db=db, sale=sale_data)
        return created_sale
    except ValueError as ve: # crud 함수 내에서 발생 가능한 ValueError 처리 (예: 음수 값)
         raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # 더욱 구체적인 오류 로깅 및 처리가 필요할 수 있습니다.
        print(f"Error creating meso sale record: {e}") # 서버 로그에 오류 기록
        raise HTTPException(status_code=500, detail="메소 판매 기록 생성 중 서버 오류 발생")


# --- 메소 판매 기록 목록 조회 ---
@router.get("/", response_model=List[schemas.MesoSale]) # response_model 수정
async def read_meso_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    """
    메소 판매 기록 목록을 조회합니다. 페이징(skip, limit)을 지원합니다.
    """
    try:
        meso_sales = crud.get_meso_sales(db, skip=skip, limit=limit)
        return meso_sales
    except Exception as e:
        print(f"Error reading meso sales records: {e}")
        raise HTTPException(status_code=500, detail="메소 판매 기록 조회 중 서버 오류 발생")

# --- 특정 메소 판매 기록 조회 ---
@router.get("/{sale_id}", response_model=schemas.MesoSale)
async def read_meso_sale(sale_id: int, db: Session = Depends(database.get_db)):
    """
    주어진 ID에 해당하는 특정 메소 판매 기록을 조회합니다.
    """
    db_sale = crud.get_meso_sale(db, log_id=sale_id)
    if db_sale is None:
        raise HTTPException(status_code=404, detail="해당 ID의 메소 판매 기록을 찾을 수 없습니다.")
    return db_sale

# --- (선택적) 메소 판매 기록 수정 ---
# @router.put("/{sale_id}", response_model=schemas.MesoSale)
# async def update_meso_sale(...):
#     # TODO: 기록 수정 로직 구현
#     pass

# --- (선택적) 메소 판매 기록 삭제 ---
# @router.delete("/{sale_id}", status_code=204) # 204 No Content
# async def delete_meso_sale(...):
#     # TODO: 기록 삭제 로직 구현
#     pass