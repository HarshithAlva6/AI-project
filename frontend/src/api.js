export const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
  
    const response = await fetch('http://localhost:5000/recognize', {
      method: 'POST',
      body: formData,
    });
    console.log(response);
    if (!response.ok) {
      throw new Error('Failed to upload image');
    }
  
    return await response.json();
  };
  