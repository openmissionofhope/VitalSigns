import { Routes, Route } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { RegionDetail } from './pages/RegionDetail';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/regions/:code" element={<RegionDetail />} />
    </Routes>
  );
}

export default App;
