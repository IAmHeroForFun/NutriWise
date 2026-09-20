// ==============================================================================
// NutriWise — Interactive Dashboard & Health Charts Controller
// ==============================================================================

document.addEventListener('DOMContentLoaded', () => {
  initMacroChart();
  initThermalMeter();
});

// 1. Initialize Chart.js Macronutrient Donut Chart
function initMacroChart() {
  const canvas = document.getElementById('macroChart');
  if (!canvas || typeof Chart === 'undefined') return;

  const ctx = canvas.getContext('2d');
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Complex Carbs', 'Plant Protein', 'Healthy Lipids', 'Dietary Fiber'],
      datasets: [{
        data: [48, 24, 18, 10],
        backgroundColor: [
          '#10b981', // Emerald
          '#f97316', // Coral
          '#f59e0b', // Amber
          '#6366f1'  // Indigo
        ],
        borderWidth: 2,
        borderColor: '#ffffff',
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(10, 47, 36, 0.95)',
          titleFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: 'bold' },
          bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: function(context) {
              return ` ${context.label}: ${context.raw}%`;
            }
          }
        }
      },
      animation: {
        animateScale: true,
        animateRotate: true,
        duration: 1000
      }
    }
  });
}

// 2. Position Thermal Gauge Thumb based on Outdoor Climate
function initThermalMeter() {
  const thumb = document.getElementById('thermalThumb');
  if (!thumb) return;

  // Read temperature from DOM or default to 28°C
  let temp = 28;
  const tempElem = document.querySelector('.temp-badge');
  if (tempElem) {
    const parsed = parseFloat(tempElem.innerText);
    if (!isNaN(parsed)) temp = parsed;
  }

  // Map 15°C (Cooling needed / left) -> 42°C (Extreme heat / right)
  let percent = ((temp - 15) / (40 - 15)) * 100;
  percent = Math.max(10, Math.min(90, percent));
  thumb.style.left = `${percent}%`;
}

// 3. Citation Modal Controller
function showCitation(title, page, chapter, author, excerpt) {
  document.getElementById('modalTitle').innerText = title || 'Authoritative Source Reference';
  let meta = [];
  if (author) meta.push(`Author: ${author}`);
  if (chapter) meta.push(`Chapter: ${chapter}`);
  if (page) meta.push(`Page: ${page}`);
  document.getElementById('modalMeta').innerText = meta.join(' | ');
  document.getElementById('modalText').innerText = excerpt || 'Reference excerpt verified in published knowledge base.';
  
  const modal = document.getElementById('citationModal');
  modal.style.display = 'flex';
}

function closeCitation() {
  const modal = document.getElementById('citationModal');
  modal.style.display = 'none';
}

// 4. "Can't Make" Ingredient Alternative Handler
async function markCantMake(foodId, foodName) {
  if (!confirm(`Can't make ${foodName}? We will find alternative dishes sharing similar ingredients!`)) {
    return;
  }

  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

  try {
    const resp = await fetch(`/food/${foodId}/cant-make/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json'
      }
    });
    if (resp.ok) {
      window.location.href = `/food/${foodId}/alternatives/`;
    }
  } catch (err) {
    window.location.href = `/food/${foodId}/alternatives/`;
  }
}

function scrollToElement(elem) {
  if (!elem) return;
  const headerOffset = window.innerWidth <= 860 ? 130 : 85;
  const elementPosition = elem.getBoundingClientRect().top;
  const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

  window.scrollTo({
    top: Math.max(0, offsetPosition),
    behavior: 'smooth'
  });
}

// 5. Interactive Time of Day and Health Hub Switcher
function showTab(targetId) {
  const mealsContainer = document.getElementById('mealsContainer');
  const healthHub = document.getElementById('health-ingredients-hub');
  const activeFilterLabel = document.getElementById('activeFilterLabel');
  const resetFilterBtn = document.getElementById('resetFilterBtn');

  // Update active button state in sidebar and mobile tabs
  document.querySelectorAll('.meal-nav-item').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-target') === targetId);
  });

  // Reset any specific ingredient search or filter
  document.querySelectorAll('.food-card').forEach(card => card.style.display = 'flex');

  if (targetId === 'health-ingredients-hub') {
    if (mealsContainer) mealsContainer.style.display = 'none';
    if (healthHub) {
      healthHub.style.display = 'block';
      scrollToElement(healthHub);
    }
    if (activeFilterLabel) {
      activeFilterLabel.innerHTML = '🌿 <strong>Health & Ingredients Explorer</strong> &mdash; Select any ingredient to see therapeutic benefits and matching dishes';
    }
    if (resetFilterBtn) resetFilterBtn.style.display = 'inline-block';
    return;
  }

  // Else showing meals
  if (healthHub) healthHub.style.display = 'none';
  if (mealsContainer) mealsContainer.style.display = 'block';

  const mealPanes = document.querySelectorAll('.meal-section-pane');

  if (targetId === 'all-meals-view') {
    mealPanes.forEach(pane => pane.style.display = 'block');
    if (activeFilterLabel) activeFilterLabel.innerText = 'Displaying all curated culinary dishes for today';
    if (resetFilterBtn) resetFilterBtn.style.display = 'none';
    const firstMeal = document.querySelector('.meal-section-pane');
    if (firstMeal) scrollToElement(firstMeal);
  } else {
    // Show specific meal time
    mealPanes.forEach(pane => {
      pane.style.display = (pane.id === targetId) ? 'block' : 'none';
    });
    const mealName = targetId.replace('meal-', '').toUpperCase();
    if (activeFilterLabel) activeFilterLabel.innerHTML = `Showing dishes for <strong>${mealName}</strong>`;
    if (resetFilterBtn) resetFilterBtn.style.display = 'inline-block';

    const targetPane = document.getElementById(targetId);
    if (targetPane) {
      scrollToElement(targetPane);
    }
  }
}

// 6. Filter dishes by clicked ingredient tag
function filterByIngredient(ingredientName) {
  const ingLower = ingredientName.toLowerCase().trim();
  const mealsContainer = document.getElementById('mealsContainer');
  const healthHub = document.getElementById('health-ingredients-hub');
  const activeFilterLabel = document.getElementById('activeFilterLabel');
  const resetFilterBtn = document.getElementById('resetFilterBtn');

  if (mealsContainer) mealsContainer.style.display = 'block';
  if (healthHub) healthHub.style.display = 'none';

  let matchCount = 0;
  document.querySelectorAll('.meal-section-pane').forEach(pane => {
    pane.style.display = 'block';
    let paneMatches = 0;
    pane.querySelectorAll('.food-card').forEach(card => {
      const cardIngs = (card.getAttribute('data-ingredients') || '').toLowerCase();
      if (cardIngs.includes(ingLower) || card.innerText.toLowerCase().includes(ingLower)) {
        card.style.display = 'flex';
        paneMatches++;
        matchCount++;
      } else {
        card.style.display = 'none';
      }
    });
  });

  if (activeFilterLabel) {
    activeFilterLabel.innerHTML = `Filtered by ingredient: <strong style="color:var(--primary);">${ingredientName}</strong> (${matchCount} dish${matchCount === 1 ? '' : 'es'})`;
    scrollToElement(activeFilterLabel);
  }
  if (resetFilterBtn) resetFilterBtn.style.display = 'inline-block';
}

// 7. Search bar inside the Health & Ingredients Hub
function searchIngredients() {
  const query = document.getElementById('ingredientSearchInput').value.toLowerCase().trim();
  document.querySelectorAll('.ingredient-card').forEach(card => {
    const text = card.innerText.toLowerCase();
    card.style.display = (query === '' || text.includes(query)) ? 'flex' : 'none';
  });
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeCitation();
});

// 8. Reinforcement feedback loop (+5 for like, +8 for cooked)
async function sendFeedback(foodId, action, btnElem) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';
  const formData = new FormData();
  formData.append('action', action);

  try {
    const resp = await fetch(`/food/${foodId}/feedback/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken
      },
      body: formData
    });
    const data = await resp.json();
    if (data.status === 'ok') {
      if (action === 'like') {
        btnElem.classList.add('active-like');
        btnElem.innerHTML = '✓ Liked';
      } else if (action === 'cooked') {
        btnElem.classList.add('active-cooked');
        btnElem.innerHTML = '✓ Cooked';
      }
    }
  } catch (err) {
    console.error('Feedback error:', err);
  }
}
