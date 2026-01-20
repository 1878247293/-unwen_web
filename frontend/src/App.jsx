import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Loading from './components/Loading'
import RouteLoader from './components/RouteLoader'
import './App.css'

// 同步导入高频访问的页面（首屏和常用页面）
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Papers from './pages/Papers'
import PaperDetail from './pages/PaperDetail'
import NotFound from './pages/NotFound'

// 懒加载低频访问的页面（代码分割）
const AddPaper = lazy(() => import('./pages/AddPaper'))
const EditPaper = lazy(() => import('./pages/EditPaper'))
const Tags = lazy(() => import('./pages/Tags'))
const Profile = lazy(() => import('./pages/Profile'))
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))
const UserManagement = lazy(() => import('./pages/UserManagement'))
const Suggestions = lazy(() => import('./pages/Suggestions'))
const Notifications = lazy(() => import('./pages/Notifications'))
const Ideas = lazy(() => import('./pages/Ideas'))
const Websites = lazy(() => import('./pages/Websites'))
const Community = lazy(() => import('./pages/Community'))
const SystemMonitor = lazy(() => import('./pages/SystemMonitor'))

function PrivateRoute({ children }) {
  const { token } = useAuthStore()
  return token ? children : <Navigate to="/login" />
}

function App() {
  return (
    <Suspense fallback={<Loading fullScreen tip="页面加载中..." />}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route path="/" element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="papers" element={<Papers />} />
          <Route path="papers/add" element={<RouteLoader><AddPaper /></RouteLoader>} />
          <Route path="papers/:id" element={<PaperDetail />} />
          <Route path="papers/:id/edit" element={<RouteLoader><EditPaper /></RouteLoader>} />
          <Route path="tags" element={<RouteLoader><Tags /></RouteLoader>} />
          <Route path="suggestions" element={<RouteLoader><Suggestions /></RouteLoader>} />
          <Route path="notifications" element={<RouteLoader><Notifications /></RouteLoader>} />
          <Route path="ideas" element={<RouteLoader><Ideas /></RouteLoader>} />
          <Route path="websites" element={<RouteLoader><Websites /></RouteLoader>} />
          <Route path="community" element={<RouteLoader><Community /></RouteLoader>} />
          <Route path="profile" element={<RouteLoader><Profile /></RouteLoader>} />
          <Route path="admin/dashboard" element={<RouteLoader><AdminDashboard /></RouteLoader>} />
          <Route path="admin/users" element={<RouteLoader><UserManagement /></RouteLoader>} />
          <Route path="admin/system" element={<RouteLoader><SystemMonitor /></RouteLoader>} />
        </Route>

        {/* 404 页面 - 捕获所有未匹配的路由 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  )
}

export default App
