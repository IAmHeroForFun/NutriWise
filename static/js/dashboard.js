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

// Interactive Time of Day and Health Hub Switcher
function showTab(targetId) {
  const mealsContainer = document.getElementById('mealsContainer');
  const healthHub = document.getElementById('health-ingredients-hub');
  const activeFilterLabel = document.getElementById('activeFilterLabel');
  const resetFilterBtn = document.getElementById('resetFilterBtn');
  const rightPane = document.getElementById('splitRightPane');

  // Update active button state
  document.querySelectorAll('.meal-nav-item').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-target') === targetId);
  });

  // Reset any specific ingredient search or filter
  document.querySelectorAll('.food-card').forEach(card => card.style.display = 'flex');

  if (targetId === 'health-ingredients-hub') {
    mealsContainer.style.display = 'none';
    healthHub.style.display = 'block';
    activeFilterLabel.innerHTML = '🌿 <strong>Health & Ingredients Explorer</strong> &mdash; Select any ingredient to see therapeutic benefits and matching dishes';
    resetFilterBtn.style.display = 'inline-block';
    if (rightPane) rightPane.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }

  // Else showing meals
  healthHub.style.display = 'none';
  mealsContainer.style.display = 'block';

  const mealPanes = document.querySelectorAll('.meal-section-pane');

  if (targetId === 'all-meals-view') {
    mealPanes.forEach(pane => pane.style.display = 'block');
    activeFilterLabel.innerText = 'Displaying all dishes for all times of the day';
    resetFilterBtn.style.display = 'none';
    if (rightPane) rightPane.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    // Show specific meal time
    mealPanes.forEach(pane => {
      pane.style.display = (pane.id === targetId) ? 'block' : 'none';
    });
    const mealName = targetId.replace('meal-', '').toUpperCase();
    activeFilterLabel.innerHTML = `Showing dishes for <strong>${mealName}</strong>`;
    resetFilterBtn.style.display = 'inline-block';
    if (rightPane) rightPane.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// 1-Click filter dishes by clicked ingredient tag
function filterByIngredient(ingredientName) {
  const ingLower = ingredientName.toLowerCase().trim();
  const mealsContainer = document.getElementById('mealsContainer');
  const healthHub = document.getElementById('health-ingredients-hub');
  const activeFilterLabel = document.getElementById('activeFilterLabel');
  const resetFilterBtn = document.getElementById('resetFilterBtn');
  const rightPane = document.getElementById('splitRightPane');

  mealsContainer.style.display = 'block';
  healthHub.style.display = 'none';

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

  activeFilterLabel.innerHTML = `Filtered by ingredient: <strong style="color:var(--primary);">${ingredientName}</strong> (${matchCount} dish${matchCount === 1 ? '' : 'es'})`;
  resetFilterBtn.style.display = 'inline-block';
  if (rightPane) rightPane.scrollTo({ top: 0, behavior: 'smooth' });
}

// Search bar inside the Health & Ingredients Hub
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

// Reinforcement feedback loop (+5 for like, +8 for cooked)
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


