import React, { useState } from 'react';
import { uploadImage } from '../api';

function UploadForm() {
  const [file, setFile] = useState(null); // Store the file object
  const [fileName, setFileName] = useState('No file chosen'); // Store the file name
  const [result, setResult] = useState(null);

  const handleFileChange = (event) => {
    if (event.target.files.length > 0) {
      const selectedFile = event.target.files[0];
      setFile(selectedFile); // Set the file object
      setFileName(selectedFile.name); // Set the file name
    } else {
      setFile(null);
      setFileName('No file chosen');
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (file) {
      try {
        const response = await uploadImage(file); 
        if (response.top_predictions && response.top_predictions.length > 0) {
          const topLabels = response.top_predictions.map(prediction => prediction.label.split("_").join(" "));
          console.log(topLabels, "Top Predictions CHECK!");
          setResult(topLabels); 
      } else {
          console.error("No predictions found in the response.");
          setResult(["Prediction not available"]);
      }
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div className="flex flex-col items-center justify-center h-screen">
          {/* Hidden file input */}
          <input 
            type="file" 
            id="file-input" 
            className="hidden"
            onChange={handleFileChange} 
          />

          {/* Custom label for the file input */}
          <label 
            htmlFor="file-input" 
            className="tbutton"
          >
            Upload
          </label>

          {/* Display selected file name */}
          <span style={{ margin: '10px' }}>{fileName} uploaded successfully</span>

          <button type="submit" className="tbutton">Identify</button>
          {result && result.length > 0 && (
          <div>
            <p>Recognized food:</p>
            <ul>
            {result.map((label, index) => (
                <li key={index}>
                    <strong>Prediction {index + 1}:</strong> {label}
                </li>
            ))}
            </ul>
          </div>
          )}
        </div>
      </form>

    </div>
  );
}

export default UploadForm;
