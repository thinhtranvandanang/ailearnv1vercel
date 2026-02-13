import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext.tsx';
import { ProtectedRoute } from './components/ProtectedRoute.tsx';
import { ROUTES } from './constants/routes.ts';

// Import Pages với đuôi .tsx để Native ESM hoạt động ổn định
import { LandingPage } from './pages/public/LandingPage.tsx';
import { LoginPage } from './pages/auth/LoginPage.tsx';
import { RegisterPage } from './pages/auth/RegisterPage.tsx';
import { AuthCallbackPage } from './pages/auth/AuthCallbackPage.tsx';
import { DashboardPage } from './pages/student/DashboardPage.tsx';
import { CreateTestPage } from './pages/student/CreateTestPage.tsx';
import { TakeTestPage } from './pages/student/TakeTestPage.tsx';
import { OfflineSubmissionPage } from './pages/student/OfflineSubmissionPage.tsx';
import { ResultPage } from './pages/student/ResultPage.tsx';
import { SuggestionsPage } from './pages/student/SuggestionsPage.tsx';

const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col antialiased text-slate-900">
      <nav className="bg-white/80 backdrop-blur-md border-b border-slate-100 sticky top-0 z-50 h-16 flex items-center">
        <div className="max-w-7xl mx-auto px-4 w-full flex justify-between items-center">
          <div
            className="flex items-center gap-2 cursor-pointer group"
            onClick={() => navigate(ROUTES.PROTECTED.DASHBOARD)}
          >
            <div className="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center font-black text-white italic group-hover:rotate-6 transition-transform shadow-lg shadow-indigo-100">E</div>
            <span className="text-xl font-black text-indigo-600 italic tracking-tighter uppercase select-none">EduNexia</span>
          </div>

          <div className="flex items-center gap-5">
            <div className="hidden sm:block text-right">
              <p className="text-sm font-black text-slate-900 leading-none mb-1">{user?.full_name || 'Học sinh'}</p>
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em]">Student Account</p>
            </div>
            <button
              onClick={logout}
              className="p-2.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all border border-transparent hover:border-red-100"
              title="Đăng xuất"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
              </svg>
            </button>
          </div>
        </div>
      </nav>
      <main className="flex-1">{children}</main>
    </div>
  );
};

const AppRoutes: React.FC = () => {
  const { token } = useAuth();

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path={ROUTES.PUBLIC.LOGIN} element={<LoginPage />} />
      <Route path={ROUTES.PUBLIC.REGISTER} element={<RegisterPage />} />
      <Route path={ROUTES.PUBLIC.CALLBACK} element={<AuthCallbackPage />} />

      <Route path={ROUTES.PROTECTED.DASHBOARD} element={<ProtectedRoute><MainLayout><DashboardPage /></MainLayout></ProtectedRoute>} />
      <Route path={ROUTES.PROTECTED.PRACTICE_SETUP} element={<ProtectedRoute><MainLayout><CreateTestPage /></MainLayout></ProtectedRoute>} />
      <Route path={ROUTES.PROTECTED.PRACTICE_TEST} element={<ProtectedRoute><TakeTestPage /></ProtectedRoute>} />
      <Route path={ROUTES.PROTECTED.PRACTICE_OFFLINE} element={<ProtectedRoute><MainLayout><OfflineSubmissionPage /></MainLayout></ProtectedRoute>} />
      <Route path={ROUTES.PROTECTED.RESULT} element={<ProtectedRoute><MainLayout><ResultPage /></MainLayout></ProtectedRoute>} />
      <Route path={ROUTES.PROTECTED.SUGGESTIONS} element={<ProtectedRoute><MainLayout><SuggestionsPage /></MainLayout></ProtectedRoute>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const App: React.FC = () => (
  <AuthProvider>
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  </AuthProvider>
);

export default App;