
import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.tsx';
import { Card, Button, Input, LoadingOverlay } from '../../components/common/UI.tsx';
import { ROUTES } from '../../constants/routes.ts';
import { GoogleLoginButton } from '../../components/auth/GoogleLoginButton.tsx';

export const LoginPage: React.FC = () => {
  const { login, isLoading, setTokenManually } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const [isVerifyingGoogle, setIsVerifyingGoogle] = useState(false);

  // Lấy và phân tích error từ URL
  const urlError = useMemo(() => {
    const params = new URLSearchParams(location.search);
    const errCode = params.get('error');
    if (!errCode) return null;

    switch (errCode) {
      case 'callback_failed': return 'Đồng bộ tài khoản thất bại. Vui lòng thử lại.';
      case 'access_denied': return 'Bạn đã hủy quyền đăng nhập Google.';
      case 'token_failed': return 'Không thể lấy mã xác thực từ Google.';
      case 'user_info_failed': return 'Không thể lấy thông tin cá nhân từ Google.';
      case 'email_missing': return 'Tài khoản Google của bạn thiếu thông tin Email.';
      default: return 'Đã có lỗi xảy ra trong quá trình đăng nhập.';
    }
  }, [location.search]);

  // Hiển thị lỗi từ URL nếu có
  useEffect(() => {
    if (urlError) setError(urlError);
  }, [urlError]);

  // Xử lý logic Google Redirect thành công
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const googleToken = params.get('token');

    if (googleToken) {
      setIsVerifyingGoogle(true);
      // setTokenManually is no longer strictly needed here as AuthContext handles it,
      // but we keep the visual feedback and navigate to dashboard.
      const timer = setTimeout(() => {
        navigate(ROUTES.PROTECTED.DASHBOARD, { replace: true });
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [location, navigate]);

  const handleLoginSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    const formData = new FormData(e.currentTarget);
    const username = formData.get('username') as string;
    const password = formData.get('password') as string;

    try {
      await login({ username, password });
      navigate(ROUTES.PROTECTED.DASHBOARD);
    } catch (err: any) {
      setError(err.message || 'Tên đăng nhập hoặc mật khẩu không chính xác.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4 selection:bg-indigo-100">
      {(isLoading || isVerifyingGoogle) && <LoadingOverlay />}

      <div className="w-full max-w-[440px] animate-in fade-in zoom-in duration-500">
        <div className="bg-white rounded-[2.5rem] shadow-2xl shadow-indigo-100/60 p-8 md:p-12 border border-slate-100">
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-indigo-600 rounded-3xl mb-6 shadow-xl shadow-indigo-200 rotate-3 transition-transform hover:rotate-0">
              <span className="text-4xl font-black text-white italic">E</span>
            </div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight">Mừng bạn trở lại!</h1>
            <p className="text-slate-500 font-medium mt-2">Đăng nhập để tiếp tục hành trình học tập.</p>
          </div>

          {isVerifyingGoogle ? (
            <div className="py-10 text-center space-y-4">
              <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-indigo-600 font-bold animate-pulse">Đang xác thực tài khoản Google...</p>
            </div>
          ) : (
            <div className="space-y-8">
              <GoogleLoginButton />

              <div className="flex items-center gap-4 py-1">
                <div className="flex-1 h-px bg-slate-100"></div>
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest px-2">Hoặc dùng tài khoản EduNexia</span>
                <div className="flex-1 h-px bg-slate-100"></div>
              </div>

              <form onSubmit={handleLoginSubmit} className="space-y-5">
                <div className="space-y-4">
                  <Input
                    name="username"
                    label="Tên đăng nhập"
                    placeholder="Nhập username"
                    required
                    className="rounded-2xl border-slate-200 focus:border-indigo-500 h-13 transition-all"
                  />
                  <div className="relative">
                    <Input
                      name="password"
                      label="Mật khẩu"
                      type="password"
                      placeholder="••••••••"
                      required
                      className="rounded-2xl border-slate-200 focus:border-indigo-500 h-13 transition-all"
                    />
                    <div className="flex justify-end mt-1.5">
                      <button type="button" className="text-xs font-bold text-indigo-600 hover:text-indigo-700">Quên mật khẩu?</button>
                    </div>
                  </div>
                </div>

                {error && (
                  <div className="p-4 bg-red-50 text-red-600 text-[13px] font-bold rounded-2xl border border-red-100 flex items-center gap-3 animate-in slide-in-from-top-2 duration-300">
                    <span className="w-5 h-5 bg-red-100 rounded-full flex items-center justify-center text-xs">!</span>
                    {error}
                  </div>
                )}

                <Button
                  type="submit"
                  isLoading={isLoading}
                  className="w-full h-14 rounded-2xl font-black text-lg shadow-xl shadow-indigo-100 transition-all hover:translate-y-[-2px] active:scale-[0.98]"
                >
                  Đăng nhập ngay
                </Button>
              </form>

              <div className="text-center pt-2">
                <p className="text-sm text-slate-500 font-medium">
                  Chưa có tài khoản? <Link to={ROUTES.PUBLIC.REGISTER} className="font-extrabold text-indigo-600 hover:text-indigo-700 underline underline-offset-4 decoration-2">Tham gia miễn phí</Link>
                </p>
              </div>

              {/* Debug Info Section - Helpful for troubleshooting production redirect issues */}
              {(new URLSearchParams(location.search).has('token') || new URLSearchParams(location.search).has('error')) && (
                <div className="mt-8 p-4 bg-slate-100 rounded-2xl text-[10px] font-mono text-slate-500 break-all border border-slate-200">
                  <p className="font-bold mb-1 uppercase tracking-tighter opacity-50">Debug Session Info:</p>
                  <p>URL: {window.location.href.split('?')[0]}</p>
                  <p>Params: {location.search || 'None'}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
