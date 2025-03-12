let documentText = '';

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const questionForm = document.getElementById('questionForm');
    const uploadError = document.getElementById('uploadError');
    const questionSection = document.getElementById('questionSection');
    const answerSection = document.getElementById('answerSection');

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('documentFile');
        const file = fileInput.files[0];
        if (!file) {
            showError('Please select a file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            showLoading(uploadForm);
            hideError();
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Error processing file');
            }

            documentText = data.text;
            questionSection.classList.remove('d-none');
            
        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading(uploadForm);
        }
    });

    questionForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const question = document.getElementById('question').value.trim();
        if (!question) {
            showError('Please enter a question');
            return;
        }

        try {
            showLoading(questionForm);
            hideError();

            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    context: documentText
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Error processing question');
            }

            displayAnswer(data.answer);
            
        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading(questionForm);
        }
    });
});

function showError(message) {
    const errorDiv = document.getElementById('uploadError');
    errorDiv.textContent = message;
    errorDiv.classList.remove('d-none');
}

function hideError() {
    const errorDiv = document.getElementById('uploadError');
    errorDiv.classList.add('d-none');
}

function showLoading(form) {
    const spinner = form.querySelector('.spinner-border');
    const button = form.querySelector('button[type="submit"]');
    spinner.classList.remove('d-none');
    button.disabled = true;
}

function hideLoading(form) {
    const spinner = form.querySelector('.spinner-border');
    const button = form.querySelector('button[type="submit"]');
    spinner.classList.add('d-none');
    button.disabled = false;
}

function displayAnswer(answer) {
    const answerSection = document.getElementById('answerSection');
    const answerText = document.getElementById('answer');
    answerText.textContent = answer;
    answerSection.classList.remove('d-none');
}
