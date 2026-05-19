import React, { useState } from 'react';
import './App.css';
import AlertQueue from './components/AlertQueue';
import CaseDetail from './components/CaseDetail';

function App() {
  const [view, setView] = useState('queue'); // 'queue' or 'detail'
  const [selectedAlert, setSelectedAlert] = useState(null);

  const handleViewCase = (alertId) => {
    setSelectedAlert({ id: alertId }); // In a real app, you'd fetch the full alert data
    setView('detail');
  };

  return (
    <div className="App">
      {view === 'queue' ? (
        <div className="alert-queue-view">
          {/* We'll pass the handleViewCase function to AlertQueue when we modify it next */}
          <AlertQueue onViewCase={handleViewCase} />
        </div>
      ) : (
        <CaseDetail 
          alertData={selectedAlert} 
          onBack={() => setView('queue')} 
        />
      )}
    </div>
  );
}

export default App;
