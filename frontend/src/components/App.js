import '../App.css';
import Navbar from './Navbar';
import UploadForm from './UploadForm';
import DataFetcher from './DataFetcher';

function App() {
  return (
    <div className="App">
      <Navbar />
      <h1>React and Flask Integration</h1>
      <UploadForm />
      <DataFetcher />
    </div>
  );
}

export default App;
