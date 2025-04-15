<script>
  import { createEventDispatcher } from 'svelte';
  import { fade } from 'svelte/transition';
  
  const dispatch = createEventDispatcher();
  
  // Track drag state
  let isDragging = false;
  
  // Handle file selection
  function handleFileSelect(event) {
    const files = event.target.files;
    if (files && files.length > 0) {
      processFiles(files);
    }
  }
  
  // Handle file drop
  function handleDrop(event) {
    event.preventDefault();
    isDragging = false;
    
    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      processFiles(files);
    }
  }
  
  // Process the uploaded files
  function processFiles(files) {
    console.log('Processing files:', files);
    // Here you would typically process the files and send them to your backend
    
    // For now, we'll just dispatch an event with the files
    dispatch('import', { files });
  }
  
  // Handle drag events
  function handleDragOver(event) {
    event.preventDefault();
    isDragging = true;
  }
  
  function handleDragLeave() {
    isDragging = false;
  }
  
  // Close modal
  function closeModal() {
    dispatch('close');
  }
  
  // Trigger file input click
  function triggerFileInput() {
    document.getElementById('importFileInput').click();
  }
</script>

<div class="modal-backdrop" on:click={closeModal} transition:fade={{ duration: 200 }}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <h2>Import Project</h2>
      <button 
        class="close-btn" 
        on:click={closeModal}
        title="Close this dialog"
      >
        ✕
      </button>
    </div>
    
    <div class="modal-body">
      <p class="description">Bring existing projects into TRACE.</p>
      
      <div 
        class="upload-area {isDragging ? 'dragging' : ''}"
        on:dragover={handleDragOver}
        on:dragleave={handleDragLeave}
        on:drop={handleDrop}
        on:click={triggerFileInput}
        title="Upload your project files here"
      >
        <div class="upload-content">
          <div class="upload-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 4V16M12 4L8 8M12 4L16 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M20 16V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18V16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <p class="upload-text">Drop a file or click to browse</p>
        </div>
        
        <input 
          type="file" 
          id="importFileInput" 
          on:change={handleFileSelect} 
          style="display: none;"
        />
      </div>
    </div>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    background-color: white;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
  
  :global(body.dark-mode) .modal-content {
    background-color: #1e1e1e;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #eee;
  }
  
  :global(body.dark-mode) .modal-header {
    border-bottom-color: #333;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 20px;
    color: #333;
  }
  
  :global(body.dark-mode) .modal-header h2 {
    color: #fff;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #777;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }
  
  :global(body.dark-mode) .close-btn {
    color: #aaa;
  }
  
  .close-btn:hover {
    background-color: #f0f0f0;
    color: #333;
  }
  
  :global(body.dark-mode) .close-btn:hover {
    background-color: #333;
    color: #fff;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .description {
    margin: 0 0 20px 0;
    color: #555;
    font-size: 16px;
  }
  
  :global(body.dark-mode) .description {
    color: #b0b0b0;
  }
  
  .upload-area {
    border: 2px dashed #ccc;
    border-radius: 8px;
    padding: 40px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-bottom: 20px;
  }
  
  :global(body.dark-mode) .upload-area {
    border-color: #444;
  }
  
  .upload-area:hover {
    border-color: #4a56e2;
    background-color: rgba(74, 86, 226, 0.05);
  }
  
  :global(body.dark-mode) .upload-area:hover {
    background-color: rgba(74, 86, 226, 0.1);
  }
  
  .upload-area.dragging {
    border-color: #4a56e2;
    background-color: rgba(74, 86, 226, 0.1);
  }
  
  :global(body.dark-mode) .upload-area.dragging {
    background-color: rgba(74, 86, 226, 0.15);
  }
  
  .upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  .upload-icon {
    margin-bottom: 15px;
    color: #777;
  }
  
  :global(body.dark-mode) .upload-icon {
    color: #aaa;
  }
  
  .upload-area:hover .upload-icon,
  .upload-area.dragging .upload-icon {
    color: #4a56e2;
  }
  
  .upload-text {
    margin: 0;
    color: #555;
    font-size: 14px;
  }
  
  :global(body.dark-mode) .upload-text {
    color: #b0b0b0;
  }
  
  .upload-area:hover .upload-text,
  .upload-area.dragging .upload-text {
    color: #4a56e2;
  }
</style>