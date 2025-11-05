// API endpoint
const API_URL = 'http://127.0.0.1:5000/api/recommend';

// Validation rules
const VALIDATION_RULES = {
    age: { min: 1, max: 100, required: true },
    bmi: { min: 10, max: 60, required: true },
    bps: { min: 80, max: 200, required: true },
    bsl: { min: 50, max: 400, required: true },
    steps: { min: 0, max: 30000, required: true },
    exercise: { min: 0, max: 7, required: true }
};

// DOM elements
const dietForm = document.getElementById('dietForm');
const submitBtn = document.getElementById('submitBtn');
const spinner = document.getElementById('spinner');
const btnText = submitBtn.querySelector('.btn-text');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');
const resultsTableBody = document.getElementById('resultsTableBody');
const profileName = document.getElementById('profileName');
const recommendationType = document.getElementById('recommendationType');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const apiErrorAlert = document.getElementById('apiErrorAlert');
const apiErrorText = document.getElementById('apiErrorText');
const summaryProfileName = document.getElementById('summaryProfileName');
const summaryRecommendationType = document.getElementById('summaryRecommendationType');
const downloadJsonBtn = document.getElementById('downloadJsonBtn');

// Store last response for download
let lastResponse = null;

// Validation functions
function validateField(fieldId, value, rules) {
    const field = document.getElementById(fieldId);
    const errorElement = document.getElementById(`${fieldId}-error`);
    
    // Clear previous error
    clearFieldError(fieldId);
    
    // Check if required and empty
    if (rules.required && (value === '' || value === null || value === undefined)) {
        showFieldError(fieldId, 'This field is required');
        return false;
    }
    
    // Skip validation if empty and not required
    if (!rules.required && (value === '' || value === null || value === undefined)) {
        return true;
    }
    
    // Convert to number for numeric validation
    const numValue = Number(value);
    
    // Check if it's a valid number
    if (isNaN(numValue)) {
        showFieldError(fieldId, 'Please enter a valid number');
        return false;
    }
    
    // Check min value
    if (rules.min !== undefined && numValue < rules.min) {
        showFieldError(fieldId, `Value must be at least ${rules.min}`);
        return false;
    }
    
    // Check max value
    if (rules.max !== undefined && numValue > rules.max) {
        showFieldError(fieldId, `Value must be at most ${rules.max}`);
        return false;
    }
    
    return true;
}

function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorElement = document.getElementById(`${fieldId}-error`);
    
    if (field && errorElement) {
        field.classList.add('error');
        errorElement.textContent = message;
    }
}

function clearFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    const errorElement = document.getElementById(`${fieldId}-error`);
    
    if (field && errorElement) {
        field.classList.remove('error');
        errorElement.textContent = '';
    }
}

// Legacy validation functions kept for backward compatibility but not used
// New validation uses validateRanges() and form.checkValidity()

// Set error function - uses existing error-message spans
function setError(id, msg) {
    const el = document.getElementById(`${id}-error`);
    if (el) {
        el.textContent = msg || "";
        el.style.display = msg ? "block" : "none";
    }
}

// Validate ranges function
function validateRanges() {
    const v = (id) => document.getElementById(id).value.trim();
    let ok = true;

    const rules = [
        { id: 'age', min: 1, max: 100, label: 'Age' },
        { id: 'bmi', min: 10, max: 60, label: 'BMI' },
        { id: 'bps', min: 80, max: 200, label: 'Blood Pressure (Systolic)' },
        { id: 'bsl', min: 50, max: 400, label: 'Blood Sugar Level' },
        { id: 'steps', min: 0, max: 30000, label: 'Daily Steps' },
        { id: 'exercise', min: 0, max: 7, label: 'Exercise Frequency' }
    ];

    for (const r of rules) {
        const val = Number(v(r.id));
        const missing = v(r.id) === "";
        const outOfRange = isNaN(val) || val < r.min || val > r.max;
        if (missing) {
            setError(r.id, `${r.label} is required.`);
            ok = false;
        } else if (outOfRange) {
            setError(r.id, `${r.label} must be ${r.min}–${r.max}.`);
            ok = false;
        } else {
            setError(r.id, "");
        }
    }

    // Validate select fields
    const selects = [
        { id: 'chronic', label: 'Chronic Disease' },
        { id: 'alcohol', label: 'Alcohol Consumption' },
        { id: 'smoking', label: 'Smoking Habit' },
        { id: 'diet', label: 'Dietary Habits' }
    ];

    for (const s of selects) {
        const value = v(s.id);
        if (!value || value === "") {
            setError(s.id, `${s.label} is required.`);
            ok = false;
        } else {
            setError(s.id, "");
        }
    }

    return ok;
}

// Live cleanup while typing
document.querySelectorAll('#dietForm input, #dietForm select').forEach(el => {
    el.addEventListener('input', () => {
        setError(el.id, "");
        // Also clear old error messages
        clearFieldError(el.id);
    });
});

// Handle form submission
dietForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Hide previous results and errors
    resultsSection.style.display = 'none';
    errorMessage.style.display = 'none';
    apiErrorAlert.style.display = 'none';
    
    // Add was-validated class to trigger CSS validation styles
    dietForm.classList.add('was-validated');
    
    // Validate form before submission
    if (!dietForm.checkValidity() || !validateRanges()) {
        // Scroll to first error
        const firstInvalid = dietForm.querySelector('input:invalid, select:invalid');
        if (firstInvalid) {
            firstInvalid.focus();
            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
    }
    
    // Build payload with exact backend keys
    const payload = {
        Age: Number(document.querySelector('#age').value),
        BMI: Number(document.querySelector('#bmi').value),
        Chronic_Disease: document.querySelector('#chronic').value,
        Blood_Pressure_Systolic: Number(document.querySelector('#bps').value),
        Blood_Sugar_Level: Number(document.querySelector('#bsl').value),
        Daily_Steps: Number(document.querySelector('#steps').value),
        Exercise_Frequency: Number(document.querySelector('#exercise').value),
        Alcohol_Consumption: document.querySelector('#alcohol').value,
        Smoking_Habit: document.querySelector('#smoking').value,
        Dietary_Habits: document.querySelector('#diet').value,
    };
    
    // Show loading state
    setLoadingState(true);
    
    try {
        // Send POST request to API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        // Check if response is ok
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
            const errorMessage = errorData.error || `Server error (${response.status})`;
            
            // Show API error at top for 400/500 errors
            if (response.status === 400 || response.status === 500) {
                showApiError(errorMessage);
            } else {
                displayError(errorMessage);
            }
            // Don't return here - let finally block run to re-enable button
        } else {
            // Parse response
            const result = await response.json();
            
            // Display results
            displayResults(result);
        }
        
    } catch (error) {
        console.error('Error:', error);
        // Network errors or other issues
        showApiError(error.message || 'An error occurred while fetching recommendations. Please check your connection and try again.');
    } finally {
        // Hide loading state
        setLoadingState(false);
    }
});

// Set loading state
function setLoadingState(isLoading) {
    if (isLoading) {
        submitBtn.disabled = true;
        btnText.textContent = 'Processing...';
        spinner.style.display = 'inline-block';
        loadingSpinner.style.display = 'block';
    } else {
        submitBtn.disabled = false;
        btnText.textContent = 'Get Recommendations';
        spinner.style.display = 'none';
        loadingSpinner.style.display = 'none';
    }
}

// Display results
function displayResults(result) {
    // Store last response for download
    lastResponse = result;
    
    // Set profile name and recommendation type
    const profileNameValue = result.profile_name || 'Profile';
    const recommendationTypeValue = result.recommendation_type || '';
    
    profileName.textContent = profileNameValue;
    recommendationType.textContent = recommendationTypeValue;
    
    // Set summary header values
    summaryProfileName.textContent = profileNameValue;
    summaryRecommendationType.textContent = recommendationTypeValue;
    
    // Clear previous table rows
    resultsTableBody.innerHTML = '';
    
    // Check if there are recommended foods
    if (!result.recommended_foods || result.recommended_foods.length === 0) {
        resultsTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">No recommendations available.</td></tr>';
    } else {
        // Add each food to the table
        result.recommended_foods.forEach(food => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td><strong>${escapeHtml(food.Food || 'N/A')}</strong></td>
                <td>${escapeHtml(food.Category || 'N/A')}</td>
                <td>${formatNumber(food.Protein)}</td>
                <td>${formatNumber(food.Fat)}</td>
                <td>${formatNumber(food.Carbs)}</td>
                <td><strong>${formatNumber(food.Calories)}</strong></td>
            `;
            
            resultsTableBody.appendChild(row);
        });
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Download JSON function
function downloadJson() {
    if (!lastResponse) {
        alert('No results to download. Please generate recommendations first.');
        return;
    }
    
    // Create JSON string with proper formatting
    const jsonString = JSON.stringify(lastResponse, null, 2);
    
    // Create blob and download
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'results.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Add event listener for download button
downloadJsonBtn.addEventListener('click', downloadJson);

// Display error message (for general errors)
function displayError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'block';
    
    // Scroll to error
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show API error at top (for 400/500 errors)
function showApiError(message) {
    apiErrorText.textContent = message;
    apiErrorAlert.style.display = 'block';
    
    // Scroll to top to show error
    apiErrorAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Format number (handle NaN and null)
function formatNumber(value) {
    if (value === null || value === undefined || isNaN(value)) {
        return '0';
    }
    return Number(value).toFixed(1);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

