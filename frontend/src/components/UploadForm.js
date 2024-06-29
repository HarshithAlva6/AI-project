import React, { useState } from 'react';
import { uploadImage } from '../api';

function UploadForm() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (file) {
      const response = await uploadImage(file);
      setResult(response.result);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
      {result && <p>Recognized food: {result}</p>}
    </div>
  );
}

export default UploadForm;
