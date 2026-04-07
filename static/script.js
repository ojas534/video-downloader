const urlInput = document.getElementById('urlInput');
const fetchBtn = document.getElementById('fetchBtn');
const loading = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const videoInfo = document.getElementById('videoInfo');
const thumbnail = document.getElementById('thumbnail');
const title = document.getElementById('title');
const formatSelect = document.getElementById('formatSelect');
const downloadBtn = document.getElementById('downloadBtn');
const downloadLoading = document.getElementById('downloadLoading');

// Variable to store current title for download naming
let currentTitle = "video";

fetchBtn.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    if (!url) return alert('Please enter a URL');

    // Reset UI
    errorDiv.classList.add('hidden');
    videoInfo.classList.add('hidden');
    loading.classList.remove('hidden');
    fetchBtn.disabled = true;

    try {
        const response = await fetch('/api/info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch video info');
        }

        // Populate UI
        currentTitle = data.title;
        title.textContent = data.title;
        thumbnail.src = data.thumbnail;
        
        // Populate formats
        formatSelect.innerHTML = '';
        data.formats.forEach(f => {
            const option = document.createElement('option');
            option.value = f.id;
            option.textContent = f.label;
            formatSelect.appendChild(option);
        });

        // Show info
        videoInfo.classList.remove('hidden');

    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
        fetchBtn.disabled = false;
    }
});

downloadBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    const formatId = formatSelect.value;
    
    if (!url || !formatId) return;

    // Show download loading text, disable button
    downloadBtn.disabled = true;
    downloadLoading.classList.remove('hidden');

    // To handle downloads nicely without blocking JS, we redirect the browser.
    // The browser will start downloading the file while staying on the page.
    const downloadUrl = `/api/download?url=${encodeURIComponent(url)}&format_id=${formatId}&title=${encodeURIComponent(currentTitle)}`;
    
    window.location.href = downloadUrl;

    // Re-enable button after a short delay so user can try again if they want
    setTimeout(() => {
        downloadBtn.disabled = false;
        downloadLoading.classList.add('hidden');
    }, 5000);
});