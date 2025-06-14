class TTSApp {
    constructor() {
        this.currentConversionId = null;
        this.statusCheckInterval = null;
        this.voices = [];
        this.defaultVoice = null;
        this.initializeElements();
        this.attachEventListeners();
        this.loadVoices();
        this.loadHistory();
    }

    initializeElements() {
        this.titleInput = document.getElementById('title');
        this.voiceSelect = document.getElementById('voice-select');
        this.markdownTextarea = document.getElementById('markdown-text');
        this.convertBtn = document.getElementById('convert-btn');
        this.statusSection = document.getElementById('status-section');
        this.statusBadge = document.getElementById('status-badge');
        this.statusMessage = document.getElementById('status-message');
        this.progressBar = document.querySelector('.progress-fill');
        this.downloadSection = document.getElementById('download-section');
        this.downloadBtn = document.getElementById('download-btn');
        this.fileInfo = document.getElementById('file-info');
        this.historyList = document.getElementById('history-list');
        this.refreshHistoryBtn = document.getElementById('refresh-history');
    }

    attachEventListeners() {
        this.convertBtn.addEventListener('click', () => this.convertToSpeech());
        this.downloadBtn.addEventListener('click', () => this.downloadAudio());
        this.refreshHistoryBtn.addEventListener('click', () => this.loadHistory());
        
        // Auto-resize textarea
        this.markdownTextarea.addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = Math.max(200, e.target.scrollHeight) + 'px';
        });
    }

    async loadVoices() {
        try {
            const response = await fetch('/voices');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.voices = data.voices;
            this.defaultVoice = data.default_voice;
            this.populateVoiceSelect();
        } catch (error) {
            console.error('Failed to load voices:', error);
            this.voiceSelect.innerHTML = '<option value="">Failed to load voices</option>';
        }
    }

    populateVoiceSelect() {
        this.voiceSelect.innerHTML = '';
        
        // Group voices by language
        const voicesByLanguage = {};
        this.voices.forEach(voice => {
            if (!voicesByLanguage[voice.language]) {
                voicesByLanguage[voice.language] = [];
            }
            voicesByLanguage[voice.language].push(voice);
        });

        // Create optgroups for each language
        Object.keys(voicesByLanguage).sort().forEach(language => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = language;
            
            voicesByLanguage[language].forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.id;
                option.textContent = `${voice.speaker} (${voice.quality})`;
                if (voice.gender) {
                    option.textContent += ` - ${voice.gender}`;
                }
                if (voice.description) {
                    option.title = voice.description;
                }
                if (voice.id === this.defaultVoice) {
                    option.selected = true;
                }
                optgroup.appendChild(option);
            });
            
            this.voiceSelect.appendChild(optgroup);
        });
    }

    async convertToSpeech() {
        const markdownText = this.markdownTextarea.value.trim();
        const title = this.titleInput.value.trim();
        const voiceId = this.voiceSelect.value || null;

        if (!markdownText) {
            this.showError('Please enter some markdown text to convert.');
            return;
        }

        this.convertBtn.disabled = true;
        this.convertBtn.textContent = 'Converting...';
        
        // Get selected voice info for display
        const selectedVoice = this.voices.find(v => v.id === voiceId);
        const voiceName = selectedVoice ? `${selectedVoice.speaker} (${selectedVoice.language})` : 'default voice';
        
        this.showStatusSection('processing', `Converting with ${voiceName}...`);

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    markdown_text: markdownText,
                    title: title || null,
                    voice_id: voiceId
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            const result = await response.json();
            this.currentConversionId = result.conversion_id;
            
            if (result.status === 'completed') {
                this.handleConversionComplete();
            } else {
                this.startStatusChecking();
            }

        } catch (error) {
            console.error('Conversion error:', error);
            this.showError(`Conversion failed: ${error.message}`);
            this.resetConvertButton();
        }
    }

    startStatusChecking() {
        this.statusCheckInterval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${this.currentConversionId}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const status = await response.json();
                
                if (status.status === 'completed') {
                    this.handleConversionComplete();
                } else if (status.status === 'failed') {
                    throw new Error('Conversion failed on server');
                }
            } catch (error) {
                console.error('Status check error:', error);
                this.showError(`Failed to check conversion status: ${error.message}`);
                this.stopStatusChecking();
                this.resetConvertButton();
            }
        }, 1000);
    }

    stopStatusChecking() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }

    async handleConversionComplete() {
        this.stopStatusChecking();
        
        try {
            const response = await fetch(`/status/${this.currentConversionId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const status = await response.json();
            this.showStatusSection('completed', 'Conversion completed successfully!');
            this.showDownloadSection(status.file_size);
            this.resetConvertButton();
            this.loadHistory(); // Refresh history
        } catch (error) {
            console.error('Error getting file info:', error);
            this.showError(`Conversion completed but failed to get file info: ${error.message}`);
            this.resetConvertButton();
        }
    }

    showStatusSection(status, message) {
        this.statusSection.classList.remove('hidden');
        this.statusBadge.className = `status-badge ${status}`;
        this.statusBadge.textContent = status === 'processing' ? 'Processing...' : 
                                     status === 'completed' ? 'Completed' : 'Error';
        this.statusMessage.textContent = message;
        
        if (status === 'processing') {
            this.progressBar.style.width = '100%';
        } else {
            this.progressBar.style.width = '0%';
        }
    }

    showDownloadSection(fileSize) {
        this.downloadSection.classList.remove('hidden');
        this.fileInfo.textContent = `File size: ${this.formatFileSize(fileSize)}`;
    }

    async downloadAudio() {
        if (!this.currentConversionId) return;

        try {
            const response = await fetch(`/download/${this.currentConversionId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tts_${this.currentConversionId}.mp3`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download error:', error);
            this.showError(`Download failed: ${error.message}`);
        }
    }

    async loadHistory() {
        this.historyList.innerHTML = '<p class="loading">Loading history...</p>';

        try {
            const response = await fetch('/history?limit=50');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const history = await response.json();
            this.renderHistory(history.items);
        } catch (error) {
            console.error('History load error:', error);
            this.historyList.innerHTML = `<p class="error-message">Failed to load history: ${error.message}</p>`;
        }
    }

    renderHistory(items) {
        if (!items || items.length === 0) {
            this.historyList.innerHTML = '<p class="loading">No conversions yet.</p>';
            return;
        }

        this.historyList.innerHTML = items.map(item => `
            <div class="history-item">
                <div class="history-item-header">
                    <div>
                        <div class="history-item-title">${this.escapeHtml(item.title || 'Untitled')}</div>
                        <div class="history-item-date">${this.formatDate(item.created_at)}</div>
                    </div>
                    <div class="history-item-actions">
                        ${item.status === 'completed' ? 
                            `<button class="btn-success" onclick="app.downloadHistoryItem('${item.id}')">Download</button>` : 
                            '<span class="status-badge processing">Processing</span>'
                        }
                        <button class="btn-danger" onclick="app.deleteHistoryItem('${item.id}')">Delete</button>
                    </div>
                </div>
                <div class="history-item-preview">${this.escapeHtml(item.text_preview)}</div>
                ${item.file_size ? `<div class="history-item-info">Size: ${this.formatFileSize(item.file_size)}</div>` : ''}
            </div>
        `).join('');
    }

    async downloadHistoryItem(conversionId) {
        try {
            const response = await fetch(`/download/${conversionId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tts_${conversionId}.mp3`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download error:', error);
            this.showError(`Download failed: ${error.message}`);
        }
    }

    async deleteHistoryItem(conversionId) {
        if (!confirm('Are you sure you want to delete this conversion?')) {
            return;
        }

        try {
            const response = await fetch(`/history/${conversionId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            this.loadHistory(); // Refresh the list
        } catch (error) {
            console.error('Delete error:', error);
            this.showError(`Delete failed: ${error.message}`);
        }
    }

    resetConvertButton() {
        this.convertBtn.disabled = false;
        this.convertBtn.textContent = 'Convert to Speech';
    }

    showError(message) {
        // Remove any existing error messages
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        // Insert before the convert section
        const convertSection = document.querySelector('.convert-section');
        convertSection.parentNode.insertBefore(errorDiv, convertSection);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    formatFileSize(bytes) {
        if (!bytes) return 'Unknown';
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new TTSApp();
});