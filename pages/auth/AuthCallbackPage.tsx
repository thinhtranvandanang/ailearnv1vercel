import React, { useEffect, useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.tsx';
import { ROUTES } from '../../constants/routes.ts';
import * as studentService from '../../services/student.service.ts';

/**
 * Trang xử lý callback sau khi Google OAuth thành công.
 * Nhiệm vụ: Hứng token, lưu trữ, xác minh thông tin tài khoản và điều hướng.
 */
export const AuthCallbackPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { setTokenManually } = useAuth();

    const [status, setStatus] = useState<'loading' | 'verifying' | 'error' | 'success'>('loading');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [debugLog, setDebugLog] = useState<string[]>([]);
    const initialized = useRef(false);

    const addLog = (msg: string) => {
        setDebugLog(prev => [...prev, `${new Date().toLocaleTimeString()}: ${msg}`]);
    };

    useEffect(() => {
        if (initialized.current) return;
        initialized.current = true;

        const processAuth = async () => {
            const params = new URLSearchParams(location.search);
            const token = params.get('token');
            const error = params.get('error');
            const details = params.get('details');
            const status_code = params.get('status');

            addLog(`Bắt đầu xử lý callback. URL: ${window.location.pathname}`);

            if (token) {
                addLog("Đã nhận được Token từ URL. Đang lưu trữ...");
                setStatus('loading');

                try {
                    // 1. Lưu token vào localStorage
                    setTokenManually(token);
                    addLog("Token đã được lưu vào Storage.");

                    // 2. Kiểm tra tính hợp lệ của Token ngay lập tức bằng Profile API
                    setStatus('verifying');
                    addLog("Đang xác thực Token với hệ thống Backend...");

                    const profileRes = await studentService.getMe();

                    if (profileRes.status === 'success') {
                        addLog(`Xác thực thành công! Xin chào ${profileRes.data?.full_name || 'bạn'}.`);
                        setStatus('success');

                        // Chuyển hướng sau 1 giây để người dùng kịp thấy trạng thái thành công
                        setTimeout(() => {
                            addLog("Đang chuyển hướng tới Dashboard...");
                            navigate(ROUTES.PROTECTED.DASHBOARD, { replace: true });
                        }, 1000);
                    } else {
                        throw new Error(profileRes.message || "Không thể lấy thông tin profile.");
                    }
                } catch (err: any) {
                    addLog(`Lỗi khi xác thực profile: ${err.message || 'Lỗi không xác định'}`);
                    setStatus('error');
                    setErrorMessage(`Xác thực thất bại: ${err.message || 'Vui lòng thử lại sau.'}`);
                }
            } else if (error) {
                addLog(`Lỗi nhận được từ Auth Provider: ${error} (${details || 'Không có chi tiết'})`);
                setStatus('error');
                setErrorMessage(`Lỗi đăng nhập Google: ${error}. ${details ? `Chi tiết: ${details}` : ''}`);
            } else {
                addLog("Không tìm thấy Token hoặc Lỗi trên URL.");
                setStatus('error');
                setErrorMessage("Không tìm thấy thông tin xác thực từ Google.");
            }
        };

        processAuth();
    }, [location, navigate, setTokenManually]);

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-xl w-full bg-white rounded-3xl shadow-2xl p-8 border border-slate-100 overflow-hidden">
                <div className="flex flex-col items-center text-center space-y-6">

                    {/* Trạng thái Loading / Verifying */}
                    {(status === 'loading' || status === 'verifying') && (
                        <>
                            <div className="relative">
                                <div className="w-20 h-20 border-4 border-slate-100 rounded-full"></div>
                                <div className="w-20 h-20 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin absolute top-0"></div>
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="w-2 h-2 bg-indigo-600 rounded-full animate-ping"></div>
                                </div>
                            </div>
                            <div>
                                <h1 className="text-2xl font-black text-slate-900 mb-2">
                                    {status === 'loading' ? 'Đang khởi tạo...' : 'Đang xác thực tài khoản...'}
                                </h1>
                                <p className="text-slate-500 font-medium">Vui lòng không đóng trình duyệt lúc này.</p>
                            </div>
                        </>
                    )}

                    {/* Trạng thái Success */}
                    {status === 'success' && (
                        <>
                            <div className="w-20 h-20 bg-green-50 text-green-500 rounded-full flex items-center justify-center shadow-inner">
                                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path>
                                </svg>
                            </div>
                            <div>
                                <h1 className="text-2xl font-black text-slate-900 mb-2">Đăng nhập thành công!</h1>
                                <p className="text-slate-500 font-medium italic">Chào mừng bạn quay trở lại EduNexia.</p>
                            </div>
                        </>
                    )}

                    {/* Trạng thái Error */}
                    {status === 'error' && (
                        <>
                            <div className="w-20 h-20 bg-red-50 text-red-500 rounded-full flex items-center justify-center shadow-inner font-black text-3xl">!</div>
                            <div>
                                <h1 className="text-2xl font-black text-slate-900 mb-2">Ôi! Có gì đó không đúng</h1>
                                <p className="text-red-500 font-bold mb-6 p-4 bg-red-50 rounded-2xl border border-red-100 italic">
                                    {errorMessage}
                                </p>
                                <div className="flex flex-col gap-3">
                                    <button
                                        onClick={() => navigate(ROUTES.PUBLIC.LOGIN)}
                                        className="px-8 py-3 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100"
                                    >
                                        Thử lại lần nữa
                                    </button>
                                    <button
                                        onClick={() => window.location.reload()}
                                        className="text-sm font-bold text-slate-400 hover:text-slate-600"
                                    >
                                        Tải lại trang
                                    </button>
                                </div>
                            </div>
                        </>
                    )}

                    {/* Diagnostic Log - Always visible for debugging during this phase */}
                    <div className="w-full pt-8 mt-6 border-t border-slate-50 text-left">
                        <div className="flex justify-between items-center mb-3">
                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none">Diagnostic Log</p>
                            <span className="text-[8px] px-2 py-1 bg-slate-100 text-slate-400 rounded-full font-bold">MODE: PRODUCTION_FIX_V4</span>
                        </div>
                        <div className="bg-slate-900 p-5 rounded-2xl text-[11px] font-mono text-indigo-300 break-all whitespace-pre-wrap shadow-inner max-h-48 overflow-y-auto border border-slate-800">
                            {debugLog.map((log, i) => (
                                <div key={i} className="mb-1 border-b border-slate-800/50 pb-1 last:border-0">{log}</div>
                            ))}
                            {status === 'loading' && <div className="animate-pulse">_</div>}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
