let currentStep = 1;
const totalSteps = 7;

const stepTitles = [
  "Basic Stats",
  "Diet Type",
  "Health Conditions & Goals",
  "Allergies",
  "Dislikes",
  "Preferences & Likes",
  "Live Location"
];

function updateWizard() {
  document.querySelectorAll('.step-pane').forEach((pane, idx) => {
    pane.classList.toggle('active', idx + 1 === currentStep);
  });

  const progressPercent = (currentStep / totalSteps) * 100;
  document.getElementById('progressFill').style.width = `${progressPercent}%`;
  document.getElementById('stepIndicator').innerText = `Step ${currentStep} of ${totalSteps} — ${stepTitles[currentStep - 1]}`;

  document.getElementById('prevBtn').style.visibility = currentStep === 1 ? 'hidden' : 'visible';
  if (currentStep === totalSteps) {
    document.getElementById('nextBtn').style.display = 'none';
    document.getElementById('submitBtn').style.display = 'inline-flex';
  } else {
    document.getElementById('nextBtn').style.display = 'inline-flex';
    document.getElementById('submitBtn').style.display = 'none';
  }
}

function nextStep() {
  if (currentStep < totalSteps) {
    currentStep++;
    updateWizard();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function prevStep() {
  if (currentStep > 1) {
    currentStep--;
    updateWizard();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// Geolocation Detection
function detectLocation() {
  const statusElem = document.getElementById('geoStatus');
  statusElem.style.display = 'block';
  statusElem.className = 'alert alert-info';
  statusElem.innerText = 'Detecting current coordinates...';

  if (!navigator.geolocation) {
    statusElem.className = 'alert alert-error';
    statusElem.innerText = 'Geolocation is not supported by your browser.';
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      document.getElementById('latInput').value = lat;
      document.getElementById('lonInput').value = lon;

      statusElem.innerText = 'Resolving city name...';
      try {
        const resp = await fetch(`/api/reverse-geocode/?lat=${lat}&lon=${lon}`);
        const data = await resp.json();
        if (data.city) {
          document.getElementById('cityInput').value = data.city;
          if (data.state) document.getElementById('stateInput').value = data.state;
          statusElem.className = 'alert alert-success';
          statusElem.innerText = `✓ Detected: ${data.city}${data.state ? ', ' + data.state : ''}`;
        } else {
          statusElem.className = 'alert alert-info';
          statusElem.innerText = `✓ Coordinates saved (${lat.toFixed(2)}, ${lon.toFixed(2)}). You may specify city name manually.`;
        }
      } catch (err) {
        statusElem.className = 'alert alert-info';
        statusElem.innerText = `✓ Coordinates recorded.`;
      }
    },
    (err) => {
      statusElem.className = 'alert alert-error';
      statusElem.innerText = 'Could not access location automatically. Please enter your city manually.';
    },
    { timeout: 8000 }
  );
}

document.addEventListener('DOMContentLoaded', () => {
  updateWizard();

  const form = document.getElementById('onboardingForm');
  if (form) {
    form.addEventListener('submit', () => {
      const overlay = document.getElementById('aiLoadingOverlay');
      const submitBtn = document.getElementById('submitBtn');
      if (overlay) {
        overlay.style.display = 'flex';
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '🤖 Synthesizing AI Plan...';
      }

      const steps = [
        '🔒 Cross-checking allergens & contraindications...',
        '🌦️ Calibrating metabolic thermal equilibrium for local climate...',
        '📚 Extracting verified dishes from medical nutrition literature...',
        '✨ Google Gemini AI curating synergistic daily regimen...'
      ];
      let stepIdx = 0;
      const stepText = document.getElementById('aiStepText');
      if (stepText) {
        setInterval(() => {
          stepIdx = (stepIdx + 1) % steps.length;
          stepText.innerText = steps[stepIdx];
        }, 1800);
      }
    });
  }
});
