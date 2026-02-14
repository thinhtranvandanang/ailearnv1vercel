from fastapi import APIRouter
from app.api.v1.endpoints import auth, auth_google, tests, submit, results, history

api_router = APIRouter()

# Đăng nhập truyền thống: /api/v1/auth/student/login
api_router.include_router(auth.router, prefix="/auth/student", tags=["Authentication"])

# Google OAuth: /api/v1/auth/google/login và /api/v1/auth/google/callback
api_router.include_router(auth_google.router, prefix="/auth", tags=["Google OAuth"])

api_router.include_router(tests.router, prefix="/practice-tests", tags=["Practice Tests"])
api_router.include_router(submit.router, prefix="/practice-tests", tags=["Submission"])
api_router.include_router(results.router, prefix="/submissions", tags=["Results & Suggestions"])
api_router.include_router(history.router, prefix="/students", tags=["Learning History"])