import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { queryClient } from './lib/queryClient'
import { ErrorBoundary } from './components/ErrorBoundary'
import { AppLayout } from './components/layout'
import { DashboardPage, PredictionsPage, PointsPage, PointDetailPage, PredictionDetailPage } from './pages'

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/predictions" element={<PredictionsPage />} />
              <Route path="/predictions/:predictionId" element={<PredictionDetailPage />} />
              <Route path="/points" element={<PointsPage />} />
              <Route path="/points/:pointId" element={<PointDetailPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            success: {
              style: {
                background: '#10B981',
                color: '#fff',
              },
            },
            error: {
              style: {
                background: '#EF4444',
                color: '#fff',
              },
              duration: 5000,
            },
          }}
        />
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
