import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.tsx';
import { ROUTES } from '../../constants/routes.ts';

export const AuthCallbackPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { setTokenManually } = useAuth();
    const [status, setStatus] = useState<'loading' | 'error' | 'success'>('loading');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [debugInfo, setDebugInfo] = useState<string>('');

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const token = params.get('token');
        const error = params.get('error');
        const details = params.get('details');
        const status_code = params.get('status');

        setDebugInfo(JSON.stringify({
            has_token: !!token,
            error,
            details,
            status_code,
            full_url: window.location.href
        }, null, 2));

        if (token) {
            console.log("AuthCallback: Token received, storing...");
            setStatus('loading');

            // Store token
            setTokenManually(token);

            // Delay slightly to ensure storage is persistent and state updates
            const timer = setTimeout(() => {
                setStatus('success');
                navigate(ROUTES.PROTECTED.DASHBOARD, { replace: true });
            }, 1500);

            return () => clearTimeout(timer);
        } else if (error) {
            console.error("AuthCallback: Error received", error, details);
            setStatus('error');
            setErrorMessage(`${error}${details ? `: ${details}` : ''}${status_code ? ` (Status: ${status_code})` : ''}`);

            // Redirect to login after a delay so they can see the error
            const timer = setTimeout(() => {
                navigate(`${ROUTES.PUBLIC.LOGIN}?error=${error}&details=${details || ''}`, { replace: true });
            }, 5000);

            return () => clearTimeout(timer);
        } else {
            // No token and no error? Unexpected state.
            setStatus('error');
            setErrorMessage("Không tìm thấy thông tin xác thực.");
            setTimeout(() => navigate(ROUTES.PUBLIC.LOGIN, { replace: true }), 3000);
        }
    }, [location, navigate, setTokenManually]);

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full bg-white rounded-3xl shadow-xl p-8 border border-slate-100">
                <div className="flex flex-col items-center text-center space-y-6">
                    {status === 'loading' && (
                        <>
                            <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                            <div>
                                <h1 className="text-2xl font-black text-slate-900 mb-2">Đang xác thực...</h1>
                                <p className="text-slate-500 font-medium">Vui lòng đợi trong giây lát khi chúng tôi thiết lập tài khoản của bạn.</p>
                            </div>
                        </>
                    )}

                    {status === 'success' && (
                        <>
                            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center">
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path>
                                </svg>
                            </div>
                            <div>
                                <h1 className="text-2xl font-black text-slate-900 mb-2">Thành công!</h1>
                                <p className="text-slate-500 font-medium">Đang chuyển hướng bạn tới bảng điều khiển...</p>
                            </div>
                        </>
                    )}

                    {status === 'error' && (
                        <>
                            <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center">
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </div>
                            <div>
                                <h1 className="text-2xl font-black text-slate-900 mb-2">Đăng nhập thất bại</h1>
                                <p className="text-red-500 font-bold mb-4">{errorMessage}</p>
                                <button
                                    onClick={() => navigate(ROUTES.PUBLIC.LOGIN)}
                                    className="px-6 py-2 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-colors"
                                >
                                    Quay lại đăng nhập
                                </button>
                            </div>
                        </>
                    )}

                    <div className="w-full pt-8 mt-8 border-t border-slate-100 text-left">
                        <p className="text-[10px] font-mono text-slate-400 uppercase tracking-widest mb-2 font-bold opacity-50">Diagnostic Data</p>
                        <pre className="bg-slate-50 p-4 rounded-2xl text-[10px] font-mono text-slate-500 break-all whitespace-pre-wrap border border-slate-100 overflow-x-auto">
                            {debugInfo}
                        </pre>
                    </div>
                </div>
            </div>
        </div>
    );
};
