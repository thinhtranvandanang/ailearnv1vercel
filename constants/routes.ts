
/**
 * ROUTES: Hệ thống đường dẫn tập trung của EduNexia
 */
export const ROUTES = {
  PUBLIC: {
    HOME: '/',
    LOGIN: '/login',
    REGISTER: '/register',
    CALLBACK: '/auth/callback',
  },
  PROTECTED: {
    DASHBOARD: '/dashboard',
    PRACTICE_SETUP: '/practice/setup',
    PRACTICE_TEST: '/practice/:testId',
    PRACTICE_OFFLINE: '/practice/:testId/offline',
    RESULT: '/results/:submissionId',
    SUGGESTIONS: '/results/:submissionId/suggestions',
  },
};
